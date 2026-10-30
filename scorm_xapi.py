"""SCORM 1.2, SCORM 2004 (4th Edition), xAPI 1.0.3 statement export,
packages for Novak LMS™ (works with any SCORM-compatible LMS).
"""
import io
import json
import uuid
import zipfile
from datetime import datetime, timezone
from xml.sax.saxutils import escape

COURSE_CATALOG = {
    "ITSUP": {
        "code": "ITSUP",
        "title": "IT Support (CompTIA A+ 220-1201 & 220-1202)",
        "cert": "CompTIA A+ Core 1 (220-1201) & Core 2 (220-1202)",
        "chapters": 13,
        "lessons": 58,
    },
    "NETOPS": {
        "code": "NETOPS",
        "title": "Basic Networking (CompTIA Network+ N10-009)",
        "cert": "CompTIA Network+ (N10-009)",
        "chapters": 7,
        "lessons": 33,
    },
    "CLIENT": {
        "code": "CLIENT",
        "title": "Operating Systems (CompTIA Tech+ FC0-U71 & Core 2)",
        "cert": "CompTIA Tech+ (FC0-U71) / Operating Systems",
        "chapters": 6,
        "lessons": 24,
    },
    "SEC": {
        "code": "SEC",
        "title": "Cybersecurity",
        "cert": "Foundational cybersecurity practice comparable to Security+ (SY0-701). Not an official exam.",
        "chapters": 10,
        "lessons": 40,
    },
}


