const LMS_LOGINS = {
  "admin@lms.local": "admin123",
  "instructor@lms.local": "teach123",
};

function opsPasswordOk(email, pw, env) {
  if (!pw) return false;
  const em = String(email || "").trim().toLowerCase();
  if (em && LMS_LOGINS[em] === pw) return true;
  if (!em && Object.values(LMS_LOGINS).includes(pw)) return true;
  if (env.OPS_PASSWORD && pw === env.OPS_PASSWORD) return true;
  const extra = String(env.OPS_USERS || "");
  if (em && extra) {
    return extra.split(/[\n,;]+/).some((row) => {
      const [e, p] = row.split(":").map((x) => String(x || "").trim());
      return e && p && e.toLowerCase() === em && p === pw;
    });
  }
  return false;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!env.DB) return new Response("D1 binding DB is missing", { status: 500 });
    const cookie = request.headers.get("Cookie") || "";
    const authed = cookie.includes("ops=1");
    if (url.pathname === "/login" && request.method === "POST") {
      const form = await request.formData();
      const email = String(form.get("email") || "").trim().toLowerCase();
      const pw = String(form.get("password") || "");
      if (opsPasswordOk(email, pw, env)) {
        return new Response(null, {
          status: 302,
          headers: {
            Location: "/",
            "Set-Cookie": "ops=1; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=604800",
          },
        });
      }
      return new Response(loginPage("Wrong email or password"), { headers: { "content-type": "text/html;charset=utf-8" } });
    }
    if (url.pathname === "/logout") {
      return new Response(null, {
        status: 302,
        headers: { Location: "/", "Set-Cookie": "ops=0; Path=/; Max-Age=0" },
      });
    }
    if (!authed) {
      return new Response(loginPage(""), { headers: { "content-type": "text/html;charset=utf-8" } });
    }
    await initSchema(env);
    await seedIfEmpty(env);
    await patchShifts(env);
    await syncStaff(env);
    if (url.pathname === "/api/away" && request.method === "POST") {
      const b = await request.json();
      const staff_id = Number(b.staff_id);
      let kind = String(b.kind || "leave").trim();
      const custom = String(b.custom || "").trim();
      const klow = kind.toLowerCase();
      if (klow === "duty") kind = "duty";
      else if (klow === "leave") kind = "leave";
      else if (klow === "other" || custom) kind = custom || "other";
      else kind = kind.slice(0, 40) || "other";
      const start = String(b.start || "");
      const end = String(b.end || b.start || "");
      const note = String(b.note || "");
      if (!staff_id || !start) return json({ ok: false }, 400);
      const editId = Number(b.id || 0);
      if (editId) {
        await env.DB.prepare("UPDATE away SET staff_id=?, kind=?, start=?, end=?, note=? WHERE id=?").bind(staff_id, kind, start, end, note, editId).run();
      } else {
        await env.DB.prepare("INSERT INTO away(staff_id,kind,start,end,note) VALUES(?,?,?,?,?)").bind(staff_id, kind, start, end, note).run();
      }
      const hits = (await env.DB.prepare(
        "SELECT day, class_id, room_id, shift FROM assign WHERE staff_id=? AND day>=? AND day<=?"
      ).bind(staff_id, start, end).all()).results || [];
      const staff = await env.DB.prepare("SELECT display, last_name, first_name FROM staff WHERE id=?").bind(staff_id).first();
      const classes = (await env.DB.prepare("SELECT id, primary_name, room_label, shift FROM classes").all()).results || [];
      const needle = ((staff && (staff.last_name || staff.display)) || "").toLowerCase();
      classes.forEach(c => {
        const raw = (c.primary_name || "").toLowerCase();
        if (needle && raw.includes(needle.split(",")[0].trim())) {
          hits.push({ day: start, class_id: c.id, room_id: 0, shift: c.shift || "A", listed: true });
        }
      });
      return json({ ok: true, hits });
    }
    if (url.pathname === "/api/away" && request.method === "DELETE") {
      const id = Number(url.searchParams.get("id") || 0);
      if (id) await env.DB.prepare("DELETE FROM away WHERE id=?").bind(id).run();
      return json({ ok: true });
    }
    if (url.pathname === "/api/team" && request.method === "POST") {
      const name = String((await request.json()).name || "").trim();
      if (!name) return json({ ok: false }, 400);
      await env.DB.prepare("INSERT OR IGNORE INTO teams(name) VALUES(?)").bind(name).run();
      return json({ ok: true, name });
    }
    if (url.pathname === "/api/team" && request.method === "DELETE") {
      const name = String(url.searchParams.get("name") || "").trim();
      if (!name) return json({ ok: false }, 400);
      await env.DB.prepare("DELETE FROM teams WHERE name=?").bind(name).run();
      await env.DB.prepare("UPDATE staff SET team='' WHERE team=?").bind(name).run();
      return json({ ok: true });
    }
    if (url.pathname === "/api/staff" && request.method === "POST") {
      const b = await request.json();
      const id = Number(b.id);
      const team = String(b.team || "").trim();
      if (!id) return json({ ok: false }, 400);
      await env.DB.prepare("UPDATE staff SET team=? WHERE id=?").bind(team, id).run();
      return json({ ok: true });
    }
    if (url.pathname === "/api/room" && request.method === "POST") {
      const name = String((await request.json()).name || "").trim();
      if (!name) return json({ ok: false }, 400);
      const exists = await env.DB.prepare("SELECT id FROM rooms WHERE name=?").bind(name).first();
      if (exists) return json({ ok: true, id: exists.id, name });
      const row = await env.DB.prepare("INSERT INTO rooms(name) VALUES(?) RETURNING id").bind(name).run();
      const id = row.meta && row.meta.last_row_id;
      return json({ ok: true, id, name });
    }
    if (url.pathname === "/api/class" && request.method === "POST") {
      const b = await request.json();
      const id = Number(b.id);
      if (!id) return json({ ok: false }, 400);
      const room = String(b.room_label || "").trim();
      const shift = String(b.shift || "A").toUpperCase().slice(0,1);
      const primary = String(b.primary_name || "").trim();
      const course = String(b.course || "").trim();
      const class_num = String(b.class_num || "").trim();
      const n = Number(b.n || 0);
      await env.DB.prepare(
        "UPDATE classes SET room_label=?, shift=?, primary_name=?, course=?, class_num=?, n=? WHERE id=?"
      ).bind(room, shift, primary, course, class_num, n, id).run();
      if (room) {
        const exists = await env.DB.prepare("SELECT id FROM rooms WHERE name=?").bind(room).first();
        if (!exists) await env.DB.prepare("INSERT INTO rooms(name) VALUES(?)").bind(room).run();
      }
      return json({ ok: true });
    }
    if (url.pathname === "/api/assign" && request.method === "POST") {
      const b = await request.json();
      const day = String(b.day || "");
      const room_id = Number(b.room_id);
      const staff_id = Number(b.staff_id);
      const on = !!b.on;
      if (!day || !staff_id) return json({ ok: false }, 400);
      const shift = String(b.shift || "A").toUpperCase();
      const class_id = Number(b.class_id || 0) || null;
      await env.DB.prepare("DELETE FROM assign WHERE day=? AND staff_id=?").bind(day, staff_id).run();
      if (on && room_id) {
        await env.DB.prepare("INSERT INTO assign(day,room_id,staff_id,shift,class_id) VALUES(?,?,?,?,?)").bind(day, room_id, staff_id, shift, class_id).run();
      }
      return json({ ok: true });
    }
    if (url.pathname === "/api/state") {
      const day = url.searchParams.get("day") || "";
      const assigns = day
        ? (await env.DB.prepare("SELECT day,room_id,staff_id,shift,class_id FROM assign WHERE day=?").bind(day).all()).results
        : (await env.DB.prepare("SELECT day,room_id,staff_id,shift,class_id FROM assign").all()).results;
      const staff = (await env.DB.prepare("SELECT * FROM staff ORDER BY team, last_name").all()).results;
      const rooms = (await env.DB.prepare("SELECT * FROM rooms ORDER BY name").all()).results;
      const classes = (await env.DB.prepare("SELECT * FROM classes").all()).results;
      const admin = (await env.DB.prepare("SELECT * FROM admin").all()).results;
      const aways = (await env.DB.prepare("SELECT * FROM away ORDER BY start").all()).results;
      let teams = (await env.DB.prepare("SELECT name FROM teams ORDER BY name").all()).results.map(r=>r.name);
      const fromStaff = [...new Set(staff.map(s=>s.team).filter(Boolean))];
      for (const name of fromStaff) {
        if (!teams.includes(name)) {
          await env.DB.prepare("INSERT OR IGNORE INTO teams(name) VALUES(?)").bind(name).run();
          teams.push(name);
        }
      }
      teams = [...new Set(teams)].sort();
      return json({ staff, rooms, classes, admin, assigns, aways, teams });
    }
    return new Response(appPage(), { headers: { "content-type": "text/html;charset=utf-8" } });
  },
};

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}

async function initSchema(env) {
  const tables = [
    "CREATE TABLE IF NOT EXISTS staff (id INTEGER PRIMARY KEY, display TEXT, last_name TEXT, first_name TEXT, team TEXT, position TEXT, phone_o TEXT, prd TEXT, eaos_soft TEXT, active TEXT)",
    "CREATE TABLE IF NOT EXISTS rooms (id INTEGER PRIMARY KEY, name TEXT)",
    "CREATE TABLE IF NOT EXISTS classes (id INTEGER PRIMARY KEY, class_num TEXT, course TEXT, primary_name TEXT, room_label TEXT, n INTEGER)",
    "CREATE TABLE IF NOT EXISTS assign (day TEXT, room_id INTEGER, staff_id INTEGER)",
    "CREATE TABLE IF NOT EXISTS admin (id INTEGER PRIMARY KEY, name TEXT, team TEXT, type TEXT, eaos TEXT, prd TEXT, notes TEXT)",
    "CREATE TABLE IF NOT EXISTS away (id INTEGER PRIMARY KEY, staff_id INTEGER, kind TEXT, start TEXT, end TEXT, note TEXT)",
    "CREATE TABLE IF NOT EXISTS teams (name TEXT PRIMARY KEY)"
  ];
  for (const sql of tables) {
    await env.DB.prepare(sql).run();
  }
  try { await env.DB.prepare("ALTER TABLE assign ADD COLUMN shift TEXT").run(); } catch (e) {}
  try { await env.DB.prepare("ALTER TABLE classes ADD COLUMN shift TEXT").run(); } catch (e) {}
  try { await env.DB.prepare("ALTER TABLE assign ADD COLUMN class_id INTEGER").run(); } catch (e) {}
}
async function seedIfEmpty(env) {
  const n = (await env.DB.prepare("SELECT COUNT(*) AS c FROM staff").first()).c;
  if (n && n > 0) return;
  const data = SEED;
  const stmts = [];
  data.staff.forEach((s,i)=>{
    stmts.push(env.DB.prepare(
      "INSERT INTO staff(id,display,last_name,first_name,team,position,phone_o,prd,eaos_soft,active) VALUES(?,?,?,?,?,?,?,?,?,?)"
    ).bind(i+1, s.display||"", s.last||"", s.first||"", s.team||"", s.position||"", s.phone_o||"", s.prd||"", s.eaos_soft||"", s.active||""));
  });
  data.classrooms.forEach((r,i)=>{
    stmts.push(env.DB.prepare("INSERT INTO rooms(id,name) VALUES(?,?)").bind(i+1, r.label));
  });
  data.classes.forEach(c=>{
    stmts.push(env.DB.prepare(
      "INSERT INTO classes(class_num,course,primary_name,room_label,n) VALUES(?,?,?,?,?)"
    ).bind(c.class_num||"", c.course||"", c.primary||"", c.label||"", c.n||0));
  });
  (data.admin||[]).forEach(a=>{
    stmts.push(env.DB.prepare(
      "INSERT INTO admin(name,team,type,eaos,prd,notes) VALUES(?,?,?,?,?,?)"
    ).bind(a.name||"", a.team||"", a.type||"", a.eaos||"", a.prd||"", a.notes||""));
  });
  await env.DB.batch(stmts);
}

