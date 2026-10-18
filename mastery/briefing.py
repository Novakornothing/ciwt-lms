"""Instructor co-pilot briefing (pass 12): a daily, per-class page built deterministically — no LLM — from
the mastery engine, the "Who needs me" list, Helix class reading data (consented students only), recent chapter
checks and graded tests, the decision log, lab process diagnoses and upcoming items.

Every line says where it comes from. Rules (all constants below):

* **To do today (top 3).** Candidates, each with a plain score that is shown:
  - re-teach a class-wide mix-up: 3 × students with it active (needs ≥ MC_MIN students);
  - check in with a student from Who needs me: 2 × different reasons (+2 if stuck);
  - review an objective most of the class has not mastered: 2 × students not yet mastered (needs ≥ OBJ_MIN students
    with answers and ≥ OBJ_SHARE of them below mastered);
  - revisit a section many measured students skimmed or skipped: 1 × those students (needs ≥ HELIX_MIN measured);
  - look at a chapter check / test with a low class average: 1 × attempts below LOW_SCORE;
  - talk through a lab several students struggled with: 2 × students struggling (needs ≥ 2).
  Highest score first, at most one item per kind while other kinds remain, ties by kind order then name.
* **Skimmed / skipped sections** (Helix): per lesson section, students with a measured session on that lesson who
  spent < 3 s (skimmed) or no time (skipped) there. Only students with current consent and Helix on for the class;
  demo sessions excluded. Reading data is advisory: it is not an assessment of anyone.
* **Re-teach** for a mix-up: the mix-up and the course's correction (curriculum_v2.misconceptions), the two lesson
  sections that best address it (the same excerpts the student correction uses) and the tagged question to ask the room.
* Nothing here is sent anywhere. The text export is ready to paste into an email.
"""
import csv
import time
from collections import defaultdict
from datetime import datetime, timedelta
from io import StringIO

from flask import Response, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from curriculum_v2 import misconceptions as MCS

from . import content as C
from . import policy as P
from .engine import HELIX_MIN_SESSION_MS, HELIX_SKIM_MS
from .models import utcnow

MC_MIN = 2
OBJ_MIN = 3
OBJ_SHARE = 0.5
HELIX_MIN = 2
HELIX_SHARE = 0.5
LOW_SCORE = 70
RECENT_DAYS = 7
UPCOMING_DAYS = 7
TODO_N = 3
KIND_ORDER = ['misconception', 'student', 'objective', 'lab', 'section', 'assessment']
KIND_LABEL = {'misconception': 'Re-teach', 'student': 'Check in', 'objective': 'Review', 'lab': 'Lab',
              'section': 'Reading', 'assessment': 'Results'}
HOME_TTL = 300   # seconds the instructor-home card may reuse a briefing (the page itself is always fresh)


def rank_todo(cands, n=TODO_N):
    """Top n candidates: score desc, one per kind while other kinds remain, deterministic ties."""
    order = sorted(cands, key=lambda c: (-c['score'], KIND_ORDER.index(c['kind']), c['title']))
    out, used = [], set()
    for c in order:
        if c['kind'] not in used:
            out.append(c)
            used.add(c['kind'])
        if len(out) == n:
            return out
    for c in order:
        if c not in out:
            out.append(c)
        if len(out) == n:
            break
    return out


def helix_sections(rows, cmap, d):
    """[{lesson, heading, skimmed, skipped, measured}] for sections with enough measured students."""
    measured = defaultdict(set)                       # lesson_id -> users with a usable session
    dwell = defaultdict(lambda: defaultdict(int))     # (lesson_id, user) -> heading -> ms
    ok_users = [r['user'] for r in rows if r['st'].get('helix_status') == 'ok']
    if not ok_users or getattr(d, 'HelixGazeSession', None) is None:
        return [], 0
    lids = list(cmap['lesson_by_id'])
    S, B = d.HelixGazeSession, d.HelixAoiBucket
    sessions = (S.query.filter(S.user_id.in_([u.id for u in ok_users]), S.lesson_id.in_(lids or [0]),
                               S.is_demo.is_(False)).all())
    good = {s.id: s for s in sessions if (s.total_ms or 0) >= HELIX_MIN_SESSION_MS}
    for s in good.values():
        measured[s.lesson_id].add(s.user_id)
    if good:
        for b in B.query.filter(B.session_id.in_(list(good))).all():
            if (b.aoi_kind or 'heading') == 'heading':
                dwell[(b.lesson_id, b.user_id)][(b.aoi_label or '').strip()] += b.dwell_ms or 0
    out = []
    for lid, users in measured.items():
        if len(users) < HELIX_MIN:
            continue
        les = cmap['lesson_by_id'].get(lid)
        if not les:
            continue
        for s in C.sections(les['html']):
            h = s['heading']
            skipped = sum(1 for u in users if dwell[(lid, u)].get(h, 0) == 0)
            skimmed = sum(1 for u in users if 0 < dwell[(lid, u)].get(h, 0) < HELIX_SKIM_MS)
            if (skipped + skimmed) >= max(HELIX_MIN, HELIX_SHARE * len(users)):
                out.append({'lesson_id': lid, 'module_id': les['module_id'], 'lesson': les['label'], 'lesson_title': les['title'],
                            'heading': h, 'skimmed': skimmed, 'skipped': skipped, 'measured': len(users)})
    out.sort(key=lambda x: (-(x['skimmed'] + x['skipped']), x['lesson'], x['heading']))
    return out, len(ok_users)