SCORM_DRIVER_JS = r"""/**
 * Novak LMS™ Dual-Standard SCORM 1.2 + SCORM 2004 (4th Edition) Runtime Driver
 * Supports:
 *   - SCORM 1.2 (window.API: LMSInitialize, LMSGetValue, LMSSetValue, LMSCommit, LMSFinish)
 *   - SCORM 2004 4th Ed (window.API_1484_11: Initialize, GetValue, SetValue, Commit, Terminate)
 *   - PostMessage Bridge (NOVAK_LMS_SCORM_EVENT) from embedded Novak LMS lessons, labs, and assessments
 */
(function (global) {
  "use strict";

  var startTimeMs = Date.now();
  var scormVersion = null;
  var api12 = null;
  var api2004 = null;
  var initialized = false;

  function findAPI12(win) {
    var attempts = 0;
    while (win && !win.API && win.parent && win.parent !== win && attempts < 15) {
      attempts++;
      win = win.parent;
    }
    return (win && win.API) ? win.API : null;
  }

  function findAPI2004(win) {
    var attempts = 0;
    while (win && !win.API_1484_11 && win.parent && win.parent !== win && attempts < 15) {
      attempts++;
      win = win.parent;
    }
    return (win && win.API_1484_11) ? win.API_1484_11 : null;
  }

  function formatScorm12Time(ms) {
    var totalSec = Math.max(0, Math.floor(ms / 1000));
    var hrs = String(Math.floor(totalSec / 3600)).padStart(4, "0");
    var mins = String(Math.floor((totalSec % 3600) / 60)).padStart(2, "0");
    var secs = String(totalSec % 60).padStart(2, "0");
    return hrs + ":" + mins + ":" + secs + ".00";
  }

  function formatScorm2004Time(ms) {
    var totalSec = Math.max(0, Math.floor(ms / 1000));
    var hrs = Math.floor(totalSec / 3600);
    var mins = Math.floor((totalSec % 3600) / 60);
    var secs = totalSec % 60;
    return "PT" + hrs + "H" + mins + "M" + secs + "S";
  }

  var NovakScormDriver = {
    init: function () {
      if (initialized) return true;
      try {
        api2004 = findAPI2004(window) || (window.opener ? findAPI2004(window.opener) : null);
        if (api2004 && typeof api2004.Initialize === "function") {
          scormVersion = "2004";
          api2004.Initialize("");
          api2004.SetValue("cmi.completion_status", "incomplete");
          api2004.SetValue("cmi.score.min", "0");
          api2004.SetValue("cmi.score.max", "100");
          api2004.Commit("");
          initialized = true;
          return true;
        }
        api12 = findAPI12(window) || (window.opener ? findAPI12(window.opener) : null);
        if (api12 && typeof api12.LMSInitialize === "function") {
          scormVersion = "1.2";
          api12.LMSInitialize("");
          var st = api12.LMSGetValue("cmi.core.lesson_status");
          if (!st || st === "not attempted") {
            api12.LMSSetValue("cmi.core.lesson_status", "incomplete");
          }
          api12.LMSSetValue("cmi.core.score.min", "0");
          api12.LMSSetValue("cmi.core.score.max", "100");
          api12.LMSCommit("");
          initialized = true;
          return true;
        }
      } catch (e) {
        console.warn("NovakScormDriver init standalone mode:", e);
      }
      scormVersion = "standalone";
      initialized = true;
      return false;
    },

    reportProgress: function (payload) {
      if (!initialized) this.init();
      payload = payload || {};
      var rawScore = typeof payload.score === "number" ? Math.max(0, Math.min(100, Math.round(payload.score))) : null;
      var status = payload.status || "completed"; // passed | completed | incomplete | failed
      var elapsedMs = Date.now() - startTimeMs;

      try {
        if (scormVersion === "2004" && api2004) {
          if (rawScore !== null) {
            api2004.SetValue("cmi.score.raw", String(rawScore));
            api2004.SetValue("cmi.score.scaled", String((rawScore / 100).toFixed(2)));
          }
          var comp = (status === "passed" || status === "completed") ? "completed" : "incomplete";
          var succ = status === "passed" ? "passed" : (status === "failed" ? "failed" : "unknown");
          api2004.SetValue("cmi.completion_status", comp);
          if (succ !== "unknown") {
            api2004.SetValue("cmi.success_status", succ);
          }
          if (payload.location) {
            api2004.SetValue("cmi.location", String(payload.location).slice(0, 250));
          }
          api2004.SetValue("cmi.session_time", formatScorm2004Time(elapsedMs));
          api2004.Commit("");
        } else if (scormVersion === "1.2" && api12) {
          if (rawScore !== null) {
            api12.LMSSetValue("cmi.core.score.raw", String(rawScore));
          }
          var st12 = (status === "passed" || status === "completed" || status === "failed") ? status : "incomplete";
          api12.LMSSetValue("cmi.core.lesson_status", st12);
          if (payload.location) {
            api12.LMSSetValue("cmi.core.lesson_location", String(payload.location).slice(0, 250));
          }
          api12.LMSSetValue("cmi.core.session_time", formatScorm12Time(elapsedMs));
          api12.LMSCommit("");
        }
      } catch (e) {
        console.warn("NovakScormDriver reportProgress error:", e);
      }

      var badge = document.getElementById("scormStatusBadge");
      if (badge) {
        badge.textContent = "SCORM Synced: " + status.toUpperCase() + (rawScore !== null ? " (" + rawScore + "%)" : "");
      }
      return true;
    },

    finish: function () {
      var elapsedMs = Date.now() - startTimeMs;
      try {
        if (scormVersion === "2004" && api2004) {
          api2004.SetValue("cmi.session_time", formatScorm2004Time(elapsedMs));
          api2004.Commit("");
          api2004.Terminate("");
        } else if (scormVersion === "1.2" && api12) {
          api12.LMSSetValue("cmi.core.session_time", formatScorm12Time(elapsedMs));
          api12.LMSCommit("");
          api12.LMSFinish("");
        }
      } catch (e) {}
      initialized = false;
    }
  };

  window.addEventListener("message", function (ev) {
    var d = ev && ev.data;
    if (!d || typeof d !== "object") return;
    if (d.type === "NOVAK_LMS_SCORM_EVENT") {
      NovakScormDriver.reportProgress(d);
    }
  });

  window.addEventListener("beforeunload", function () {
    NovakScormDriver.finish();
  });

  global.NovakScormDriver = NovakScormDriver;
})(window);
"""