const CLASS_SHIFT = {"26-100":"A","26-110":"B","26-240":"A","26-250":"A","26-260":"A","26-270":"B","26-320":"A","26-273":"A","26-275":"A","26-277":"A","26-280":"B","26-290":"A","26-295":"A","26-300":"B","26-310":"B","26-330":"B","26-340":"A","26-350":"B","26-370":"A","26-380":"A","26-430":"A","26-440":"A","26-450":"B","26-460":"B","26-470":"A","26-480":"A","26-490":"B","26-500":"B","26-502":"C","26-505":"C","26-510":"A","26-520":"A","26-530":"B","26-540":"C","26-560":"A","26-570":"A","26-590":"A","26-600":"A","26-610":"A","26-620":"A","26-640":"B","26-650":"A","26-660":"A","26-670":"C","26-680":"A","26-690":"C","26-700":"B","26-710":"A","26-720":"B","26-730":"A","26-740":"B"};
const SEED = {"staff":[{"display":"CWO4 Monsivais, E","last":"Monsivais","first":"Ed","team":"Admin","position":"DH","phone_o":"(850) 452-6308","prd":"","eaos_soft":"","active":"No"},{"display":"ITCM Ohrum, S","last":"Ohrum","first":"Scott","team":"Admin","position":"DLCPO","phone_o":"(850) 452-6217","prd":"2029-01-31","eaos_soft":"2028-09-30","active":"No"},{"display":"CTTCS Mitchell, A","last":"Mitchell","first":"Ashley","team":"Admin","position":"C School","phone_o":"","prd":"","eaos_soft":"","active":"No"},{"display":"CWTC Woodley, T","last":"Woodley","first":"Tyler","team":"Admin","position":"Support","phone_o":"","prd":"","eaos_soft":"","active":"No"},{"display":"ENS Falvo, G","last":"Falvo","first":"Gregg","team":"Admin","position":"Support","phone_o":"","prd":"","eaos_soft":"","active":"No"},{"display":"Display Name","last":"Last Name","first":"First Name","team":"Team","position":"Position","phone_o":"Phone Office","prd":"PRD","eaos_soft":"EAOS Soft","active":"Active N74 Instructor"},{"display":"IT1 Barcia, F","last":"Barcia","first":"Fabricio","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2027-07-01","eaos_soft":"2030-05-02","active":"Yes"},{"display":"IT1 Betzler, E","last":"Betzler","first":"Eden","team":"SYS","position":"Instructor","phone_o":"(850) 452-6343","prd":"2026-10-01","eaos_soft":"2028-06-14","active":"Yes"},{"display":"IT1 Castro, T","last":"Castro","first":"Tommy","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2027-07-01","eaos_soft":"2027-07-19","active":"Yes"},{"display":"IT1 Chaplin, T","last":"Chaplin","first":"Tyshawn","team":"SYS","position":"Instructor","phone_o":"(850) 452-6113","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT1 Espinoza, G","last":"Espinoza","first":"Gerardo","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"5/1/20267","eaos_soft":"2026-12-08","active":"Yes"},{"display":"IT1 Everitt, A","last":"Everitt","first":"Alexis","team":"Admin","position":"LPO","phone_o":"(850) 452-6112","prd":"2027-07-01","eaos_soft":"2027-11-19","active":"Yes"},{"display":"IT1 Fink, M","last":"Fink","first":"Matthew","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"2025-12-01","eaos_soft":"2025-12-25","active":"Yes"},{"display":"IT1 Gardiner, T","last":"Gardiner","first":"Torrey","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"2026-12-01","eaos_soft":"2026-12-14","active":"Yes"},{"display":"IT1 Gavaldon, C","last":"Gavaldon","first":"Cristobal","team":"JCC","position":"LPO","phone_o":"(850) 452-6112","prd":"2027-08-01","eaos_soft":"2027-08-18","active":"Yes"},{"display":"IT1 Gillespie, K","last":"Gillespie","first":"Kevin","team":"SYS","position":"LPO","phone_o":"(850) 452-6537","prd":"2026-12-01","eaos_soft":"2027-06-22","active":"Yes"},{"display":"IT1 Hartley, M","last":"Hartley","first":"Michael","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT1 Jacques, M","last":"Jacques","first":"","team":"","position":"","phone_o":"(850) 452-6537","prd":"2026-04-01","eaos_soft":"2030-05-30","active":"No"},{"display":"IT1 Kenney, G","last":"Kenney","first":"Garrett","team":"SYS","position":"Instructor","phone_o":"(850) 452-6343","prd":"2026-05-01","eaos_soft":"2028-04-07","active":"Yes"},{"display":"IT1 Malone, B","last":"Malone","first":"Brandon","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2027-03-01","eaos_soft":"2027-03-21","active":"Yes"},{"display":"IT1 Markham, J","last":"Markham","first":"Joshua","team":"ITA","position":"LPO","phone_o":"(850) 452-6537","prd":"2026-11-01","eaos_soft":"2029-03-22","active":"Yes"},{"display":"IT1 Massey","last":"Massey","first":"Joshua","team":"SYS","position":"Instructor","phone_o":"(850) 452-6112","prd":"","eaos_soft":"","active":""},{"display":"IT1 Matthews, D","last":"Matthews","first":"Dalton","team":"ITA","position":"Instructor","phone_o":"(850) 452-6994","prd":"2026-12-01","eaos_soft":"2030-08-22","active":"Yes"},{"display":"IT1 McAteer","last":"McAteer","first":"Michael","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"2026-03-01","eaos_soft":"2026-09-22","active":"Yes"},{"display":"IT1 Miller, A","last":"Miller","first":"Aaron","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"2026-10-01","eaos_soft":"2026-10-24","active":"Yes"},{"display":"IT1 Nelson, D","last":"Nelson","first":"David","team":"SYS","position":"Instructor","phone_o":"(850) 452-6113","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT1 Nelson, M","last":"Nelson","first":"Matthew","team":"SYS","position":"Instructor","phone_o":"(850) 452-6113","prd":"2026-11-01","eaos_soft":"2027-03-30","active":"Yes"},{"display":"IT1 Parker, B","last":"Parker","first":"Brandon","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"2027-01-01","eaos_soft":"2029-08-03","active":"Yes"},{"display":"IT1 Pickron, J","last":"Pickron","first":"Joshua","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2027-02-01","eaos_soft":"2027-05-11","active":"Yes"},{"display":"IT1 Polhemus, P","last":"Polhemus","first":"Peter","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"2027-07-31","eaos_soft":"2031-08-18","active":"Yes"},{"display":"IT1 Powell, J","last":"Powell","first":"Jacob","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2028-09-28","eaos_soft":"2028-09-28","active":"Yes"},{"display":"IT1 Ricke, L","last":"Ricke","first":"Lawrence","team":"SYS","position":"Instructor","phone_o":"(850) 452-6945","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT1 Rowe, B","last":"Rowe","first":"Brandon","team":"SYS","position":"Instructor","phone_o":"(850) 452-6299","prd":"2027-08-01","eaos_soft":"2027-08-30","active":"Yes"},{"display":"IT1 Sawyer, J","last":"Sawyer","first":"Josiah","team":"ITA","position":"Instructor","phone_o":"(850) 452-6343","prd":"2028-02-01","eaos_soft":"2027-02-15","active":"Yes"},{"display":"IT1 Sousoulas, G","last":"Sousoulas","first":"George","team":"Admin","position":"Instructor","phone_o":"(850) 452-6537","prd":"2025-08-01","eaos_soft":"2025-08-27","active":"Yes"},{"display":"IT1 Stephens, S","last":"Stephens","first":"Samantha","team":"JCC","position":"CS","phone_o":"(850) 452-6887","prd":"2027-06-01","eaos_soft":"2030-02-01","active":"Yes"},{"display":"IT1 Stiles","last":"Stiles","first":"Alexzander","team":"ITA","position":"Instructor","phone_o":"850-452-6112","prd":"2029-04-12","eaos_soft":"2032-12-31","active":""},{"display":"IT1 Thompson, D","last":"Thompson","first":"David","team":"","position":"","phone_o":"(850) 452-6343","prd":"2026-10-01","eaos_soft":"2026-10-18","active":"No"},{"display":"IT1 Voodre, J","last":"Voodre","first":"Jessica","team":"ITA","position":"Instructor","phone_o":"(850) 452-6299","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT1 Weiss, W","last":"Weiss","first":"William","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2029-06-01","eaos_soft":"2029-06-01","active":"Yes"},{"display":"IT1 Willis, A","last":"Willis","first":"Austin","team":"CM_CS","position":"CS","phone_o":"(850) 452-6887","prd":"2028-03-01","eaos_soft":"2030-11-10","active":"Yes"},{"display":"IT2 Boehler","last":"Boehler","first":"Micah","team":"SYS","position":"Instructor","phone_o":"(850) 452-6112","prd":"2029-05-31","eaos_soft":"2026-03-30","active":"Yes"},{"display":"IT2 Clark, T","last":"Clark","first":"Trejean","team":"SYS","position":"Instructor","phone_o":"(850) 452-6229","prd":"2027-07-01","eaos_soft":"2029-04-02","active":"Yes"},{"display":"IT2 Cochran, P","last":"Cochran","first":"Peyton","team":"SYS","position":"Instructor","phone_o":"(850) 452-6113","prd":"2025-06-25","eaos_soft":"","active":"Yes"},{"display":"IT2 Davis","last":"Lauryn","first":"Gabryelle","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2029-08-26","eaos_soft":"","active":""},{"display":"IT2 Dewitt, K","last":"Dewitt","first":"Kyle","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2025-09-29","eaos_soft":"","active":"Yes"},{"display":"IT2 Dominique, P","last":"Dominique","first":"Presten","team":"CM_CS","position":"CS","phone_o":"(850) 452-6887","prd":"2027-04-01","eaos_soft":"2028-01-13","active":"Yes"},{"display":"IT2 Garza, B","last":"Garza","first":"Brian","team":"SYS","position":"Instructor","phone_o":"(850) 452-6945","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT2 Hall, B","last":"Hall","first":"Brandon","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"5/25/2028","eaos_soft":"10/21/2028","active":"Yes"},{"display":"IT2 Hensley, W","last":"Hensley","first":"William","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2025-07-28","eaos_soft":"2031-04-27","active":"YES"},{"display":"IT2 Huyghue, A","last":"Huyghue,","first":"Ajani","team":"SYS","position":"Instructor","phone_o":"(850) 452-6343","prd":"#N/A","eaos_soft":"#N/A","active":"Yes"},{"display":"IT2 Junker, J","last":"Junker","first":"","team":"--","position":"","phone_o":"(850) 452-6113","prd":"2025-11-01","eaos_soft":"2026-07-24","active":"No"},{"display":"IT2 Kus, T","last":"Kus","first":"Tyler","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"2025-05-08","eaos_soft":"","active":"Yes"},{"display":"IT2 McClamma, D","last":"McClamma","first":"Devin","team":"SYS","position":"Instructor","phone_o":"(850) 452-6299","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT2 Michaels, B","last":"Michaels","first":"Bryce","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2028-10-21","eaos_soft":"2028-10-16","active":"Yes"},{"display":"IT2 Patterson, R","last":"Patterson","first":"Rachael","team":"SYS","position":"Instructor","phone_o":"(850) 452-6112","prd":"#N/A","eaos_soft":"#N/A","active":"Yes"},{"display":"IT2 Petelle, L","last":"Petelle","first":"Lars","team":"JCC","position":"","phone_o":"(850) 452-6112","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT2 Polk, J","last":"Polk","first":"Janae","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2028-06-23","eaos_soft":"2030-11-26","active":"Yes"},{"display":"IT2 Ponce, R","last":"Ponce","first":"Ricardo","team":"SYS","position":"Instructor","phone_o":"(850) 452-6352","prd":"2027-12-01","eaos_soft":"2028-01-28","active":"Yes"},{"display":"IT2 Riccardi, S","last":"Riccardi","first":"Samuel","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"2027-05-01","eaos_soft":"2027-05-17","active":"Yes"},{"display":"IT2 Ridley, C","last":"Ridley","first":"Cody","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2029-05-31","eaos_soft":"2027-06-16","active":"No"},{"display":"IT2 Ross, R","last":"Ross","first":"Robert","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT2 SantaMaria, D","last":"SantaMaria","first":"Dominick","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2029-01-01","eaos_soft":"","active":"Yes"},{"display":"IT2 SHELTON","last":"SHELTON","first":"JORDAN","team":"ITA","position":"Instructor","phone_o":"850-452-6112","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT2 Speaks, J","last":"Speaks","first":"","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT2 VanHuss","last":"Justin","first":"Thomas","team":"ITA","position":"Instructor?","phone_o":"","prd":"","eaos_soft":"","active":""},{"display":"ITC Adams","last":"B","first":"","team":"ITA","position":"Instructor?","phone_o":"(850) 452-6112","prd":"","eaos_soft":"","active":"No"},{"display":"ITC Alacar, B","last":"Alacar","first":"","team":"--","position":"Course Manager","phone_o":"(850) 452-6113","prd":"2026-12-01","eaos_soft":"2026-12-13","active":"No"},{"display":"ITC Clay, C","last":"Clay","first":"Cody","team":"JCC","position":"LCPO/Instructor","phone_o":"(850) 452-6853","prd":"2028-09-01","eaos_soft":"2028-08-31","active":"Yes"},{"display":"ITC Darr, B","last":"Darr","first":"","team":"Admin","position":"CMEO","phone_o":"(850) 452-6343","prd":"2027-07-01","eaos_soft":"2027-03-31","active":"No"},{"display":"ITC Fode, D.","last":"Fode","first":"Dale","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"","eaos_soft":"","active":"No"},{"display":"ITC Helton, D","last":"Helton","first":"","team":"ITA","position":"LCPO","phone_o":"(850) 452-6112","prd":"2027-08-01","eaos_soft":"2025-10-17","active":"Yes"},{"display":"ITC Johnson, R","last":"Johnson","first":"","team":"SYS","position":"Instructor","phone_o":"(850) 452-6352","prd":"2025-10-01","eaos_soft":"2026-05-19","active":"Yes"},{"display":"ITC Kelly, J","last":"Kelly","first":"Jonathan","team":"SYS","position":"LCPO/Instructor","phone_o":"8504526343","prd":"","eaos_soft":"","active":"No"},{"display":"ITC Martinez, A","last":"Martinez","first":"","team":"JCC","position":"LCPO","phone_o":"(850) 452-6994","prd":"2026-08-05","eaos_soft":"2028-11-03","active":"Yes"},{"display":"ITC Moon, R","last":"Moon","first":"","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2026-07-01","eaos_soft":"2027-01-28","active":"Yes"},{"display":"ITC Ragland, C","last":"Ragland","first":"Chandler","team":"ITA","position":"LCPO/Instructor","phone_o":"(850) 452-6765","prd":"","eaos_soft":"","active":""},{"display":"ITC Smith, A","last":"Smith","first":"","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"2026-11-01","eaos_soft":"2026-11-30","active":"Yes"},{"display":"ITC Sweitzer, S","last":"Sweitzer","first":"","team":"ITA","position":"Instructor","phone_o":"(850) 452-6112","prd":"2026-10-01","eaos_soft":"2026-10-19","active":"Yes"},{"display":"ITC Tynes, S","last":"Tynes","first":"","team":"Admin","position":"LCPO","phone_o":"(850) 452-6357","prd":"2027-05-01","eaos_soft":"2027-05-15","active":"Yes"},{"display":"ITN1 Kissinger","last":"Kissinger","first":"","team":"ITA","position":"Instructor","phone_o":"(850) 452-6537","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Ables, A","last":"Ables","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Carmouche","last":"Carmouche","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Chandler, J","last":"Chandler-Smith","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Funches, D","last":"Funches","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6966","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Harris, C","last":"Harris","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Hendrickson, R","last":"Hendrickson","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Impastato, A","last":"Impastato","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Ladd, E","last":"Ladd","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Lamar, T","last":"Lamar","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Lysaght, J","last":"Lysaght","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Montgomery, D","last":"Montgomery","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Moser","last":"Mr. Moser","first":"","team":"SYS","position":"Instructor","phone_o":"","prd":"","eaos_soft":"","active":""},{"display":"Mr. Novak, J","last":"Novak","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Wade, B","last":"Wade","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6519","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Wentland, J","last":"Wentland","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mr. Wheeler, D","last":"Wheeler","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Mrs. Jeanneret, K","last":"Jeanneret","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"Ms. Bonham, A","last":"Bonham","first":"","team":"GS","position":"Instructor","phone_o":"(850) 452-6717","prd":"","eaos_soft":"","active":"Yes"},{"display":"IT2 Wright, N","last":"Wright","first":"Nyla","team":"SYS","position":"Instructor","phone_o":"(850) 452-6343","prd":"2028-10-08","eaos_soft":"2028-10-08","active":""},{"display":"IT2 Roach","last":"Roach","first":"Johnny","team":"ITA","position":"Instructor","phone_o":"8504526112","prd":"2029-07-24","eaos_soft":"","active":"No"},{"display":"IT2 Van Huss, J","last":"Van Huss","first":"Justin","team":"ITA","position":"Instructor","phone_o":"","prd":"","eaos_soft":"","active":"No"},{"display":"IT2 Davis, Lauryn","last":"Davis","first":"Lauryn","team":"SYS","position":"Instructor","phone_o":"","prd":"","eaos_soft":"","active":"No"},{"display":"IT1 Rodriguez Crespo, C.","last":"Rodriguez Crespo","first":"Christopher","team":"SYS","position":"Instructor","phone_o":"(850) 452-6343","prd":"","eaos_soft":"","active":"Yes"}],"classrooms":[{"bldg":"1099","room":"102B","label":"1099-102B"},{"bldg":"1099","room":"102C","label":"1099-102C"},{"bldg":"1099","room":"103","label":"1099-103"},{"bldg":"1099","room":"103B","label":"1099-103B"},{"bldg":"1099","room":"113B","label":"1099-113B"},{"bldg":"1099","room":"114","label":"1099-114"},{"bldg":"1099","room":"115B","label":"1099-115B"},{"bldg":"1099","room":"116B","label":"1099-116B"},{"bldg":"1099","room":"121B","label":"1099-121B"},{"bldg":"1099","room":"123","label":"1099-123"},{"bldg":"1099","room":"123B","label":"1099-123B"},{"bldg":"1099","room":"137","label":"1099-137"},{"bldg":"1099","room":"145","label":"1099-145"},{"bldg":"1099","room":"153","label":"1099-153"},{"bldg":"1099","room":"155","label":"1099-155"},{"bldg":"1099","room":"202","label":"1099-202"},{"bldg":"1099","room":"202B","label":"1099-202B"},{"bldg":"1099","room":"203B","label":"1099-203B"},{"bldg":"1099","room":"204A","label":"1099-204A"},{"bldg":"1099","room":"213B","label":"1099-213B"},{"bldg":"1099","room":"214B","label":"1099-214B"},{"bldg":"1099","room":"217B","label":"1099-217B"},{"bldg":"1099","room":"218B","label":"1099-218B"},{"bldg":"1099","room":"228B","label":"1099-228B"},{"bldg":"1099","room":"229C","label":"1099-229C"},{"bldg":"1099","room":"230C","label":"1099-230C"},{"bldg":"1099","room":"233C","label":"1099-233C"},{"bldg":"1099","room":"239C","label":"1099-239C"},{"bldg":"502","room":"104W","label":"502-104W"}],"classes":[{"class_num":"26-100","course":"IT 'C' JCC","primary":"IT1 Markham, J","label":"1099-214B","n":10},{"class_num":"26-110","course":"IT 'C' JCC","primary":"ITC Clay, C","label":"1099-218B","n":24},{"class_num":"26-240","course":"IT 'C' SYSAD","primary":"Mr. Wade, B","label":"1099-153","n":13},{"class_num":"26-250","course":"IT 'C' SYSAD","primary":"Mr. Wentland, J","label":"1099-113B","n":19},{"class_num":"26-260","course":"IT 'C' SYSAD","primary":"IT1 Ricke, L","label":"1099-114","n":16},{"class_num":"26-270","course":"IT 'C' SYSAD","primary":"IT1 Massey","label":"1099-153","n":15},{"class_num":"26-273","course":"IT 'C' SYSAD","primary":"IT2 McClamma, D","label":"","n":9},{"class_num":"26-275","course":"IT 'C' SYSAD","primary":"IT2 McClamma, D","label":"","n":13},{"class_num":"26-277","course":"IT 'C' SYSAD","primary":"IT2 McClamma, D","label":"","n":8},{"class_num":"26-280","course":"IT 'C' SYSAD","primary":"IT2 Garza, B","label":"1099-145","n":18},{"class_num":"26-290","course":"IT 'C' SYSAD","primary":"Mr. Harris, C","label":"1099-137","n":15},{"class_num":"26-295","course":"IT 'C' SYSAD","primary":"IT1 Chaplin, T","label":"1099-155","n":16},{"class_num":"26-300","course":"IT 'C' SYSAD","primary":"IT1 Betzler, E","label":"1099-116B","n":13},{"class_num":"26-310","course":"IT 'C' SYSAD","primary":"IT2 Clark, T","label":"1099-123B","n":19},{"class_num":"26-320","course":"IT 'C' SYSAD","primary":"IT2 McClamma, D","label":"1099-116B","n":17},{"class_num":"26-330","course":"IT 'C' SYSAD","primary":"IT1 Nelson, M","label":"1099-137","n":16},{"class_num":"26-340","course":"IT 'C' SYSAD","primary":"IT1 Nelson, D","label":"1099-115B","n":14},{"class_num":"26-350","course":"IT 'C' SYSAD","primary":"Mr. Moser","label":"1099-239C","n":25},{"class_num":"26-370","course":"IT 'C' SYSAD","primary":"IT2 Patterson, R","label":"1099-153","n":15},{"class_num":"26-380","course":"IT 'C' SYSAD","primary":"Mr. Ables","label":"1099-202B","n":16},{"class_num":"26-430","course":"IT 'A' COMMS","primary":"IT1 Hartley, M","label":"1099-202B","n":25},{"class_num":"26-440","course":"IT 'A' COMMS","primary":"IT2 Riccardi, S","label":"1099-121B","n":25},{"class_num":"26-450","course":"IT 'A' COMMS","primary":"IT1 Weiss, W","label":"1099-203B","n":24},{"class_num":"26-460","course":"IT 'A' COMMS","primary":"Ms. Bonham, A","label":"1099-103B","n":23},{"class_num":"26-470","course":"IT 'A' COMMS","primary":"IT1 Pickron, J","label":"1099-214B","n":24},{"class_num":"26-480","course":"IT 'A' COMMS","primary":"IT2 SantaMaria, D","label":"1099-217B","n":25},{"class_num":"26-490","course":"IT 'A' COMMS","primary":"IT2 Hall, B","label":"1099-103","n":19},{"class_num":"26-500","course":"IT 'A' COMMS","primary":"IT1 Stiles","label":"1099-230C","n":22},{"class_num":"26-502","course":"IT 'A' CCNA","primary":"IT1 Powell, J","label":"1099-202","n":18},{"class_num":"26-505","course":"IT 'A' CCNA","primary":"IT1 Polhemus, P","label":"502-104W","n":20},{"class_num":"26-510","course":"IT 'A' COMMS","primary":"IT1 Barcia, F","label":"1099-229C","n":24},{"class_num":"26-520","course":"IT 'A' COMMS","primary":"IT1 Espinoza, G","label":"1099-121B","n":23},{"class_num":"26-530","course":"IT 'A' COMMS","primary":"IT1 Matthews, D","label":"1099-202B","n":24},{"class_num":"26-540","course":"IT 'A' COMMS","primary":"IT1 Parker, B","label":"1099-214B","n":24},{"class_num":"26-560","course":"IT 'A' ITE","primary":"Mr. Lysaght, J","label":"1099-204A","n":16},{"class_num":"26-570","course":"IT 'A' ITE","primary":"IT2 Ridley, C","label":"1099-233C","n":14},{"class_num":"26-590","course":"IT 'A' ITE","primary":"Mr. Lamar, T","label":"1099-121B","n":22},{"class_num":"26-600","course":"IT 'A' ITE","primary":"IT2 Ross, R","label":"1099-213B","n":22},{"class_num":"26-610","course":"IT 'A' ITE","primary":"IT2 Speaks, J","label":"1099-123","n":21},{"class_num":"26-620","course":"IT 'A' ITE","primary":"Mr. Carmouche","label":"1099-230C","n":21},{"class_num":"26-640","course":"IT 'A' ITE","primary":"Mrs. Jeanneret, K","label":"1099-228B","n":25},{"class_num":"26-650","course":"IT 'A' ITE","primary":"IT1 Malone, B","label":"1099-102C","n":25},{"class_num":"26-660","course":"IT 'A' ITE","primary":"IT1 Fink, M","label":"1099-103B","n":23},{"class_num":"26-670","course":"IT 'A' ITE","primary":"IT1 Sawyer, J","label":"1099-103B","n":25},{"class_num":"26-680","course":"IT 'A' ITE","primary":"Mr. Funches, D","label":"1099-228B","n":25},{"class_num":"26-690","course":"IT 'A' ITE","primary":"IT1 Voodre, J","label":"1099-102B","n":25},{"class_num":"26-700","course":"IT 'A' ITE","primary":"Mr. Impastato, A","label":"1099-102B","n":25},{"class_num":"26-710","course":"IT 'A' ITE","primary":"Mr. Montgomery, D","label":"1099-229C","n":25},{"class_num":"26-720","course":"IT 'A' ITE","primary":"ITN1 Kissinger","label":"1099-230C","n":25},{"class_num":"26-730","course":"IT 'A' ITE","primary":"ITC Helton, D","label":"1099-121B","n":25},{"class_num":"26-740","course":"IT 'A' ITE","primary":"Mr. Chandler, J","label":"1099-229C","n":19}],"admin":[{"name":"IT1 MCATEER","team":"ITA","type":"SEPARATION","eaos":"2026-09-22","prd":"2026-09-01","notes":"ON TERMINAL"},{"name":"IT1 MILLER, A","team":"ITA","type":"SEPARATION","eaos":"2026-10-24","prd":"2026-10-01","notes":"SEPARATION PKG COMPLETE"},{"name":"ITC SWEITZER, S","team":"ITA","type":"RETIREMENT","eaos":"2026-10-19","prd":"2026-10-01","notes":"ON TERMINAL"},{"name":"ITC SMITH, A","team":"ITA","type":"RETIREMENT","eaos":"2026-11-30","prd":"2026-11-01","notes":"ON TERMINAL"},{"name":"IT1 GARDINER, T","team":"ITA","type":"SEPARATION","eaos":"2026-12-14","prd":"","notes":"PENDING MEDBOARD IN SEPTEMBER"}]};


async function syncStaff(env) {
  const n = (await env.DB.prepare("SELECT COUNT(*) AS c FROM staff").first()).c || 0;
  const want = (SEED.staff || []).length;
  if (n >= want) return;
  const have = (await env.DB.prepare("SELECT display, last_name FROM staff").all()).results || [];
  const keys = new Set(have.map(s => ((s.display||"")+"|"+(s.last_name||"")).toLowerCase()));
  const stmts = [];
  SEED.staff.forEach((s,i) => {
    const k = ((s.display||"")+"|"+(s.last||"")).toLowerCase();
    if (keys.has(k)) return;
    stmts.push(env.DB.prepare(
      "INSERT INTO staff(display,last_name,first_name,team,position,phone_o,prd,eaos_soft,active) VALUES(?,?,?,?,?,?,?,?,?)"
    ).bind(s.display||"", s.last||"", s.first||"", s.team||"", s.position||"", s.phone_o||"", s.prd||"", s.eaos_soft||"", s.active||""));
  });
  if (stmts.length) await env.DB.batch(stmts);
}
async function patchShifts(env) {
  const row = await env.DB.prepare("SELECT shift FROM classes LIMIT 1").first();
  if (row && row.shift) return;
  const stmts = Object.keys(CLASS_SHIFT).map(cn =>
    env.DB.prepare("UPDATE classes SET shift=? WHERE class_num=?").bind(CLASS_SHIFT[cn]||"", cn)
  );
  if (stmts.length) await env.DB.batch(stmts);
}

function loginPage(err) {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ops login</title>
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:grid;place-items:center;background:#070b12;color:#e8f1ff;font-family:Segoe UI,system-ui,sans-serif}
form{background:#0d1624;border:1px solid #d4b46a;padding:1.4rem;width:min(24rem,92vw);position:relative;z-index:2}
label{display:block;color:#8aa0b8;font-size:.8rem;margin-bottom:.35rem}
input{width:100%;padding:.7rem .65rem;background:#0a1220;color:#e8f1ff;border:1px solid #243044;font-size:16px;pointer-events:auto}
button{margin-top:.8rem;width:100%;padding:.7rem;background:#1a3a68;color:#d4b46a;border:1px solid #d4b46a;font-size:1rem;cursor:pointer}
.err{color:#e07070;margin-bottom:.6rem}
a{color:#8aa0b8}
.row{display:flex;gap:.4rem;align-items:center}
.row input{flex:1}
.row button{margin-top:0;width:auto;padding:.7rem .8rem;white-space:nowrap}
</style></head><body>
<form method="post" action="/login" autocomplete="on">
<div style="color:#d4b46a;letter-spacing:.14em;text-transform:uppercase;margin-bottom:.8rem">N74 Ops</div>
${err ? `<div class="err">${err}</div>` : ""}
<label for="email">LMS email (optional)</label>
<input id="email" type="email" name="email" autocomplete="username" placeholder="admin@lms.local">
<label for="password" style="margin-top:.7rem">Password</label>
<div class="row">
<input id="password" type="password" name="password" autocomplete="current-password" autofocus required>
<button type="button" id="toggle">Show</button>
</div>
<button type="submit">Enter</button>
<p class="muted" style="margin-top:.85rem;color:#8aa0b8;font-size:.8rem;line-height:1.45">
Anyone with the staff password can enter. LMS accounts also work:<br>
<code>admin@lms.local</code> / <code>admin123</code><br>
<code>instructor@lms.local</code> / <code>teach123</code>
</p>
<p style="margin-top:1rem;font-size:.8rem"><a href="https://novakornothing.com">Home</a></p>
</form>
<script>
document.getElementById("toggle").onclick=function(){
  var i=document.getElementById("password");
  var hide=i.type==="password";
  i.type=hide?"text":"password";
  this.textContent=hide?"Hide":"Show";
  i.focus();
};
</script>
</body></html>`;
}

function appPage() {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ops</title>
<style>
:root{--bg:#080c14;--card:#101a28;--g:#d4b46a;--ice:#eaf2ff;--dim:#8aa0b8;--line:#2a3a50;--bad:#e07070;--ok:#5ee0a0}
*{box-sizing:border-box;margin:0;padding:0}
body{font:16px/1.45 "Segoe UI",system-ui,sans-serif;background:var(--bg);color:var(--ice)}
header{display:flex;gap:.8rem;align-items:center;padding:.55rem 1.15rem;background:#060a10;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:6}
header strong{color:var(--g);letter-spacing:.14em;text-transform:uppercase;font-size:.78rem}
header a{color:var(--dim);text-decoration:none;margin-left:.55rem}
.bar{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;padding:.45rem 1.15rem .5rem;background:#0b1220;border-bottom:1px solid var(--line);position:sticky;top:2.55rem;z-index:5}
.seg{display:flex;border:1px solid var(--line);overflow:hidden}
.seg button{border:0;border-right:1px solid var(--line);border-radius:0}
.seg button:last-child{border-right:0}
.bar input,.bar select,input,select{background:#0a1220;color:var(--ice);border:1px solid var(--line);padding:.42rem .5rem}
button.g,button.x{padding:.4rem .7rem;cursor:pointer}
button.g{background:#1a3a68;color:var(--g);border:1px solid var(--g)}
button.x{background:transparent;color:var(--dim);border:1px solid var(--line)}
.hint{padding:.35rem 1.15rem .15rem;color:var(--dim);font-size:.9rem}
.alert{margin:.45rem 1.1rem;padding:.55rem .7rem;border:1px solid var(--bad);background:#241015;cursor:pointer}
.strip{display:grid;grid-template-columns:repeat(5,1fr);gap:.3rem;padding:.1rem 1.15rem .55rem}
.daypill{background:var(--card);border:1px solid var(--line);padding:.45rem;cursor:pointer}
.daypill.on{border-color:var(--g);background:#173154}
.daypill.bad{border-color:var(--bad)}
.daypill b{display:block;color:var(--g);font-size:.75rem}
.wrap{display:grid;grid-template-columns:minmax(0,1fr) 22rem;min-height:58vh}
@media(max-width:960px){.wrap{grid-template-columns:1fr}.panel{position:relative;height:auto;top:auto}}
.list{padding:0 1.1rem 2rem}
.row{display:grid;grid-template-columns:6.2rem 2.2rem minmax(0,1fr) 8.2rem;gap:.45rem;align-items:center;padding:.62rem .65rem;border:1px solid var(--line);background:var(--card);margin-bottom:.3rem;cursor:pointer}
.row:hover{border-color:#4a678a}
.row.on{outline:1px solid var(--g)}
.row.bad{border-color:var(--bad);background:#241015}
.row .cn{color:var(--g);font-weight:700}
.panel{border-left:1px solid var(--line);background:#0b121c;padding:1rem;position:sticky;top:5.5rem;height:calc(100vh - 5.5rem);overflow:auto}
.panel h2{color:var(--g);font-size:1.05rem;margin-bottom:.3rem}
.drop{min-height:3rem;border:1px dashed var(--line);padding:.45rem;margin:.45rem 0;background:#0a1220}
.drop.bad{border-color:var(--bad);background:#2a1010}
.chip{display:inline-block;margin:.12rem .18rem;padding:.3rem .45rem;background:#152334;border-left:3px solid var(--ok);cursor:pointer}
.chip.away{border-left-color:var(--bad)}
.pick{max-height:11rem;overflow:auto;border:1px solid var(--line);padding:.35rem;background:#0a1220}
.muted{color:var(--dim)}
.hide{display:none !important}
.stat{font-size:.78rem;color:var(--dim);margin-top:.15rem}
.toast{position:fixed;bottom:1rem;right:1rem;background:#173154;color:var(--g);border:1px solid var(--g);padding:.55rem .8rem;z-index:9}
.formgrid{display:grid;gap:.4rem;margin:.6rem 0}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:.5rem;margin:.2rem 0 1rem}
.card{background:var(--card);border:1px solid var(--line);padding:.7rem}
.card b{display:block;color:var(--g);font-size:1.35rem}
table.rep{width:100%;border-collapse:collapse;font-size:.92rem;margin:.4rem 0 1rem}
table.rep th,table.rep td{text-align:left;padding:.4rem .35rem;border-bottom:1px solid var(--line)}
table.rep th{color:var(--g);font-weight:600}
@media print{
  header,.bar,.strip,.hint,.alert,.toast,.panel{display:none !important}
  .wrap{display:block}
  body{background:#fff;color:#111}
  .card,.row{border-color:#ccc;background:#fff}
}
</style></head><body>
<header>
  <strong>N74 schedule</strong>
  <span class="muted" id="kpi"></span>
  <span style="margin-left:auto"><a href="https://novakornothing.com">Home</a><a href="/logout">Log out</a></span>
</header>
<div class="bar">
  <input type="date" id="day">
  <div class="seg">
  <button class="g" id="vDay" type="button">Day</button>
  <button class="x" id="vWeek" type="button">Week</button>
  <button class="x" id="vRep" type="button">Report</button>
  </div>
  <div class="seg">
  <button class="x" id="byClass" type="button">Classes</button>
  <button class="x" id="byTeam" type="button">Teams</button>
  <button class="x" id="byRoom" type="button">Rooms</button>
  <button class="x" id="byAway" type="button">Leave &amp; duty</button>
  <button class="x" id="byPeople" type="button">People</button>
  <button class="x" id="byMine" type="button">My schedule</button>
  </div>
  <select id="fltShift"><option value="">All shifts</option><option value="A">A</option><option value="B">B</option><option value="C">C</option></select>
  <select id="fltNeed"><option value="">All classes</option><option value="open">Need instructor</option><option value="away">Need replacement</option><option value="issue">All problems</option></select>
  <select id="team"><option value="">All teams</option></select>
  <input id="q" placeholder="Search" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" name="ops_q_noshare">
</div>
<div id="fixbar" class="alert hide"></div>
<p class="hint" id="hint">Day board — click a class to assign.</p>
<div id="strip" class="strip"></div>
<div class="wrap">
  <div id="board" class="list">Loading…</div>
  <aside class="panel" id="panel"><p class="muted">Click a class to assign or change the instructor.</p></aside>
</div>
<div id="toast" class="toast hide"></div>
<script>
const CLASS_SHIFT = ${JSON.stringify(CLASS_SHIFT)};
let STATE={staff:[],rooms:[],classes:[],admin:[],assigns:[],aways:[]};
let view="day", sort="class", selected=null;
const $=id=>document.getElementById(id);
const today=()=>new Date().toISOString().slice(0,10);
const nm=s=>s && (s.display||((s.last_name||"")+(s.first_name?(", "+s.first_name):""))) || "Unknown";
function addDays(iso,n){const d=new Date(iso+"T12:00:00");d.setDate(d.getDate()+n);return d.toISOString().slice(0,10)}
function weekStart(iso){const d=new Date(iso+"T12:00:00");d.setDate(d.getDate()-((d.getDay()+6)%7));return d.toISOString().slice(0,10)}
function dow(iso){return new Date(iso+"T12:00:00").getDay()}
function isWeekend(iso){const d=dow(iso);return d===0||d===6}
function workday(iso){
  let d=iso||today();
  while(isWeekend(d)) d=addDays(d,1);
  return d;
}
$("day").value=workday(today());
function staffById(id){return STATE.staff.find(s=>s.id===id)}
function clsShift(c){return (c.shift||CLASS_SHIFT[c.class_num]||"A").toUpperCase()}
function classPeople(classId, day){
  const d=day||$("day").value||today();
  return STATE.assigns.filter(a=>a.class_id===classId && (!a.day||a.day===d)).map(a=>staffById(a.staff_id)).filter(Boolean);
}
function teachersOn(c, day){
  const assigned=classPeople(c.id, day);
  if(assigned.length) return assigned;
  const listed=matchListed(c);
  return listed?[listed]:[];
}
function roomShiftClasses(roomLabel, sh){return STATE.classes.filter(c=>c.room_label===roomLabel && clsShift(c)===sh)}
function awayOn(staffId, day){return (STATE.aways||[]).find(a=>a.staff_id===staffId && a.start<=day && (a.end||a.start)>=day)}
function classBlocked(c, day){
  const ppl=teachersOn(c, day);
  const why=[];
  ppl.forEach(s=>{ const a=awayOn(s.id, day); if(a) why.push(nm(s)+" on "+a.kind); });
  if(ppl.length>1) why.push("Two instructors");
  if(roomShiftClasses(c.room_label,clsShift(c)).length>1) why.push("Two classes same room/shift");
  return why;
}
function matchListed(c){
  const raw=(c.primary_name||"").toLowerCase().trim();
  if(!raw) return null;
  return STATE.staff.find(s=>{
    const last=(s.last_name||"").toLowerCase();
    const disp=(s.display||"").toLowerCase();
    const n=nm(s).toLowerCase();
    if(last && last.length>2 && raw.indexOf(last)>=0) return true;
    if(disp && raw.indexOf(disp)>=0) return true;
    if(n && raw.indexOf(n)>=0) return true;
    return false;
  })||null;
}
function toast(msg){$("toast").textContent=msg;$("toast").classList.remove("hide");setTimeout(()=>$("toast").classList.add("hide"),1800)}
function weekDays(){const ws=weekStart($("day").value||today());return [0,1,2,3,4].map(i=>addDays(ws,i))}
function dayStats(d){
  if(isWeekend(d)) return {covered:0, open:0, repl:0, issues:0, total:0, off:1};
  let covered=0, open=0, repl=0, issues=0;
  STATE.classes.forEach(c=>{
    const who=STATE.assigns.filter(a=>a.day===d && a.class_id===c.id);
    const ppl=who.map(a=>staffById(a.staff_id)).filter(Boolean);
    if(ppl.length) covered++; else open++;
    if(ppl.some(s=>awayOn(s.id,d))) repl++;
    if(classBlocked(Object.assign({},c),d).length && ppl.length) issues++;
    else if(roomShiftClasses(c.room_label,clsShift(c)).length>1) issues++;
  });
  return {covered, open, repl, issues, total:STATE.classes.length};
}
async function load(){
  const day=$("day").value||today();
  const wide = view==="week" || view==="report" || sort==="away" || sort==="mine" || sort==="people";
  const r=await fetch(wide?"/api/state":("/api/state?day="+day));
  STATE=await r.json();
  if(!STATE.aways) STATE.aways=[];
  const st=dayStats(day);
  $("kpi").textContent=st.covered+" of "+st.total+" covered · "+st.repl+" replacements";
  if(!STATE.teams) STATE.teams=[];
  refreshTeamSelect();
  render();
}
async function place(sid, roomId, on, shift, classId){
  await fetch("/api/assign",{method:"POST",headers:{"content-type":"application/json"},
    body:JSON.stringify({day:$("day").value||today(),staff_id:sid,room_id:roomId,on:on,shift:shift||"A",class_id:classId||0})});
  toast(on?"Saved":"Cleared");
  await load();
}
function paintStrip(){
  if(sort==="away"||sort==="people"){ $("strip").innerHTML=""; return; }
  const names=["Mon","Tue","Wed","Thu","Fri"];
  const cur=$("day").value||today();
  $("strip").innerHTML=weekDays().map((d,i)=>{
    const st=dayStats(d);
    const red=st.repl||st.issues;
    return '<div class="daypill '+(d===cur?"on":"")+(red?" bad":"")+'" data-open="'+d+'"><b>'+names[i]+' '+d.slice(5)+'</b><span class="stat">'+st.covered+'/'+st.total+(st.repl?" · "+st.repl+" out":"")+'</span></div>';
  }).join("");
  $("strip").querySelectorAll("[data-open]").forEach(el=>el.onclick=()=>{ $("day").value=el.dataset.open; view="day"; sort="class"; load(); });
}
function paintFixbar(){
  const day=$("day").value||today();
  if(view==="report"||sort==="away"||sort==="people"||sort==="mine"||isWeekend($("day").value||today())){ $("fixbar").classList.add("hide"); return; }
  const hits=STATE.classes.filter(c=>classBlocked(c,day).length);
  if(!hits.length){ $("fixbar").classList.add("hide"); return; }
  $("fixbar").classList.remove("hide");
  $("fixbar").innerHTML=hits.length+" issue"+(hits.length>1?"s":"")+" — click a class to fix: "+
    hits.map(c=>'<button class="x" type="button" data-fix="'+c.id+'" style="margin:.15rem .15rem 0 0">'+c.class_num+'</button>').join("");
  $("fixbar").onclick=null;
  $("fixbar").querySelectorAll("[data-fix]").forEach(b=>b.onclick=e=>{
    e.stopPropagation();
    view="day"; sort="class"; selected=+b.dataset.fix;
    $("fltNeed").value="issue";
    render();
    openClass(selected);
  });
}

function staffRows(){
  return STATE.staff.map(s=>({
    value:String(s.id),
    label:nm(s)+(s.team?" · "+s.team:""),
    search:(nm(s)+" "+(s.display||"")+" "+(s.last_name||"")+" "+(s.first_name||"")+" "+(s.team||"")+" "+(s.position||"")).toLowerCase()
  }));
}
function lockInput(inp){
  if(!inp) return;
  inp.setAttribute("autocomplete","off");
  inp.setAttribute("autocorrect","off");
  inp.setAttribute("autocapitalize","off");
  inp.setAttribute("spellcheck","false");
  inp.setAttribute("name","ops_"+Math.random().toString(36).slice(2));
  inp.setAttribute("data-lpignore","true");
  inp.setAttribute("data-1p-ignore","true");
}
function bindFinder(inp, box, rows, onpick){
  lockInput(inp);
  function paint(){
    const q=(inp.value||"").toLowerCase().trim();
    let hits=rows.filter(r=>{
      const hay=(r.search||r.label||"").toLowerCase();
      return !q || hay.indexOf(q)>=0;
    });
    if(!q) hits=hits.slice(0,8);
    else hits=hits.slice(0,25);
    box.innerHTML=(q?"":'<span class="muted">Type to search all '+rows.length+' names</span>')+
      hits.map(r=>'<div class="chip" data-val="'+String(r.value).replace(/"/g,"")+'" data-lab="'+(r.label||"").replace(/"/g,"")+'" style="display:block">'+r.label+'</div>').join("")||
      '<span class="muted">No match</span>';
    box.querySelectorAll("[data-val]").forEach(el=>el.onclick=()=>{
      inp.value=el.dataset.lab;
      inp.dataset.val=el.dataset.val;
      box.innerHTML="";
      if(onpick) onpick(el.dataset.val, el.dataset.lab);
    });
  }
  inp.oninput=()=>{ inp.dataset.val=""; paint(); };
  inp.onfocus=paint;
}

function openClass(id){
  selected=id;
  $("panel").style.display="";
  if($("panel").parentElement) $("panel").parentElement.style.gridTemplateColumns="";
  document.querySelectorAll(".row").forEach(r=>r.classList.toggle("on", +r.dataset.cid===id));
  const c=STATE.classes.find(x=>x.id===id);
  if(!c){$("panel").innerHTML='<p class="muted">Click a class.</p>';return;}
  const day=$("day").value||today();
  const sh=clsShift(c);
  let rm=STATE.rooms.find(r=>r.name===c.room_label);
  let rid=rm?rm.id:0;
  const ppl=classPeople(c.id,day);
  const why=classBlocked(c,day);
  const listed=matchListed(c);
  const team=$("team").value;
  $("panel").innerHTML=
    '<h2>Edit class</h2>'+
    '<div class="formgrid">'+
    '<label class="muted">Class #<input id="edNum" value="'+(c.class_num||"")+'"></label>'+
    '<label class="muted">Course<input id="edCourse"></label>'+
    '<label class="muted">Shift <select id="edShift"><option>A</option><option>B</option><option>C</option></select></label>'+
    '<label class="muted">Room — type to search or enter a new number<input id="edRoom" placeholder="1099-…" autocomplete="off"></label>'+
    '<div class="pick" id="edRoomList"></div>'+
    '<label class="muted">Listed instructor — type to search<input id="edListed" placeholder="Name" autocomplete="off"></label>'+
    '<div class="pick" id="edListedList"></div>'+
    '<label class="muted">Students <input id="edN" type="number" value="'+(c.n||0)+'"></label>'+
    '<button class="g" type="button" id="edSave">Save class details</button>'+
    '</div>'+
    (why.length?'<p style="color:#ffb4b4">'+why.join(" · ")+'</p>':'')+(function(){ const sib=roomShiftClasses(c.room_label,sh).filter(x=>x.id!==c.id); if(!sib.length) return ''; return '<p class="muted">Same room/shift — click to open and change room or shift:</p>'+sib.map(x=>'<button class="g" type="button" data-sib="'+x.id+'">'+x.class_num+' · '+(x.room_label||'')+' · '+clsShift(x)+'</button> ').join(''); })()+
    '<p style="margin:.75rem 0 .25rem">On podium today ('+day+')</p>'+
    '<div class="drop '+(why.length?"bad":"")+'">'+(ppl.map(s=>'<span class="chip '+(awayOn(s.id,day)?"away":"")+'">'+nm(s)+'</span>').join("")||'<span class="muted">Empty</span>')+'</div>'+
    (ppl.length?'<button class="x" type="button" id="btnClear">Remove today</button> ':'')+
    '<p style="margin:1rem 0 .3rem">Put someone on the podium</p>'+
    '<input id="pickQ" placeholder="Type a name" autocomplete="off" autocorrect="off" spellcheck="false" name="ops_pick" style="width:100%;margin-bottom:.35rem">'+
    '<div class="pick" id="pickList"></div>';
  $("edCourse").value=c.course||"";
  $("edShift").value=sh;
  $("edRoom").value=c.room_label||"";
  $("edListed").value=listed?nm(listed):(c.primary_name||"");
  if(listed) $("edListed").dataset.val=String(listed.id);
  bindFinder($("edRoom"), $("edRoomList"), STATE.rooms.map(r=>({value:r.name,label:r.name})), (v)=>{ $("edRoom").value=v; });
  bindFinder($("edListed"), $("edListedList"), staffRows(), (v,lab)=>{ $("edListed").dataset.val=v; $("edListed").value=lab.split(" · ")[0]; });
  $("edSave").onclick=async ()=>{
    let room=$("edRoom").value.trim();
    const listedId=+$("edListed").dataset.val||0;
    const listedStaff=listedId?staffById(listedId):matchListed({primary_name:$("edListed").value});
    await fetch("/api/class",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({
      id:c.id, class_num:$("edNum").value.trim(), course:$("edCourse").value.trim(),
      shift:$("edShift").value, room_label:room, primary_name:listedStaff?nm(listedStaff):$("edListed").value.trim(),
      n:+$("edN").value||0
    })});
    if(listedStaff){
      rm=STATE.rooms.find(r=>r.name===room);
      rid=rm?rm.id:0;
      await place(listedStaff.id, rid||1, true, $("edShift").value, c.id);
    } else {
      toast("Class saved");
      await load();
      openClass(c.id);
    }
  };
  function paintPick(){
    const pq=($("pickQ").value||"").toLowerCase();
    if(!pq){ $("pickList").innerHTML='<span class="muted">Type part of a name</span>'; return; }
    const list=STATE.staff.filter(s=>!(team&&s.team!==team) && !awayOn(s.id,day) && staffRows().find(r=>r.value==String(s.id)&&r.search.includes(pq))).slice(0,25);
    $("pickList").innerHTML=list.map(s=>'<div class="chip" data-pick="'+s.id+'">'+nm(s)+(s.team?" · "+s.team:"")+'</div>').join("")||'<span class="muted">No match</span>';
    $("pickList").querySelectorAll("[data-pick]").forEach(el=>el.onclick=async ()=>{
      rm=STATE.rooms.find(r=>r.name===($("edRoom").value.trim()||c.room_label));
      rid=rm?rm.id:0;
      await place(+el.dataset.pick, rid||1, true, $("edShift").value||sh, c.id);
    });
  }
  paintPick();
  $("pickQ").oninput=paintPick;
  if($("btnClear")) $("btnClear").onclick=()=>{ if(ppl[0]) place(ppl[0].id,0,false,sh,0); };
  $("panel").querySelectorAll("[data-sib]").forEach(b=>b.onclick=()=>openClass(+b.dataset.sib));
}


async function setTeam(id, team){
  await fetch("/api/staff",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({id:id,team:team||""})});
  const s=staffById(id); if(s) s.team=team||"";
}
function allTeams(){
  const base=(STATE.teams||[]).slice();
  STATE.staff.forEach(s=>{ if(s.team && base.indexOf(s.team)<0) base.push(s.team); });
  return base.filter(Boolean).sort();
}
function refreshTeamSelect(){
  const keep=$("team").value;
  $("team").innerHTML='<option value="">All teams</option>'+allTeams().map(function(tm){return '<option>'+tm+'</option>';}).join("");
  $("team").value=keep;
}


function renderByTeam(){
  $("hint").textContent="Create a team, then type a name to put them on it. Unassigned people sit at the top.";
  const day=$("day").value||today();
  const only=$("team").value;
  const q=($("q").value||"").toLowerCase();
  const teams=allTeams().filter(tm=>!only||tm===only);
  const none=STATE.staff.filter(s=>!s.team && (!q||nm(s).toLowerCase().includes(q)));
  let html='<div style="background:var(--card);border:1px solid var(--line);padding:.85rem;margin-bottom:.7rem">'+
    '<h3 style="color:var(--g);margin-bottom:.35rem">Create a team</h3>'+
    '<div class="formgrid">'+
    '<input id="newTeam" placeholder="Team name — Night, CTT, Support 2, ITA-2">'+
    '<button class="g" type="button" id="addTeam">Create team</button></div>'+
    '<p class="muted">Existing teams: '+(allTeams().join(", ")||"none yet")+'</p></div>';
  html+='<div style="background:var(--card);border:1px solid var(--line);padding:.85rem;margin-bottom:.7rem">'+
    '<h3 style="color:var(--g);margin-bottom:.35rem">Unassigned ('+none.length+')</h3>'+
    (none.length?none.map(s=>'<div class="row" style="grid-template-columns:1fr 10rem;cursor:default"><div><b>'+nm(s)+'</b><div class="muted">'+(s.position||"")+'</div></div><div><select data-team="'+s.id+'"><option value="">Pick team</option>'+allTeams().map(tm=>'<option value="'+tm+'">'+tm+'</option>').join("")+'</select></div></div>').join(""):'<p class="muted">Everyone is on a team.</p>')+
    '</div>';
  teams.forEach(tm=>{
    const people=STATE.staff.filter(s=>s.team===tm && (!q||nm(s).toLowerCase().includes(q)));
    const ids=new Set(people.map(s=>s.id));
    const classes=STATE.classes.filter(c=>STATE.assigns.some(a=>a.day===day && a.class_id===c.id && ids.has(a.staff_id)));
    html+='<div style="background:var(--card);border:1px solid var(--line);padding:.7rem;margin-bottom:.55rem">'+
      '<div style="display:flex;justify-content:space-between;gap:.5rem;align-items:center;flex-wrap:wrap">'+
      '<div><strong style="color:var(--g)">'+tm+'</strong> <span class="muted">'+people.length+' people · '+classes.length+' classes today</span></div>'+
      '<button class="x" type="button" data-delteam="'+tm.replace(/"/g,"")+'">Remove team</button></div>'+
      '<div class="formgrid" style="margin:.45rem 0 .3rem"><input id="addQ-'+tm.replace(/[^a-z0-9]/gi,"")+'" placeholder="Type a name to add to '+tm+'"><div class="pick" id="addL-'+tm.replace(/[^a-z0-9]/gi,"")+'"></div></div>'+
      people.map(s=>'<div class="row" style="grid-template-columns:1fr 10rem;cursor:default"><div>'+nm(s)+(awayOn(s.id,day)?' <span class="muted">(out)</span>':'')+'</div><div><select data-team="'+s.id+'"><option value="">(no team)</option>'+allTeams().map(x=>'<option value="'+x+'"'+(x===tm?' selected':'')+'>'+x+'</option>').join("")+'</select></div></div>').join("")+
      (classes.map(c=>{
        const ppl=classPeople(c.id,day);
        return '<div class="row" data-cid="'+c.id+'" style="grid-template-columns:6.2rem 2rem 1fr 8rem"><div class="cn">'+c.class_num+'</div><div>'+clsShift(c)+'</div><div>'+c.course+' · '+(c.room_label||"")+'</div><div>'+ppl.map(nm).join(", ")+'</div></div>';
      }).join("")||'<p class="muted">No podium assignments for this team today.</p>')+
    '</div>';
  });
  $("board").innerHTML=html;
  $("addTeam").onclick=async ()=>{
    const name=($("newTeam").value||"").trim();
    if(!name){ toast("Type a team name"); return; }
    await fetch("/api/team",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({name})});
    STATE.teams=STATE.teams||[]; if(STATE.teams.indexOf(name)<0) STATE.teams.push(name);
    toast("Created "+name);
    refreshTeamSelect();
    renderByTeam();
  };
  $("board").querySelectorAll("[data-team]").forEach(sel=>{
    sel.onchange=async ()=>{
      await setTeam(+sel.dataset.team, sel.value);
      toast(sel.value?"Moved to "+sel.value:"Unassigned");
      refreshTeamSelect();
      renderByTeam();
    };
  });
  $("board").querySelectorAll("[data-delteam]").forEach(b=>b.onclick=async ()=>{
    const name=b.dataset.delteam;
    if(!confirm("Remove team "+name+"? People on it become unassigned.")) return;
    await fetch("/api/team?name="+encodeURIComponent(name),{method:"DELETE"});
    STATE.teams=(STATE.teams||[]).filter(t=>t!==name);
    STATE.staff.forEach(s=>{ if(s.team===name) s.team=""; });
    toast("Removed "+name);
    refreshTeamSelect();
    renderByTeam();
  });
  teams.forEach(tm=>{
    const safe=tm.replace(/[^a-z0-9]/gi,"");
    const inp=$("addQ-"+safe), box=$("addL-"+safe);
    if(!inp||!box) return;
    bindFinder(inp, box, staffRows(), async (v)=>{
      await setTeam(+v, tm);
      toast(nm(staffById(+v))+" → "+tm);
      refreshTeamSelect();
      renderByTeam();
    });
  });
  $("board").querySelectorAll("[data-cid]").forEach(el=>el.onclick=()=>{ sort="class"; view="day"; selected=+el.dataset.cid; render(); openClass(selected); });
  $("panel").innerHTML='<p class="muted">Create the team first. Then search a name inside that team block, or use the dropdown on any person. The All teams filter at the top follows these names.</p>';
}

function renderPeople(){
  $("hint").textContent="Create a team, then assign people. The All teams menu and By team view update immediately.";
  const q=($("q").value||"").toLowerCase();
  const teams=allTeams();
  const people=STATE.staff.filter(s=>!q||nm(s).toLowerCase().includes(q)||(s.team||"").toLowerCase().includes(q));
  people.sort((a,b)=>(a.team||"zzz").localeCompare(b.team||"zzz")||nm(a).localeCompare(nm(b)));
  let html='<div style="background:var(--card);border:1px solid var(--line);padding:.8rem;margin-bottom:.7rem">'+
    '<h3 style="color:var(--g);margin-bottom:.4rem">New team</h3>'+
    '<div class="formgrid"><input id="newTeam" placeholder="Team name (example: Night, CTT, Support 2)">'+
    '<button class="g" type="button" id="addTeam">Create team</button></div>'+
    '<p class="muted">Existing: '+(teams.join(", ")||"none")+'</p></div>';
  let last="";
  people.forEach(s=>{
    if((s.team||"(no team)")!==last){ last=s.team||"(no team)"; html+='<h3 style="color:var(--g);margin:.65rem 0 .3rem">'+last+'</h3>'; }
    const opts=['<option value="">(no team)</option>'].concat(teams.map(tm=>'<option value="'+tm+'"'+(s.team===tm?' selected':'')+'>'+tm+'</option>')).join("");
    html+='<div class="row" style="grid-template-columns:minmax(0,1fr) 10rem;cursor:default"><div><b>'+nm(s)+'</b><div class="muted">'+(s.position||"")+'</div></div><div><select data-team="'+s.id+'">'+opts+'</select></div></div>';
  });
  $("board").innerHTML=html;
  $("addTeam").onclick=async ()=>{
    const name=($("newTeam").value||"").trim();
    if(!name) return;
    await fetch("/api/team",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({name})});
    STATE.teams=STATE.teams||[]; if(STATE.teams.indexOf(name)<0) STATE.teams.push(name);
    toast("Team created");
    refreshTeamSelect();
    renderPeople();
  };
  $("board").querySelectorAll("[data-team]").forEach(sel=>{
    sel.onchange=async ()=>{
      await fetch("/api/staff",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({id:+sel.dataset.team,team:sel.value})});
      const s=staffById(+sel.dataset.team); if(s) s.team=sel.value;
      toast("Assigned to "+(sel.value||"no team"));
      refreshTeamSelect();
      renderPeople();
    };
  });
  $("panel").innerHTML='<p class="muted">Create any team name you need. Assign people with the dropdown. Then use All teams or By team on the Day/Week boards.</p>';
}

function mineId(){
  const n=+(localStorage.getItem("opsMine")||0);
  return STATE.staff.some(s=>s.id===n)?n:0;
}
function setMine(id){
  localStorage.setItem("opsMine", String(id||""));
}
function iTeach(c, s, d){
  if(!s||!c) return false;
  if(STATE.assigns.some(a=>a.day===d && a.class_id===c.id && a.staff_id===s.id)) return true;
  const listed=matchListed(c);
  return !!(listed && listed.id===s.id);
}
function renderMine(){
  $("hint").textContent="Your week only. Pick your name once — this browser remembers it.";
  const days=weekDays();
  const names=["Mon","Tue","Wed","Thu","Fri"];
  const sid=mineId();
  const me=staffById(sid);
  let html='<div style="background:var(--card);border:1px solid var(--line);padding:.85rem;margin-bottom:.7rem">'+
    '<h3 style="color:var(--g);margin-bottom:.35rem">Who are you?</h3>'+
    '<input id="mineQ" placeholder="Type your last name" autocomplete="off">'+
    '<div class="pick" id="mineList"></div>'+
    (me?'<p style="margin-top:.55rem">Signed in as <b>'+nm(me)+'</b>'+(me.team?' · '+me.team:'')+(me.position?' · '+me.position:'')+' <button class="x" type="button" id="mineClear">Not me</button></p>':'<p class="muted">Search yourself. Then you only see your classes.</p>')+
    '</div>';
  if(me){
    const away=(STATE.aways||[]).filter(a=>a.staff_id===me.id);
    html+='<div style="background:var(--card);border:1px solid var(--line);padding:.75rem;margin-bottom:.7rem"><strong style="color:var(--g)">Leave and duty</strong>'+
      (away.map(a=>'<div class="muted" style="margin-top:.3rem">'+a.kind+' · '+a.start+(a.end&&a.end!==a.start?' → '+a.end:'')+(a.note?' · '+a.note:'')+'</div>').join("")||'<p class="muted">None on the books.</p>')+'</div>';
    days.forEach((d,i)=>{
      const rows=STATE.classes.filter(c=>iTeach(c,me,d));
      const out=awayOn(me.id,d);
      html+='<div style="background:var(--card);border:1px solid var(--line);padding:.7rem;margin-bottom:.45rem">'+
        '<strong style="color:var(--g)">'+names[i]+' '+d.slice(5)+'</strong>'+(out?' <span class="muted">· '+out.kind+'</span>':'')+
        (rows.map(c=>{
          return '<div class="row" data-cid="'+c.id+'" data-day="'+d+'" style="margin-top:.35rem"><div class="cn">'+c.class_num+'</div><div>'+clsShift(c)+'</div><div>'+c.course+'<div class="muted">'+(c.room_label||"")+'</div></div><div>'+(out?"Cover needed":"You")+'</div></div>';
        }).join("")||'<p class="muted" style="margin-top:.35rem">'+(out?"Out — no podium":"No class this day")+'</p>')+
      '</div>';
    });
  }
  $("board").innerHTML=html;
  if($("mineQ")) bindFinder($("mineQ"), $("mineList"), staffRows(), (v)=>{
    setMine(+v);
    toast("Saved "+nm(staffById(+v)));
    renderMine();
  });
  if($("mineClear")) $("mineClear").onclick=()=>{ setMine(0); renderMine(); };
  $("board").querySelectorAll("[data-cid]").forEach(el=>el.onclick=()=>{
    $("day").value=el.dataset.day||$("day").value;
    sort="class"; view="day"; selected=+el.dataset.cid;
    render(); openClass(selected);
  });
  $("panel").innerHTML='<p class="muted">This is the instructor view. Scheduling still happens on Classes. Click a class to open that day.</p>';
}

function renderAway(){
  $("hint").textContent="Search any instructor. Edit an existing row or add a new one.";
  const draft=window._awayDraft||{};
  $("board").innerHTML=
    '<div style="background:var(--card);border:1px solid var(--line);padding:.85rem;margin-bottom:.8rem">'+
    '<h3 style="color:var(--g);margin-bottom:.5rem" id="awTitle">'+(draft.id?"Edit leave / duty":"Add leave or duty")+'</h3><div class="formgrid">'+
    '<input id="awStaffQ" placeholder="Type instructor name" autocomplete="off"><div class="pick" id="awStaffList"></div><input type="hidden" id="awStaff">'+
    '<select id="awKind"><option value="leave">Leave</option><option value="duty">Duty</option><option value="other">Other</option></select>'+'<input id="awCustom" placeholder="If Other, type the reason">'+
    '<label class="muted">Starts <input type="date" id="awStart"></label>'+
    '<label class="muted">Ends <input type="date" id="awEnd"></label>'+
    '<input id="awNote" placeholder="Note">'+
    '<input type="hidden" id="awId">'+
    '<button class="g" type="button" id="awSave">Save and find classes to fix</button>'+
    '<button class="x" type="button" id="awCancel">Clear form</button></div></div>'+
    (STATE.aways||[]).map(a=>{
      const s=staffById(a.staff_id);
      return '<div class="row" style="cursor:default"><div class="cn">'+(a.kind||"leave")+'</div><div></div><div>'+nm(s)+'<div class="muted">'+a.start+(a.end&&a.end!==a.start?" → "+a.end:"")+(a.note?" · "+a.note:"")+'</div></div><div><button class="g" type="button" data-ed="'+a.id+'">Edit</button> <button class="x" type="button" data-del="'+a.id+'">Remove</button></div></div>';
    }).join("")||'<p class="muted">None yet.</p>';
  const s0=draft.id?staffById(draft.staff_id):null;
  $("awId").value=draft.id||"";
  $("awStaff").value=draft.staff_id||"";
  $("awStaffQ").value=s0?nm(s0):"";
  $("awKind").value=["leave","duty","other"].includes(draft.kind)?draft.kind:(draft.kind&&draft.kind!=="leave"&&draft.kind!=="duty"?"other":"leave");
  $("awCustom").value=(draft.kind&&draft.kind!=="leave"&&draft.kind!=="duty")?draft.kind:"";
  $("awStart").value=draft.start||today();
  $("awEnd").value=draft.end||draft.start||today();
  $("awNote").value=draft.note||"";
  ["awStart","awEnd"].forEach(id=>{
    const el=$(id);
    el.onclick=e=>e.stopPropagation();
    el.onmousedown=e=>e.stopPropagation();
    el.onchange=e=>{ e.stopPropagation(); window._awayDraft=window._awayDraft||{}; window._awayDraft.start=$("awStart").value; window._awayDraft.end=$("awEnd").value; };
  });
  bindFinder($("awStaffQ"), $("awStaffList"), staffRows(), (v)=>{ $("awStaff").value=v; });
  $("awSave").onclick=saveAway;
  $("awCancel").onclick=()=>{ window._awayDraft={}; renderAway(); };
  function syncCustom(){ $("awCustom").style.display=$("awKind").value==="other"?"":"none"; }
  $("awKind").onchange=syncCustom; syncCustom();
  $("board").querySelectorAll("[data-del]").forEach(b=>b.onclick=async e=>{
    e.stopPropagation();
    await fetch("/api/away?id="+b.dataset.del,{method:"DELETE"});
    toast("Removed"); window._awayDraft={}; await load();
  });
  $("board").querySelectorAll("[data-ed]").forEach(b=>b.onclick=e=>{
    e.stopPropagation();
    const a=STATE.aways.find(x=>String(x.id)===String(b.dataset.ed));
    if(!a) return;
    window._awayDraft={id:a.id,staff_id:a.staff_id,kind:a.kind,start:a.start,end:a.end,note:a.note||""};
    renderAway();
    $("board").scrollTop=0;
  });
  $("panel").innerHTML='<p class="muted">Edit changes the same row. After save, classes that listed instructor owns are flagged even if you never dropped them on the day board.</p>';
}
async function saveAway(){
  const staff_id=+$("awStaff").value||+$("awStaffQ").dataset.val||0;
  if(!staff_id){ toast("Pick an instructor from the search list"); return; }
  const start=$("awStart").value, end=$("awEnd").value||start;
  const res=await fetch("/api/away",{method:"POST",headers:{"content-type":"application/json"},
    body:JSON.stringify({id:$("awId").value||0,staff_id,kind:$("awKind").value,custom:$("awCustom")?$("awCustom").value:"",start,end,note:$("awNote").value||""})});
  const data=await res.json();
  window._awayDraft={};
  await load();
  const sid=staff_id;
  const hits=STATE.classes.filter(c=>teachersOn(c,start).some(s=>s.id===sid));
  if(hits.length){
    $("day").value=start; view="day"; sort="class"; $("fltNeed").value="away"; selected=hits[0].id;
    render(); openClass(selected);
    toast(hits.length+" class"+(hits.length>1?"es":"")+" need a replacement");
  } else toast("Saved — no listed or assigned classes in that window");
}

function cellFor(c,d){
  const who=STATE.assigns.filter(a=>a.day===d && a.class_id===c.id).map(a=>staffById(a.staff_id)).filter(Boolean);
  const listed=who.length?who:(matchListed(c)?[matchListed(c)]:[]);
  const out=listed.filter(s=>s && awayOn(s.id,d));
  if(out.length) return {txt:out.map(s=>nm(s)).join(", ")+" — away", bad:1, empty:0};
  if(listed.length) return {txt:listed.map(s=>nm(s)).join(", "), bad:0, empty:0};
  if(c.primary_name) return {txt:c.primary_name, bad:0, empty:0};
  return {txt:"—", bad:0, empty:1};
}
function renderWeekGrid(){
  $("hint").textContent="Weekdays only. No classes Saturday or Sunday — coverage is not required.";
  const days=weekDays();
  const names=["Mon","Tue","Wed","Thu","Fri"];
  const want=$("fltShift").value;
  const q=($("q").value||"").toLowerCase();
  const rows=STATE.classes.filter(c=>{
    if(want && clsShift(c)!==want) return false;
    const blob=(c.class_num+" "+c.course+" "+(c.room_label||"")+" "+(c.primary_name||"")).toLowerCase();
    return !q || blob.includes(q);
  }).sort((a,b)=>clsShift(a).localeCompare(clsShift(b))||(a.class_num||"").localeCompare(b.class_num||""));
  let html='<div style="overflow:auto"><table class="rep" style="min-width:980px"><tr><th>Class</th><th>Sh</th><th>Room</th>'+names.map((n,i)=>'<th>'+n+' '+days[i].slice(5)+'</th>').join("")+'</tr>';
  rows.forEach(c=>{
    html+='<tr><td class="cn" data-jump="'+days[0]+'|'+c.id+'" style="cursor:pointer">'+c.class_num+'<div class="muted">'+c.course+'</div></td><td>'+clsShift(c)+'</td><td>'+(c.room_label||"—")+'</td>';
    days.forEach(d=>{
      const cell=cellFor(c,d);
      const bg=cell.bad?"background:#241015;color:#ffb4b4":(cell.empty?"color:#8aa0b8":"");
      html+='<td data-jump="'+d+'|'+c.id+'" style="'+bg+';font-size:.78rem;cursor:pointer">'+cell.txt+'</td>';
    });
    html+='</tr>';
  });
  html+='</table></div>';
  const out=(STATE.aways||[]).filter(a=>days.some(d=>a.start<=d && (a.end||a.start)>=d));
  html+='<h3 style="color:var(--g);margin:1rem 0 .4rem">Out this week</h3>';
  html+=out.map(a=>'<p>'+nm(staffById(a.staff_id))+' · '+a.kind+' · '+a.start+(a.end&&a.end!==a.start?"–"+a.end:"")+(a.note?" · "+a.note:"")+'</p>').join("")||'<p class="muted">None.</p>';
  $("board").innerHTML=html;
  $("board").querySelectorAll("[data-jump]").forEach(el=>el.onclick=()=>{
    const p=el.dataset.jump.split("|");
    $("day").value=p[0]; view="day"; sort="class"; selected=+p[1]; load();
  });
  $("panel").innerHTML='<p class="muted">Click a name or class to open that day and change it.</p>';
}

function renderReport(){
  $("hint").textContent="Weekdays only for leadership. Saturday and Sunday are off — no coverage.";
  const days=weekDays();
  const names=["Mon","Tue","Wed","Thu","Fri"];
  const cur=$("day").value||today();
  const todaySt=dayStats(cur);
  let weekCover=0, weekRepl=0;
  days.forEach(d=>{ const s=dayStats(d); weekCover+=s.covered; weekRepl+=s.repl; });
  const out=STATE.aways.filter(a=>days.some(d=>a.start<=d && (a.end||a.start)>=d));
  const loadMap={};
  STATE.assigns.filter(a=>days.includes(a.day)).forEach(a=>{ loadMap[a.staff_id]=(loadMap[a.staff_id]||0)+1; });
  const loadRows=Object.keys(loadMap).map(id=>({s:staffById(+id),n:loadMap[id]})).filter(x=>x.s).sort((a,b)=>b.n-a.n);
  const replToday=STATE.classes.filter(c=>classPeople(c.id,cur).some(s=>awayOn(s.id,cur)));
  const openToday=STATE.classes.filter(c=>!classPeople(c.id,cur).length);
  $("board").innerHTML=
    '<div class="cards">'+
    '<div class="card"><b>'+todaySt.covered+'/'+todaySt.total+'</b>Covered today</div>'+
    '<div class="card"><b>'+todaySt.repl+'</b>Need replacement</div>'+
    '<div class="card"><b>'+todaySt.open+'</b>No instructor yet</div>'+
    '<div class="card"><b>'+out.length+'</b>Out this week</div>'+
    '</div>'+
    '<p style="margin-bottom:.4rem"><button class="g" type="button" onclick="window.print()">Print report</button></p>'+
    '<h3 style="color:var(--g)">This week at a glance</h3>'+
    '<table class="rep"><tr><th>Day</th><th>Covered</th><th>Open</th><th>Replace</th></tr>'+
    days.map((d,i)=>{const s=dayStats(d);return '<tr><td>'+names[i]+' '+d.slice(5)+'</td><td>'+s.covered+'/'+s.total+'</td><td>'+s.open+'</td><td>'+(s.repl||"—")+'</td></tr>';}).join("")+
    '</table>'+
    '<h3 style="color:var(--g)">Every class this week</h3>'+
    (function(){
      let h='<div style="overflow:auto"><table class="rep" style="min-width:980px"><tr><th>Class</th><th>Sh</th><th>Room</th>'+names.map((n,i)=>'<th>'+n+' '+days[i].slice(5)+'</th>').join("")+'</tr>';
      STATE.classes.slice().sort((a,b)=>clsShift(a).localeCompare(clsShift(b))||(a.class_num||"").localeCompare(b.class_num||"")).forEach(c=>{
        h+='<tr><td>'+c.class_num+'</td><td>'+clsShift(c)+'</td><td>'+(c.room_label||"—")+'</td>';
        days.forEach(d=>{ const cell=cellFor(c,d); h+='<td data-jump="'+d+'|'+c.id+'" style="cursor:pointer;font-size:.75rem;'+(cell.bad?"color:#ffb4b4":cell.empty?"color:#8aa0b8":"")+'">'+cell.txt+'</td>'; });
        h+='</tr>';
      });
      return h+'</table></div>';
    })()+
    '<h3 style="color:var(--g);margin-top:.8rem">Replace today</h3>'+
    (replToday.map(c=>'<div class="row bad" data-cid="'+c.id+'"><div class="cn">'+c.class_num+'</div><div>'+clsShift(c)+'</div><div>'+c.course+'<div class="muted">'+classBlocked(c,cur).join(" · ")+'</div></div><div>Fix</div></div>').join("")||'<p class="muted">None.</p>')+
    '<h3 style="color:var(--g);margin-top:.8rem">Still open today</h3>'+
    (openToday.slice(0,20).map(c=>'<div class="row" data-cid="'+c.id+'"><div class="cn">'+c.class_num+'</div><div>'+clsShift(c)+'</div><div>'+c.course+' · '+(c.room_label||"")+'</div><div class="muted">'+(c.primary_name||"")+'</div></div>').join("")||'<p class="muted">All have a name or none assigned yet.</p>')+
    '<h3 style="color:var(--g);margin-top:.8rem">Out this week</h3>'+
    (out.map(a=>'<p>'+nm(staffById(a.staff_id))+' · '+a.kind+' · '+a.start+(a.end&&a.end!==a.start?"–"+a.end:"")+'</p>').join("")||'<p class="muted">None.</p>')+
    '<h3 style="color:var(--g);margin-top:.8rem">Instructor load this week</h3>'+
    '<table class="rep"><tr><th>Name</th><th>Team</th><th>Days on podium</th></tr>'+
    loadRows.slice(0,25).map(x=>'<tr><td>'+nm(x.s)+'</td><td>'+(x.s.team||"")+'</td><td>'+x.n+'</td></tr>').join("")+
    '</table>';
  $("board").querySelectorAll("[data-open]").forEach(el=>el.onclick=()=>{ $("day").value=el.dataset.open; view="day"; sort="class"; load(); });
  $("board").querySelectorAll("[data-cid]").forEach(el=>el.onclick=()=>{ view="day"; sort="class"; selected=+el.dataset.cid; load(); });
  $("board").querySelectorAll("[data-jump]").forEach(el=>el.onclick=()=>{ const p=el.dataset.jump.split("|"); $("day").value=p[0]; view="day"; sort="class"; selected=+p[1]; load(); });
  $("panel").innerHTML='<p class="muted">This is what management needs: coverage, holes, who is out, and who is carrying the load. Click any class or day to fix it.</p>';
}
function render(){
  $("vDay").className=view==="day"?"g":"x";
  $("vWeek").className=view==="week"?"g":"x";
  $("vRep").className=view==="report"?"g":"x";
  $("byRoom").className=sort==="room"?"g":"x";
  if($("byClass")) $("byClass").className=(view==="day"&&sort==="class")?"g":"x";
  $("byAway").className=sort==="away"?"g":"x";
  if($("byPeople")) $("byPeople").className=sort==="people"?"g":"x";
  if($("byTeam")) $("byTeam").className=sort==="teams"?"g":"x";
  if($("byMine")) $("byMine").className=sort==="mine"?"g":"x";
  paintStrip();
  paintFixbar();
  const hideSide = view==="week" || view==="report" || sort==="away" || sort==="people" || sort==="mine";
  $("panel").parentElement.style.gridTemplateColumns = hideSide ? "1fr" : "";
  $("panel").style.display = hideSide ? "none" : "";
  const q=($("q").value||"").toLowerCase();
  const want=$("fltShift").value;
  const need=$("fltNeed").value;
  const day=$("day").value||today();
  if(view==="report"){ renderReport(); return; }
  if(sort==="away"){ renderAway(); return; }
  if(sort==="people"){ renderPeople(); return; }
  if(sort==="teams"){ renderByTeam(); return; }
  if(sort==="mine"){ renderMine(); return; }
  if(view==="week"){ renderWeekGrid(); return; }
  if(isWeekend(day)){
    $("hint").textContent="No classes on Saturday or Sunday. Coverage is not required.";
    $("board").innerHTML='<p class="muted">Weekend — schoolhouse is dark. Use the Mon–Fri strip above.</p>';
    return;
  }
  $("hint").textContent="Click a class. Click a name on the right to put them on the podium.";
  if(sort==="room"){
    $("board").innerHTML='<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:.5rem">'+STATE.rooms.map(rm=>{
      const cls=STATE.classes.filter(c=>c.room_label===rm.name);
      return '<div><strong style="color:var(--g)">'+rm.name+'</strong>'+["A","B","C"].map(sh=>{
        const here=cls.filter(c=>clsShift(c)===sh);
        if(want && sh!==want) return "";
        const ppl=STATE.assigns.filter(a=>a.room_id===rm.id && String(a.shift||"A")===sh).map(a=>staffById(a.staff_id)).filter(Boolean);
        const bad=ppl.length>1||here.length>1||ppl.some(s=>awayOn(s.id,day));
        return '<div class="drop '+(bad?"bad":"")+'" data-cid="'+(here[0]?here[0].id:0)+'"><b>'+sh+'</b> '+(here.map(c=>c.class_num).join(", ")||"")+'<div>'+ppl.map(s=>nm(s)).join(", ")+'</div></div>';
      }).join("")+'</div>';
    }).join("")+'</div>';
    $("board").querySelectorAll("[data-cid]").forEach(el=>el.onclick=()=>{ if(+el.dataset.cid){ sort="class"; selected=+el.dataset.cid; render(); openClass(selected);} });
    return;
  }
  let rows=STATE.classes.filter(c=>{
    const sh=clsShift(c), ppl=classPeople(c.id,day), why=classBlocked(c,day), repl=ppl.some(s=>awayOn(s.id,day));
    if(want && sh!==want) return false;
    if(need==="open" && ppl.length) return false;
    if(need==="issue" && !why.length) return false;
    if(need==="away" && !repl) return false;
    const blob=(c.class_num+" "+c.course+" "+(c.primary_name||"")+" "+(c.room_label||"")+" "+ppl.map(nm).join(" ")).toLowerCase();
    return !q || blob.includes(q);
  });
  rows.sort((a,b)=>{
    const ar=teachersOn(a,day).some(s=>awayOn(s.id,day))?0:1;
    const br=teachersOn(b,day).some(s=>awayOn(s.id,day))?0:1;
    if(ar!==br) return ar-br;
    return (classPeople(a.id,day).length?1:0)-(classPeople(b.id,day).length?1:0) || clsShift(a).localeCompare(clsShift(b)) || (a.class_num||"").localeCompare(b.class_num||"");
  });
  $("board").innerHTML=rows.map(c=>{
    const ppl=classPeople(c.id,day), why=classBlocked(c,day);
    return '<div class="row '+(why.length?"bad":"")+(selected===c.id?" on":"")+'" data-cid="'+c.id+'"><div class="cn">'+c.class_num+'</div><div>'+clsShift(c)+'</div><div>'+c.course+'<div class="muted">'+(c.room_label||"")+(why[0]?" · "+why[0]:"")+'</div></div><div>'+(ppl.map(s=>nm(s)+(awayOn(s.id,day)?" (out)":"")).join("<br>")||'<span class="muted">Open</span>')+'</div></div>';
  }).join("")||'<p class="muted">Nothing matches.</p>';
  $("board").querySelectorAll("[data-cid]").forEach(el=>el.onclick=()=>openClass(+el.dataset.cid));
  if(selected) openClass(selected);
}
$("vDay").onclick=()=>{view="day";sort="class";load();};
$("vWeek").onclick=()=>{view="week";load();};
$("vRep").onclick=()=>{view="report";load();};
$("byRoom").onclick=()=>{sort="room";view="day";render();};
$("byClass").onclick=()=>{sort="class";view="day";render();};
$("byAway").onclick=()=>{sort="away";render();};
$("byPeople").onclick=()=>{sort="people";render();};
$("byTeam").onclick=()=>{sort="teams";render();};
$("byMine").onclick=()=>{sort="mine";load();};
$("day").onchange=()=>{ $("day").value=workday($("day").value); load(); };
$("team").onchange=$("q").oninput=$("fltShift").onchange=$("fltNeed").onchange=render;
lockInput($("q"));
load();
</script></body></html>`;
}