def objectives_not_mastered(rows, cmap):
    out = []
    for obj, o in cmap['objs'].items():
        with_ev = [r for r in rows if r['st']['states'][obj]['n_items'] > 0
                   and r['st']['decision']['rows'][obj]['state'] != 'waived']
        if len(with_ev) < OBJ_MIN:
            continue
        below = [r for r in with_ev if r['st']['decision']['rows'][obj]['state'] != 'mastered']
        if len(below) / len(with_ev) >= OBJ_SHARE:
            review = [r for r in below if r['st']['decision']['rows'][obj]['state'] == 'review']
            out.append({'obj': obj, 'text': o['text'], 'chapter': o['chapter'], 'with_evidence': len(with_ev),
                        'below': len(below), 'needs_review': len(review), 'users': [r['user'] for r in below]})
    out.sort(key=lambda x: (-x['below'] / x['with_evidence'], -x['below'], x['chapter'], x['obj']))
    return out


def class_misconceptions(rows):
    agg = {}
    for r in rows:
        for mc, mm in r['st']['misconceptions'].items():
            a = agg.setdefault(mc, {'mc': mc, 'label': mm['label'], 'obj': mm['obj'], 'students': 0, 'active': 0,
                                    'hits': 0, 'users': []})
            a['students'] += 1
            a['hits'] += mm['hits']
            if mm['active']:
                a['active'] += 1
                a['users'].append(r['user'])
    return sorted(agg.values(), key=lambda a: (-a['active'], -a['hits'], a['mc']))


def reteach_for(mc, cmap, d):
    """5-minute re-teach for one mix-up, from course content only."""
    info = MCS.MISCONCEPTIONS.get(mc)
    if not info:
        return None
    obj = info['obj']
    o = cmap['objs'].get(obj, {})
    li = cmap['obj_lesson'].get(obj)
    les = cmap['lesson_by_id'].get(li['lesson_id']) if li else None
    corr = C.build_correction(obj, o.get('text', ''), info, les, chapter_lessons=cmap['by_ch'].get(o.get('chapter'), []),
                              glossary=getattr(d, 'glossary', ()), marked=getattr(d, 'glossary_marked', ()))
    question = None
    items = {}
    pools = []
    try:
        from curriculum_v2.exam_supplement import SUPPLEMENT
        from curriculum_v2.itsup_core import EXPANSION
        pools += [SUPPLEMENT, EXPANSION]                                             # course banks (tests draw on these)
    except ImportError:
        pass
    pools += [t['qs'] for _, t in sorted(cmap.get('tests', {}).items()) if isinstance(t.get('qs'), list)]
    pools += [q.get('items') or [] for q in sorted(cmap.get('quizzes', {}).values(), key=lambda q: q['id'])]
    for pool in pools:                                                               # later pools win
        for it in pool:
            if isinstance(it, dict) and it.get('bank_id') and (it.get('type') or 'single') == 'single' and it.get('options'):
                items[it['bank_id']] = it
    for it in cmap['check_items']:                                                   # then the lesson checks win
        if it.get('bank_id'):
            items[it['bank_id']] = it
    for (bank_id, distractor), tag in MCS.TAGS.items():
        if tag == mc and bank_id in items:
            it = items[bank_id]
            question = {'text': it.get('text') or it.get('q'), 'options': list(it.get('options') or []),
                        'correct': it.get('correct'), 'distractor': distractor, 'bank_id': bank_id}
            break
    steps = [{'min': 1, 'text': f'Name the mix-up: “{info["label"]}”.'},
             {'min': 2, 'text': 'What the course teaches instead: ' + info['fix']},
             {'min': 2, 'text': 'Ask the room the question below; ask why the tempting answer is wrong.' if question
              else 'Ask two students to explain the rule back in their own words.'}]
    return {'mc': mc, 'label': info['label'], 'obj': obj, 'fix': info['fix'], 'steps': steps,
            'blocks': corr['blocks'][:2], 'question': question, 'lesson': les}