def build_scorm_package_zip(course_code="NETOPS", version="1.2", base_url="https://novak-lms.onrender.com", modules_by_course=None):
    """Generate an in-memory SCORM 1.2 or SCORM 2004 4th Edition .zip package for ITSUP, NETOPS, CLIENT, or ALL."""
    code = (course_code or "NETOPS").upper().strip()
    if code.endswith(".ZIP"):
        code = code[:-4]
    if code not in ("ITSUP", "NETOPS", "CLIENT", "SEC", "ALL"):
        return None, None, None

    ver = "2004" if "2004" in str(version) else "1.2"
    target_codes = ["ITSUP", "NETOPS", "CLIENT", "SEC"] if code == "ALL" else [code]
    primary_meta = COURSE_CATALOG.get(code, {
        "code": "ALL",
        "title": "Novak LMS™ Complete Course Suite (IT Support, Basic Networking, Operating Systems, and Cybersecurity)",
        "cert": "CompTIA A+ (220-1201/1202), Network+ (N10-009), Tech+ (FC0-U71)",
        "chapters": 26,
        "lessons": 115,
    })

    items_xml = []
    for c_code in target_codes:
        c_info = COURSE_CATALOG[c_code]
        ch_list = (modules_by_course or {}).get(c_code) or [
            (idx, f"{c_info['title'].split(' (')[0]} Chapter {idx}") for idx in range(1, c_info["chapters"] + 1)
        ]
        sub_items = []
        for ch_order, ch_title in ch_list:
            sub_items.append(
                f'        <item identifier="ITEM-{c_code}-CH{ch_order}" identifierref="RES-SCO-1" isvisible="true">\n'
                f'          <title>{escape(f"Ch {ch_order}: {ch_title}")}</title>\n'
                f'        </item>'
            )
        items_xml.append(
            f'      <item identifier="ITEM-{c_code}" identifierref="RES-SCO-1" isvisible="true">\n'
            f'        <title>{escape(c_info["title"])}</title>\n'
            + "\n".join(sub_items) + "\n"
            f'      </item>'
        )

    if ver == "2004":
        manifest_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="NOVAK-LMS-{code}-SCORM2004" version="1.0"
          xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
          xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_v1p3"
          xmlns:adlseq="http://www.adlnet.org/xsd/adlseq_v1p3"
          xmlns:adlnav="http://www.adlnet.org/xsd/adlnav_v1p3"
          xmlns:imsss="http://www.imsglobal.org/xsd/imsss">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>2004 4th Edition</schemaversion>
  </metadata>
  <organizations default="ORG-NOVAK-{code}">
    <organization identifier="ORG-NOVAK-{code}">
      <title>{escape(primary_meta["title"])}</title>
{chr(10).join(items_xml)}
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES-SCO-1" type="webcontent" adlcp:scormType="sco" href="index.html">
      <file href="index.html"/>
      <file href="scorm_driver.js"/>
      <file href="package_metadata.json"/>
    </resource>
  </resources>
</manifest>
"""
    else:
        manifest_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="NOVAK-LMS-{code}-SCORM12" version="1.2"
          xmlns="http://www.imsproject.org/xsd/imscp_rootv1p1p2"
          xmlns:adlcp="http://www.adlnet.org/xsd/adlcp_rootv1p2">
  <metadata>
    <schema>ADL SCORM</schema>
    <schemaversion>1.2</schemaversion>
  </metadata>
  <organizations default="ORG-NOVAK-{code}">
    <organization identifier="ORG-NOVAK-{code}">
      <title>{escape(primary_meta["title"])}</title>
{chr(10).join(items_xml)}
    </organization>
  </organizations>
  <resources>
    <resource identifier="RES-SCO-1" type="webcontent" adlcp:scormtype="sco" href="index.html">
      <file href="index.html"/>
      <file href="scorm_driver.js"/>
      <file href="package_metadata.json"/>
    </resource>
  </resources>
</manifest>
"""

    launch_url = f"{base_url.rstrip('/')}/demo/student?scorm=1&course={code}"
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(primary_meta["title"])} — Novak LMS™ SCORM {ver} package</title>
  <script src="scorm_driver.js"></script>
  <style>
    html, body {{ margin: 0; padding: 0; height: 100%; font-family: system-ui, -apple-system, sans-serif; background: #0b1324; color: #f8fafc; display: flex; flex-direction: column; }}
    .scorm-bar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 8px 16px; background: #0f172a; border-bottom: 1px solid rgba(56, 189, 248, 0.3); font-size: 13px; }}
    .scorm-badge {{ background: rgba(56, 189, 248, 0.16); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 3px 10px; border-radius: 999px; font-weight: 600; }}
    .scorm-btn {{ background: #d4b46a; color: #0b1324; border: none; padding: 5px 12px; border-radius: 6px; font-weight: 700; cursor: pointer; text-decoration: none; }}
    iframe {{ flex: 1; width: 100%; border: 0; background: #ffffff; }}
  </style>
</head>
<body onload="NovakScormDriver.init()">
  <div class="scorm-bar">
    <div>
      <strong>Novak LMS™ SCORM {ver}</strong> · {escape(primary_meta["title"])}
    </div>
    <div style="display:flex;align-items:center;gap:8px">
      <span id="scormStatusBadge" class="scorm-badge">SCORM {ver} Initialized</span>
      <button type="button" class="scorm-btn" onclick="NovakScormDriver.reportProgress({{status:'passed',score:100,location:'{code}-COMPLETE'}})">Sync Completion to LMS</button>
    </div>
  </div>
  <iframe id="novakScoFrame" src="{escape(launch_url)}" title="{escape(primary_meta["title"])}" allow="clipboard-read; clipboard-write"></iframe>
</body>
</html>
"""

    package_metadata = {
        "schema": "Novak LMS course package metadata v1",
        "scorm_version": f"SCORM {ver}",
        "xapi_profile": "xAPI 1.0.3 statement export",
        "lti_advantage": "1EdTech LTI 1.3 + NRPS + AGS 2.0",
        "course_code": code,
        "course_title": primary_meta["title"],
        "certification_alignment": primary_meta["cert"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "telemetry_capabilities": [
            "5-Path Adaptive Learning Modality Tracking (R0 Standard, R1 Plain English, R2 Analogy, R3 Visual Map, R4 Interactive Try-It)",
            "Per-Section Time-to-Mastery (median_seconds_to_resolve & mean_attempts_to_resolve)",
            "114 Browser-Native Hands-On Labs (8 Ubuntu 24.04 GNOME GUI + Bash Split-View, 8 Windows 11 GUI, 32 Real WebAssembly Linux VMs, 19 Cisco IOS Switch/Router CLI)",
            "Diagnose -> Fix -> Verify Engineering Process Grading",
            "100% Browser-Local Helix Gaze-Assisted Intervention Telemetry (Zero Video Transmitted)",
        ],
    }

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("imsmanifest.xml", manifest_xml.strip() + "\n")
        zf.writestr("index.html", index_html.strip() + "\n")
        zf.writestr("scorm_driver.js", SCORM_DRIVER_JS.strip() + "\n")
        zf.writestr("package_metadata.json", json.dumps(package_metadata, indent=2) + "\n")

    fname = f"novak-lms-{code.lower()}-scorm-{ver.replace('.', '_')}.zip"
    return buf.getvalue(), "application/zip", fname


def build_xapi_statements(app=None, limit=50):
    """Build xAPI 1.0.3-shaped statements from Novak LMS ladder telemetry (read-only export; not a cmi5 AU/LRS)."""
    statements = []
    now_iso = datetime.now(timezone.utc).isoformat()

    if app is not None:
        try:
            from mastery.ladder import LadderEvent, LadderState
            states = {}
            for s in LadderState.query.limit(200).all():
                states[(s.user_id, s.lesson_label, s.section_id)] = s

            events = LadderEvent.query.order_by(LadderEvent.id.desc()).limit(limit).all()
            for ev in events:
                st = states.get((ev.user_id, ev.lesson_label, ev.section_id))
                elapsed_sec = None
                if st and st.created_at and ev.created_at and ev.created_at >= st.created_at:
                    elapsed_sec = max(1, int(round((ev.created_at - st.created_at).total_seconds())))

                if ev.kind == "resolved" or (ev.kind == "check" and ev.correct):
                    verb = {
                        "id": "http://adlnet.gov/expapi/verbs/passed",
                        "display": {"en-US": "passed"},
                    }
                    result = {
                        "completion": True,
                        "success": True,
                        "score": {"scaled": 1.0, "raw": 100, "min": 0, "max": 100},
                    }
                    if elapsed_sec is not None:
                        result["duration"] = f"PT{elapsed_sec}S"
                elif ev.kind == "rung":
                    verb = {
                        "id": "http://adlnet.gov/expapi/verbs/experienced",
                        "display": {"en-US": "experienced learning modality"},
                    }
                    result = {"completion": False}
                else:
                    verb = {
                        "id": "http://adlnet.gov/expapi/verbs/interacted",
                        "display": {"en-US": "interacted"},
                    }
                    result = {
                        "completion": bool(ev.correct),
                        "success": bool(ev.correct) if ev.correct is not None else False,
                    }

                ts = ev.created_at.replace(tzinfo=timezone.utc).isoformat() if ev.created_at else now_iso
                statements.append({
                    "id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"https://novakornothing.com/xapi/ladder-event/{ev.id}")),
                    "version": "1.0.3",
                    "timestamp": ts,
                    "actor": {
                        "objectType": "Agent",
                        "account": {
                            "homePage": "https://novakornothing.com",
                            "name": f"learner-{ev.user_id}",
                        },
                    },
                    "verb": verb,
                    "object": {
                        "objectType": "Activity",
                        "id": f"https://novakornothing.com/activities/lesson/{ev.lesson_label}/section/{ev.section_id}",
                        "definition": {
                            "name": {"en-US": f"Lesson {ev.lesson_label} · Concept Section {ev.section_id}"},
                            "type": "http://adlnet.gov/expapi/activities/lesson",
                        },
                    },
                    "result": result,
                    "context": {
                        "platform": "Novak LMS™",
                        "extensions": {
                            "https://novakornothing.com/xapi/ext/event_kind": ev.kind,
                            "https://novakornothing.com/xapi/ext/learning_path_rung": ev.rung or "R0",
                            "https://novakornothing.com/xapi/ext/source": ev.source or "student",
                            "https://novakornothing.com/xapi/ext/helix_gaze_assisted": bool(ev.kind == "helix_offer" or ev.source == "helix"),
                            "https://novakornothing.com/xapi/ext/time_to_resolve_sec": elapsed_sec,
                        },
                    },
                })
        except Exception:
            pass

    if not statements:
        statements.append({
            "id": str(uuid.uuid4()),
            "version": "1.0.3",
            "timestamp": now_iso,
            "actor": {
                "objectType": "Agent",
                "account": {"homePage": "https://novakornothing.com", "name": "learner-demo"},
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/passed",
                "display": {"en-US": "passed"},
            },
            "object": {
                "objectType": "Activity",
                "id": "https://novakornothing.com/activities/course/NETOPS/lesson/7.1/section/sec_0",
                "definition": {
                    "name": {"en-US": "Basic Networking 7.1 · Wireless Standards & 802.11ax/be"},
                    "type": "http://adlnet.gov/expapi/activities/lesson",
                },
            },
            "result": {
                "completion": True,
                "success": True,
                "score": {"scaled": 1.0, "raw": 100, "min": 0, "max": 100},
                "duration": "PT84S",
            },
            "context": {
                "platform": "Novak LMS™",
                "extensions": {
                    "https://novakornothing.com/xapi/ext/learning_path_rung": "R2",
                    "https://novakornothing.com/xapi/ext/time_to_resolve_sec": 84,
                    "https://novakornothing.com/xapi/ext/helix_gaze_assisted": False,
                },
            },
        })

    return {
        "version": "1.0.3",
        "standard": "xAPI 1.0.3 statement export",
        "generated_at": now_iso,
        "count": len(statements),
        "statements": statements[:limit],
    }