def register_briefing(app, db, ctx):
    eng, m, d = ctx.eng, ctx.m, ctx.d
    home_cache = {}

    def recent_results(section, cmap, rows, now):
        since = now - timedelta(days=RECENT_DAYS)
        uids = [r['user'].id for r in rows]
        out = []
        qids = list(cmap['quizzes'])
        by_quiz = defaultdict(list)
        for a in (d.QuizAttempt.query.filter(d.QuizAttempt.user_id.in_(uids or [0]), d.QuizAttempt.quiz_id.in_(qids or [0]),
                                             d.QuizAttempt.completed_at >= since)
                  .filter((d.QuizAttempt.section_id == section.id) | (d.QuizAttempt.section_id.is_(None))).all()):
            by_quiz[a.quiz_id].append(a)
        for qid, atts in by_quiz.items():
            sc = [a.score or 0 for a in atts]
            out.append({'kind': 'quiz', 'id': qid, 'title': cmap['quizzes'][qid]['title'], 'attempts': len(atts),
                        'students': len({a.user_id for a in atts}), 'mean': round(sum(sc) / len(sc)),
                        'low': sum(1 for s in sc if s < LOW_SCORE),
                        'url': url_for('instructor_quiz_preview', section_id=section.id, quiz_id=qid)})
        by_test = defaultdict(list)
        for a in (d.TestAttempt.query.filter(d.TestAttempt.section_id == section.id, d.TestAttempt.completed_at >= since).all()):
            by_test[a.test_id].append(a)
        for tid, atts in by_test.items():
            t = cmap['tests'].get(tid)
            sc = [a.score or 0 for a in atts]
            out.append({'kind': 'test', 'id': tid, 'title': t['title'] if t else f'Test {tid}', 'attempts': len(atts),
                        'students': len({a.user_id for a in atts}), 'mean': round(sum(sc) / len(sc)),
                        'low': sum(1 for s in sc if s < LOW_SCORE),
                        'url': url_for('instructor_test_performance', section_id=section.id, test_id=tid)})
        out.sort(key=lambda x: (x['mean'], x['title']))
        return out

    def upcoming(section, now):
        out = []
        CR = getattr(d, 'ContentRelease', None)
        if CR is not None:
            for r in (CR.query.filter(CR.section_id == section.id, CR.user_id.is_(None), CR.available_from >= now,
                                      CR.available_from <= now + timedelta(days=UPCOMING_DAYS))
                      .order_by(CR.available_from).all()):
                out.append({'when': r.available_from, 'text': f'{r.content_type.title()} {r.content_id} opens', 'kind': 'release'})
            for r in (CR.query.filter(CR.section_id == section.id, CR.user_id.is_(None), CR.available_until >= now,
                                      CR.available_until <= now + timedelta(days=UPCOMING_DAYS))
                      .order_by(CR.available_until).all()):
                out.append({'when': r.available_until, 'text': f'{r.content_type.title()} {r.content_id} closes', 'kind': 'release'})
        for ci, u in (db.session.query(m.MasteryCheckin, d.User).join(d.User, d.User.id == m.MasteryCheckin.user_id)
                      .filter(m.MasteryCheckin.section_id == section.id, m.MasteryCheckin.done_at.is_(None),
                              m.MasteryCheckin.on_date <= (now + timedelta(days=UPCOMING_DAYS)).date()).all()):
            out.append({'when': datetime.combine(ci.on_date, datetime.min.time()), 'text': f'Check-in with {u.full_name}',
                        'kind': 'checkin', 'overdue': ci.on_date < now.date(), 'user': u})
        return sorted(out, key=lambda x: x['when'])

    def build(section):
        now = utcnow()
        cmap, rows, people = ctx.needs_me(section)
        focus = [p for p in people if p['kinds'] != ['inactive']]
        mcs = class_misconceptions(rows)
        objs = objectives_not_mastered(rows, cmap)
        skims, helix_n = helix_sections(rows, cmap, d)
        results = recent_results(section, cmap, rows, now)
        labs = defaultdict(list)
        for p in focus:
            for r in p['reasons']:
                if r['kind'] == 'lab' and r.get('lab'):
                    labs[r['lab']['lab_id']].append({'user': p['user'], 'diag': r['lab']})
        log = (db.session.query(m.MasteryDecision, d.User).join(d.User, d.User.id == m.MasteryDecision.user_id)
               .filter(m.MasteryDecision.section_id == section.id, m.MasteryDecision.created_at >= now - timedelta(days=RECENT_DAYS))
               .order_by(m.MasteryDecision.created_at.desc()).all())
        log_counts = defaultdict(int)
        for e, _u in log:
            log_counts[e.action] += 1
        cands = []
        for a in mcs:
            if a['active'] >= MC_MIN:
                cands.append({'kind': 'misconception', 'score': 3 * a['active'], 'title': f'Re-teach: {a["label"]}',
                              'why': [f'{a["active"]} students have this mix-up active ({a["hits"]} picks in total) on {a["obj"]}.'],
                              'formula': f'3 × {a["active"]} students', 'mc': a['mc'], 'obj': a['obj'], 'users': a['users']})
        for p in focus[:5]:
            sc = 2 * len(p['kinds']) + (2 if 'stuck' in p['kinds'] else 0)
            cands.append({'kind': 'student', 'score': sc, 'title': f'Check in with {p["user"].full_name}',
                          'why': [r['text'] for r in p['reasons'][:3]],
                          'formula': f'2 × {len(p["kinds"])} reasons' + (' + 2 (stuck)' if 'stuck' in p['kinds'] else ''),
                          'user': p['user'], 'obj': p['top_obj']})
        for o in objs[:3]:
            cands.append({'kind': 'objective', 'score': 2 * o['below'], 'title': f'Review {o["obj"]} with the class',
                          'why': [f'{o["below"]} of {o["with_evidence"]} students with answers are not yet at mastered on “{o["text"]}”'
                                  + (f'; {o["needs_review"]} need a review.' if o['needs_review'] else '.')],
                          'formula': f'2 × {o["below"]} students', 'obj': o['obj'], 'users': o['users']})
        for lab_id, ss in labs.items():
            if len(ss) >= 2:
                cands.append({'kind': 'lab', 'score': 2 * len(ss), 'title': f'Talk through lab “{ss[0]["diag"]["title"]}”',
                              'why': [f'{len(ss)} students show ' + ', '.join(sorted({c["label"].lower() for s in ss for c in s["diag"]["concerns"]})) + '.'],
                              'formula': f'2 × {len(ss)} students', 'lab_id': lab_id})
        for s in skims[:3]:
            n = s['skimmed'] + s['skipped']
            cands.append({'kind': 'section', 'score': n, 'title': f'Revisit “{s["heading"]}” ({s["lesson"]})',
                          'why': [f'{n} of {s["measured"]} measured students skimmed or skipped it (Helix, consented students only).'],
                          'formula': f'1 × {n} students', 'section': s})
        for r in results:
            if r['low'] and r['mean'] < LOW_SCORE:
                cands.append({'kind': 'assessment', 'score': r['low'], 'title': f'Go over {r["title"]}',
                              'why': [f'Class average {r["mean"]}% over {r["attempts"]} attempts in the last {RECENT_DAYS} days; '
                                      f'{r["low"]} below {LOW_SCORE}%.'], 'formula': f'1 × {r["low"]} low attempts', 'result': r})
        lab_list = sorted(({'lab_id': k, 'title': v[0]['diag']['title'], 'students': [x['user'] for x in v],
                            'concerns': sorted({c['label'] for x in v for c in x['diag']['concerns']})}
                           for k, v in labs.items()), key=lambda x: (-len(x['students']), x['title']))
        todo = rank_todo(cands)
        reteach = [x for x in (reteach_for(a['mc'], cmap, d) for a in mcs[:3] if a['active'] >= 1) if x]
        for rt in reteach:
            rt['agg'] = next(a for a in mcs if a['mc'] == rt['mc'])
        return {'section': section, 'now': now, 'today': now.date(), 'n_students': len(rows), 'todo': todo, 'candidates': len(cands),
                'focus': focus, 'misconceptions': mcs, 'reteach': reteach, 'objectives': objs, 'skims': skims,
                'helix_n': helix_n, 'results': results, 'labs': lab_list, 'upcoming': upcoming(section, now),
                'log_counts': dict(log_counts), 'log_n': len(log), 'labs_wired': bool(getattr(d, 'lab_events', None)),
                'demo': any(r['st']['demo'] for r in rows), 'cmap': cmap}

    def as_text(b):
        s = b['section']
        L = [f'Briefing — {s.name} — {b["today"].strftime("%a %d %b %Y")}',
             f'{b["n_students"]} students. Generated by Novak Learning from class data; nothing here is a grade.', '']
        if b['demo']:
            L += ['Note: includes demo seed data (the demo accounts are not real students).', '']
        L.append('TOP 3 TODAY')
        for i, t in enumerate(b['todo'], 1):
            L.append(f'{i}. {t["title"]}  [score {t["score"]} = {t["formula"]}]')
            L += [f'   - {w}' for w in t['why']]
        if not b['todo']:
            L.append('Nothing stands out today.')
        L += ['', 'MIX-UPS TO RE-TEACH']
        for rt in b['reteach']:
            L.append(f'- {rt["label"]} ({rt["obj"]}): {rt["agg"]["active"]} students active.')
            L += [f'   {st["min"]} min: {st["text"]}' for st in rt['steps']]
            if rt['question']:
                L.append(f'   Ask: {rt["question"]["text"]}')
        if not b['reteach']:
            L.append('- None recorded.')
        L += ['', 'OBJECTIVES MOST OF THE CLASS HAS NOT MASTERED']
        L += [f'- {o["obj"]} {o["text"]}: {o["below"]} of {o["with_evidence"]} with answers' for o in b['objectives'][:8]] or ['- None.']
        L += ['', 'SKIMMED OR SKIPPED SECTIONS (Helix, consented students only)']
        L += [f'- {x["lesson"]} “{x["heading"]}”: {x["skimmed"]} skimmed, {x["skipped"]} skipped of {x["measured"]} measured'
              for x in b['skims'][:8]] or [f'- None ({b["helix_n"]} students with current Helix consent).']
        L += ['', 'LAB STRUGGLES (from lab event logs; never changes a lab score)']
        L += [f'- {x["title"]}: ' + ', '.join(u.full_name for u in x['students']) + (f' ({"; ".join(x["concerns"])})' if x['concerns'] else '')
              for x in b['labs'][:8]] or ['- None.']
        L += ['', 'WHO TO CHECK IN WITH']
        L += [f'- {p["user"].full_name}: ' + '; '.join(r['text'] for r in p['reasons'][:3]) for p in b['focus'][:8]] or ['- Nobody today.']
        L += ['', f'RECENT RESULTS (last {RECENT_DAYS} days)']
        L += [f'- {r["title"]}: average {r["mean"]}% over {r["attempts"]} attempts' for r in b['results'][:8]] or ['- None.']
        L += ['', 'UPCOMING']
        L += [f'- {u["when"].strftime("%a %d %b")}: {u["text"]}' for u in b['upcoming']] or ['- Nothing scheduled.']
        return '\n'.join(L) + '\n'

    @login_required
    def mastery_briefing(section_id):
        section = ctx.staff_section(section_id)
        b = build(section)
        home_cache[section.id] = (time.time(), b['today'], {'todo': b['todo'][:1], 'n_todo': len(b['todo']), 'demo': b['demo']})
        return render_template('mastery/briefing.html', b=b, section=section, email_text=as_text(b),
                               tomorrow=(b['today'] + timedelta(days=1)).isoformat(), kind_label=KIND_LABEL,
                               low_score=LOW_SCORE, recent_days=RECENT_DAYS)

    @login_required
    def mastery_briefing_txt(section_id):
        section = ctx.staff_section(section_id)
        b = build(section)
        d.audit('mastery_briefing_export', f'section={section.id} format=txt')
        return Response(as_text(b), mimetype='text/plain; charset=utf-8',
                        headers={'Content-Disposition': f'attachment; filename=briefing-section-{section.id}-{b["today"].isoformat()}.txt'})

    @login_required
    def mastery_briefing_csv(section_id):
        section = ctx.staff_section(section_id)
        b = build(section)
        buf = StringIO()
        w = csv.writer(buf)
        w.writerow(['part', 'rank', 'item', 'detail', 'score', 'score_formula', 'demo_data'])
        demo = int(b['demo'])
        for i, t in enumerate(b['todo'], 1):
            w.writerow(['todo', i, t['title'], ' '.join(t['why']), t['score'], t['formula'], demo])
        for i, a in enumerate(b['misconceptions'], 1):
            w.writerow(['misconception', i, a['label'], f'{a["obj"]}; {a["active"]} active of {a["students"]} students; {a["hits"]} picks', '', '', demo])
        for i, o in enumerate(b['objectives'], 1):
            w.writerow(['objective', i, o['obj'], f'{o["below"]} of {o["with_evidence"]} not mastered', '', '', demo])
        for i, x in enumerate(b['skims'], 1):
            w.writerow(['section', i, f'{x["lesson"]} {x["heading"]}', f'{x["skimmed"]} skimmed, {x["skipped"]} skipped of {x["measured"]}', '', '', demo])
        for i, p in enumerate(b['focus'], 1):
            w.writerow(['check_in', i, p['user'].full_name, '; '.join(r['text'] for r in p['reasons']), '', '', demo])
        for i, r in enumerate(b['results'], 1):
            w.writerow(['result', i, r['title'], f'average {r["mean"]}% over {r["attempts"]} attempts', '', '', demo])
        d.audit('mastery_briefing_export', f'section={section.id} format=csv')
        return Response(buf.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition': f'attachment; filename=briefing-section-{section.id}-{b["today"].isoformat()}.csv'})

    @login_required
    def mastery_briefing_assign(section_id):
        """One click: force a review on one objective for the listed students (instructor override, logged + audited)."""
        section = ctx.staff_section(section_id)
        cmap = eng.course_map(section)
        obj = (request.form.get('obj') or '').strip()
        note = (request.form.get('note') or '').strip()[:300]
        back = url_for('mastery_briefing', section_id=section.id)
        if obj not in cmap['objs'] or not note:
            flash('That review could not be assigned.', 'danger')
            return redirect(back, code=303)
        uids = {int(x) for x in (request.form.get('user_ids') or '').split(',') if x.strip().isdigit()}
        enrolled = {e.user_id for e in d.Enrollment.query.filter_by(section_id=section.id).all()}
        users = [u for u in d.User.query.filter(d.User.id.in_(list(uids & enrolled) or [0])).all() if u.role == 'student']
        now = utcnow()
        for u in users:
            for o in m.MasteryOverride.query.filter_by(section_id=section.id, user_id=u.id, target=obj, active=True).all():
                o.active, o.cleared_at, o.cleared_by = False, now, current_user.id
            db.session.add(m.MasteryOverride(section_id=section.id, user_id=u.id, target=obj, kind='force_review', note=note,
                                             created_by=current_user.id, created_at=now))
            eng.log(section.id, u.id, obj, 'override_force_review', 'instructor',
                    [f'Your instructor set “{P.OVERRIDE_KINDS["force_review"]}” on {obj}.', f'Note: {note}'], actor_id=current_user.id)
        db.session.commit()
        d.audit('mastery_briefing_assign', f'section={section.id} target={obj} students={len(users)}')
        flash(f'Review on {obj} assigned to {len(users)} student{"s" if len(users) != 1 else ""}.', 'success')
        return redirect(back, code=303)

    def home_summary(section):
        """Cached top item for the instructor home card (fresh when older than HOME_TTL or from another day)."""
        hit = home_cache.get(section.id)
        if hit and time.time() - hit[0] < HOME_TTL and hit[1] == utcnow().date():
            return hit[2]
        b = build(section)
        val = {'todo': b['todo'][:1], 'n_todo': len(b['todo']), 'demo': b['demo']}
        home_cache[section.id] = (time.time(), b['today'], val)
        return val

    for rule, ep, fn, methods in [
        ('/instructor/section/<int:section_id>/briefing', 'mastery_briefing', mastery_briefing, ['GET']),
        ('/instructor/section/<int:section_id>/briefing.txt', 'mastery_briefing_txt', mastery_briefing_txt, ['GET']),
        ('/instructor/section/<int:section_id>/briefing.csv', 'mastery_briefing_csv', mastery_briefing_csv, ['GET']),
        ('/instructor/section/<int:section_id>/briefing/assign', 'mastery_briefing_assign', mastery_briefing_assign, ['POST']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)
    return {'build': build, 'as_text': as_text, 'home_summary': home_summary}
