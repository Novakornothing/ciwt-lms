"""Evidence gathering and orchestration for the mastery engine (pass 11).

Reads existing data only (tests, chapter checks, lab completions, skills-exam stations, lesson time,
Helix buckets when consented) plus the engine's own tables. Never writes to grade tables.
"""
import json
import re
import threading
from collections import OrderedDict, defaultdict
from datetime import datetime

from sqlalchemy import func

from . import content as C
from . import model as M
from . import policy as P
from .models import utcnow

DEMO_DOMAIN = '@lms.local'          # accounts created by seed_database(); their test attempts are generated
HELIX_SKIM_MS = 3000                # a section seen for under 3 s in a measured session counts as skimmed
HELIX_REREAD_VISITS = 3             # 3+ separate visits to one section counts as re-read
HELIX_MIN_SESSION_MS = 60_000       # only sessions with at least a minute of measured reading are used
REVIEW_ITEMS = 3
TESTOUT_PER_OBJ = 2
TESTOUT_MAX = 12
TESTOUT_PASS = 80

_lock = threading.Lock()
_course_cache = {}


def short_text(text, n=70):
    t = (text or '').strip()
    return t if len(t) <= n else t[:n - 1].rsplit(' ', 1)[0] + '…'


class Engine:
    def __init__(self, db, d, m):
        self.db, self.d, self.m = db, d, m

    # ------------------------------------------------------------------ course map (cached)
    def course_code(self, section):
        course = self.db.session.get(self.d.Course, section.course_id)
        return (course.code if course else '') or ''

    def objectives(self, code):
        from curriculum_v2.objectives import objectives_for
        out = OrderedDict()
        for k, v in objectives_for(code):
            ch = v['chapter'] - 7 if code == 'CLIENT' else v['chapter']
            out[k] = {'text': v['text'], 'chapter': ch, 'bloom': v['bloom']}
        return out

    def course_map(self, section):
        d, db = self.d, self.db
        mods = d.Module.query.filter_by(course_id=section.course_id).order_by(d.Module.order).all()
        mod_ids = [mm.id for mm in mods]
        sig = db.session.query(func.count(d.Lesson.id), func.max(d.Lesson.id), func.sum(func.length(d.Lesson.content))) \
            .filter(d.Lesson.module_id.in_(mod_ids or [0])).first()
        qsig = db.session.query(func.count(d.Quiz.id), func.sum(func.length(d.Quiz.questions))) \
            .filter(d.Quiz.module_id.in_(mod_ids or [0])).first()
        key = (section.course_id, tuple(sig or ()), tuple(qsig or ()))
        with _lock:
            hit = _course_cache.get(section.course_id)
            if hit and hit['key'] == key:
                return hit
        code = self.course_code(section)
        objs = self.objectives(code)
        lessons, by_ch = [], defaultdict(list)
        for mm in mods:
            for les in d.Lesson.query.filter_by(module_id=mm.id).order_by(d.Lesson.order).all():
                row = {'id': les.id, 'module_id': mm.id, 'chapter': mm.order, 'order': les.order,
                       'title': les.title, 'label': C.lesson_label(les.title) or f'{mm.order}.{les.order}',
                       'html': les.content or '', 'minutes': les.estimated_minutes or 30}
                lessons.append(row)
                by_ch[mm.order].append(row)
        quizzes, check_items = {}, []
        for mm in mods:
            for qz in d.Quiz.query.filter_by(module_id=mm.id).order_by(d.Quiz.id).all():
                try:
                    items = json.loads(qz.questions or '[]')
                except ValueError:
                    items = []
                quizzes[qz.id] = {'id': qz.id, 'chapter': mm.order, 'module_id': mm.id, 'title': qz.title, 'items': items}
                for i, it in enumerate(items):
                    if it.get('obj'):
                        check_items.append(dict(it, src='check', ref=f'quiz:{qz.id}:{i}', chapter=mm.order))
        votes = C.tip_votes(check_items)
        obj_lesson, lesson_objs, obj_sections = {}, defaultdict(list), {}
        for obj, o in objs.items():
            mp = C.map_objective(obj, o['text'], o['chapter'], by_ch.get(o['chapter'], []), votes)
            if not mp:
                continue
            obj_lesson[obj] = {'lesson_id': mp['lesson']['id'], 'label': mp['lesson']['label'],
                               'title': mp['lesson']['title'], 'why': mp['why']}
            lesson_objs[mp['lesson']['id']].append(obj)
            obj_sections[obj] = [s['heading'] for s in C.pick_sections(o['text'], C.sections(mp['lesson']['html']))]
        # labs attached to a lesson count for the objectives mapped to that lesson
        lab_objs = defaultdict(set)
        lesson_labs = getattr(d, 'LESSON_LABS', {}) or {}
        for les in lessons:
            for lab_id in lesson_labs.get((code, les['chapter'], les['order']), []):
                for obj in lesson_objs.get(les['id'], []):
                    lab_objs[lab_id].add(obj)
        tests = {}
        for t in d.KnowledgeTest.query.filter_by(course_id=section.course_id).all():
            try:
                tests[t.id] = {'title': t.title, 'qs': json.loads(t.questions or '[]')}
            except ValueError:
                tests[t.id] = {'title': t.title, 'qs': []}
        cmap = {'key': key, 'code': code, 'objs': objs, 'lessons': lessons, 'by_ch': dict(by_ch),
                'lesson_by_id': {x['id']: x for x in lessons}, 'quizzes': quizzes, 'check_items': check_items,
                'obj_lesson': obj_lesson, 'lesson_objs': dict(lesson_objs), 'obj_sections': obj_sections,
                'lab_objs': {k: sorted(v) for k, v in lab_objs.items()}, 'tests': tests,
                'chapters': sorted({o['chapter'] for o in objs.values()}),
                'chapter_objs': {ch: [k for k, o in objs.items() if o['chapter'] == ch] for ch in {o['chapter'] for o in objs.values()}}}
        with _lock:
            _course_cache[section.course_id] = cmap
        return cmap

    # ------------------------------------------------------------------ settings / overrides / history
    def settings(self, section_id):
        s = self.m.MasterySetting.query.filter_by(section_id=section_id).first()
        if not s:
            return {'enabled': True, 'testout': True, 'testout_bank': False, 'row': None}
        return {'enabled': bool(s.enabled), 'testout': bool(s.testout), 'testout_bank': bool(s.testout_bank), 'row': s}

    def overrides(self, section_id, user_id):
        out = {}
        for o in (self.m.MasteryOverride.query.filter_by(section_id=section_id, user_id=user_id, active=True)
                  .order_by(self.m.MasteryOverride.created_at)):
            out[o.target] = {'kind': o.kind, 'note': o.note, 'at': o.created_at, 'by': o.created_by, 'id': o.id}
        return out

    def checks(self, section_id, user_id):
        return (self.m.MasteryCheck.query.filter_by(section_id=section_id, user_id=user_id)
                .order_by(self.m.MasteryCheck.started_at).all())

    def history(self, section_id, user_id, checks):
        hist, tout = defaultdict(dict), defaultdict(lambda: {'attempts': 0, 'passed': False})
        for c in checks:
            if not c.completed_at:
                continue
            if c.kind == 'review':
                h = hist[c.target]
                h['reviews_done'] = h.get('reviews_done', 0) + 1
                h['last_review_at'] = max(h.get('last_review_at') or datetime.min, c.completed_at)
            elif c.kind == 'testout':
                ch = int(c.target.split('-')[1])
                tout[ch]['attempts'] += 1
                tout[ch]['passed'] = tout[ch]['passed'] or bool(c.passed)
                tout[ch]['last'] = c
        for r in (self.m.MasteryDecision.query.filter_by(section_id=section_id, user_id=user_id, action='review_skipped')):
            h = hist[r.target]
            h['skipped_at'] = max(h.get('skipped_at') or datetime.min, r.created_at)
            h['skips'] = h.get('skips', 0) + 1
        return dict(hist), dict(tout)

    # ------------------------------------------------------------------ evidence
    def evidence(self, section, user, cmap, checks):
        d = self.d
        ev = defaultdict(list)
        sources = defaultdict(int)
        # graded knowledge tests and skills-exam stations
        for a in (d.TestAttempt.query.filter_by(user_id=user.id, section_id=section.id)
                  .filter(d.TestAttempt.completed_at.isnot(None)).all()):
            t = cmap['tests'].get(a.test_id)
            if not t:
                continue
            try:
                answers = json.loads(a.answers or '{}')
            except ValueError:
                answers = {}
            qs = t['qs']
            if d.is_practical_payload(qs):
                for i, st in enumerate(d.stations_of(qs)):
                    passed = answers.get(st.get('lab_id'), answers.get(str(i))) == 'pass'
                    for obj in cmap['lab_objs'].get(st.get('lab_id'), []):
                        ev[obj].append({'kind': 'lab', 'correct': passed, 'when': a.completed_at,
                                        'ref': st.get('lab_id'), 'source': t['title'] + ' station'})
                        sources['lab'] += 1
                continue
            for i, q in enumerate(qs):
                obj = q.get('obj')
                if obj not in cmap['objs']:
                    continue
                ans = answers.get(str(i))
                if ans is not None and ans not in (q.get('options') or []):
                    sources['stale'] += 1   # answered an older wording of this question: cannot be judged now
                    continue
                ev[obj].append({'kind': 'test', 'correct': ans is not None and ans == q.get('correct'),
                                'when': a.completed_at, 'ref': q.get('bank_id') or f'test:{a.test_id}:{i}', 'source': t['title']})
                sources['test'] += 1
        # chapter checks (ungraded quizzes), taken in this class or before classes were recorded
        qids = list(cmap['quizzes'])
        for a in (d.QuizAttempt.query.filter(d.QuizAttempt.user_id == user.id, d.QuizAttempt.quiz_id.in_(qids or [0]))
                  .filter((d.QuizAttempt.section_id == section.id) | (d.QuizAttempt.section_id.is_(None))).all()):
            qz = cmap['quizzes'].get(a.quiz_id)
            try:
                answers = json.loads(a.answers or '{}')
            except ValueError:
                answers = {}
            for i, q in enumerate(qz['items']):
                obj = q.get('obj')
                if obj not in cmap['objs']:
                    continue
                ans = answers.get(str(i))
                if ans is not None and ans not in (q.get('options') or []):
                    sources['stale'] += 1
                    continue
                ev[obj].append({'kind': 'quiz', 'correct': ans is not None and ans == q.get('correct'),
                                'when': a.completed_at, 'ref': q.get('bank_id') or f'quiz:{a.quiz_id}:{i}', 'source': qz['title']})
                sources['quiz'] += 1
        # the engine's own review checks and mastery checks
        for c in checks:
            if not c.completed_at or c.skipped:
                continue
            try:
                items, answers = json.loads(c.items_json or '[]'), json.loads(c.answers_json or '{}')
            except ValueError:
                continue
            kind = 'review_check' if c.kind == 'review' else 'testout'
            for i, it in enumerate(items):
                obj = it.get('obj')
                if obj not in cmap['objs']:
                    continue
                ans = answers.get(str(i))
                ev[obj].append({'kind': kind, 'correct': ans is not None and ans == it.get('correct'),
                                'when': c.completed_at, 'ref': it.get('bank_id', ''),
                                'source': 'Mastery check' if kind == 'testout' else 'Review check'})
                sources[kind] += 1
        # interactive lab completions (all lab objectives met)
        seen_lab = set()
        for lc in (d.LabCompletion.query.filter_by(user_id=user.id)
                   .filter((d.LabCompletion.section_id == section.id) | (d.LabCompletion.section_id.is_(None)))
                   .order_by(d.LabCompletion.completed_at.desc()).all()):
            if lc.lab_id in seen_lab or lc.test_id:
                continue
            seen_lab.add(lc.lab_id)
            for obj in cmap['lab_objs'].get(lc.lab_id, []):
                ev[obj].append({'kind': 'lab', 'correct': True, 'when': lc.completed_at, 'ref': lc.lab_id, 'source': 'Lab ' + lc.lab_id})
                sources['lab'] += 1
        # time on task (lesson study time)
        lids = list(cmap['lesson_by_id'])
        rows = (self.db.session.query(d.TimeLog.lesson_id, func.sum(d.TimeLog.seconds), func.max(d.TimeLog.ended_at))
                .filter(d.TimeLog.user_id == user.id, d.TimeLog.kind == 'study', d.TimeLog.lesson_id.in_(lids or [0]))
                .filter((d.TimeLog.section_id == section.id) | (d.TimeLog.section_id.is_(None)))
                .group_by(d.TimeLog.lesson_id).all())
        reading = {}
        for lid, secs, last in rows:
            les = cmap['lesson_by_id'].get(lid)
            reading[lid] = int(secs or 0)
            for obj in cmap['lesson_objs'].get(lid, []):
                ev[obj].append({'kind': 'reading', 'seconds': int(secs or 0), 'expected': les['minutes'] * 60,
                                'when': last, 'lesson': f"lesson {les['label']}"})
                sources['reading'] += 1
        return dict(ev), dict(sources), reading

    # ------------------------------------------------------------------ Helix (advisory only)
    def helix_state(self, section, user):
        """('ok' | 'no_consent' | 'disabled' | 'unavailable'). Consent must be current (policy version)."""
        d = self.d
        Consent = getattr(d, 'HelixConsent', None)
        if Consent is None:
            return 'unavailable'
        c = (Consent.query.filter_by(user_id=user.id, revoked_at=None).order_by(Consent.granted_at.desc()).first())
        if not c or c.policy_version != d.HELIX_POLICY_VERSION:
            return 'no_consent'
        s = d.HelixSectionSetting.query.filter_by(section_id=section.id).first()
        if s is not None and not s.enabled:
            return 'disabled'
        return 'ok'

    def helix_signals(self, section, user, cmap):
        if self.helix_state(section, user) != 'ok':
            return None
        d = self.d
        lids = list(cmap['lesson_objs'])
        sessions = (d.HelixGazeSession.query.filter(d.HelixGazeSession.user_id == user.id,
                                                    d.HelixGazeSession.lesson_id.in_(lids or [0]),
                                                    d.HelixGazeSession.is_demo.is_(False)).all())
        good = {s.id: s for s in sessions if (s.total_ms or 0) >= HELIX_MIN_SESSION_MS}
        if not good:
            return {}
        dwell = defaultdict(lambda: defaultdict(lambda: [0, 0]))
        lessons_seen = set()
        for b in d.HelixAoiBucket.query.filter(d.HelixAoiBucket.session_id.in_(list(good))).all():
            if (b.aoi_kind or 'heading') != 'heading':
                continue
            lessons_seen.add(b.lesson_id)
            acc = dwell[b.lesson_id][(b.aoi_label or '').strip()]
            acc[0] += b.dwell_ms or 0
            acc[1] += b.visits or 0
        out = {}
        for obj, info in cmap['obj_lesson'].items():
            lid = info['lesson_id']
            if lid not in lessons_seen:
                continue
            heads = cmap['obj_sections'].get(obj) or []
            skimmed = [h for h in heads if dwell[lid].get(h, [0, 0])[0] < HELIX_SKIM_MS]
            reread = [h for h in heads if dwell[lid].get(h, [0, 0])[1] >= HELIX_REREAD_VISITS]
            if skimmed or reread:
                out[obj] = {'skimmed': skimmed, 'reread': reread, 'lesson': info['label']}
        return out

    # ------------------------------------------------------------------ the whole picture for one student
    def student_state(self, section, user, log=True, cmap=None):
        cmap = cmap or self.course_map(section)
        settings = self.settings(section.id)
        overrides = self.overrides(section.id, user.id)
        checks = self.checks(section.id, user.id)
        hist, tout = self.history(section.id, user.id, checks)
        ev, sources, reading = self.evidence(section, user, cmap, checks)
        states = {obj: M.estimate(ev.get(obj, [])) for obj in cmap['objs']}
        helix_status = self.helix_state(section, user)
        helix = self.helix_signals(section, user, cmap) if helix_status == 'ok' else None
        nxt, upcoming = self.next_lesson(section, user, cmap, tout, reading)
        decision = P.decide(states, chapters={k: o['chapter'] for k, o in cmap['objs'].items()}, settings=settings,
                            overrides=overrides, history=hist, helix=helix, describe=M.describe_counts,
                            testout_history=tout, upcoming=upcoming)
        st = {'section': section, 'user': user, 'cmap': cmap, 'settings': settings, 'overrides': overrides,
              'checks': checks, 'history': hist, 'testout_history': tout, 'evidence': ev, 'sources': sources,
              'states': states, 'helix_status': helix_status, 'helix': helix, 'decision': decision,
              'next_lesson': nxt, 'upcoming': upcoming, 'reading': reading,
              'demo': (user.email or '').endswith(DEMO_DOMAIN) and sources.get('test', 0) > 0}
        if log:
            self.sync_log(st)
        return st

    def next_lesson(self, section, user, cmap, tout, reading):
        d = self.d
        released = {}
        for les in cmap['lessons']:
            mid = les['module_id']
            if mid not in released:
                released[mid] = (user.role in ('admin', 'instructor')
                                 or d.is_content_available(section.id, 'module', mid, user.id))
        passed = {ch for ch, t in tout.items() if t.get('passed')}
        order = [les for les in cmap['lessons'] if released[les['module_id']]]
        visited = [i for i, les in enumerate(order) if reading.get(les['id'])]
        start = (max(visited) + 1) if visited else 0
        nxt = None
        for les in order[start:]:
            if les['chapter'] not in passed:
                nxt = les
                break
        quiz_done = {cmap['quizzes'][a.quiz_id]['chapter'] for a in
                     d.QuizAttempt.query.filter(d.QuizAttempt.user_id == user.id,
                                                d.QuizAttempt.quiz_id.in_(list(cmap['quizzes']) or [0])).all()}
        first_ch = nxt['chapter'] if nxt else None
        upcoming = []
        if first_ch is not None:
            rel_ch = {les['chapter'] for les in order}
            upcoming = [ch for ch in cmap['chapters'] if ch >= first_ch and ch in rel_ch
                        and ch not in passed and ch not in quiz_done]
        return nxt, upcoming

    # ------------------------------------------------------------------ decision log
    @staticmethod
    def snapshot(est):
        if not est:
            return {}
        return {k: est[k] for k in ('p', 'pct', 'n_eff', 'confidence', 'status', 'n_items', 'n_correct', 'counts')}

    def sync_log(self, st):
        """Write new decisions, resolve ones that no longer apply. Idempotent per (target, action)."""
        D = self.m.MasteryDecision
        sec, user = st['section'], st['user']
        cur = OrderedDict()
        for a in st['decision']['actions']:
            cur[(a['obj'], a['type'])] = (a['source'], a['required'], a['reasons'], st['states'].get(a['obj']))
        for o in st['decision']['testout']:
            cur[(P.chapter_key(o['chapter']), 'testout_offer')] = (o['source'], False, o['reasons'], None)
        for obj in st['decision']['stuck']:
            cur[(obj, 'stuck_flag')] = ('engine', False, ['Two reviews completed and the estimate is still low.'],
                                        st['states'].get(obj))
        live = {}
        for r in D.query.filter_by(section_id=sec.id, user_id=user.id, status='active').all():
            live[(r.target, r.action)] = r
        changed = False
        now = utcnow()
        for k, (source, required, reasons, est) in cur.items():
            r = live.pop(k, None)
            if r and (r.source != source or bool(r.required) != bool(required)):
                r.status, r.resolved_at = 'resolved', now
                r = None
            if r is None:
                self.db.session.add(D(section_id=sec.id, user_id=user.id, target=k[0], action=k[1], source=source,
                                      required=bool(required), status='active', reasons_json=json.dumps(reasons),
                                      evidence_json=json.dumps(self.snapshot(est), default=str), created_at=now))
                changed = True
        for r in live.values():
            if r.action in ('review', 'alt_review', 'helix_offer', 'testout_offer', 'stuck_flag'):
                r.status, r.resolved_at = 'resolved', now
                changed = True
        if changed:
            self.db.session.commit()

    def log(self, section_id, user_id, target, action, source, reasons, est=None, actor_id=None, status='logged',
            required=False):
        D = self.m.MasteryDecision
        self.db.session.add(D(section_id=section_id, user_id=user_id, target=target, action=action, source=source,
                              required=required, status=status, reasons_json=json.dumps(reasons),
                              evidence_json=json.dumps(self.snapshot(est), default=str), actor_id=actor_id))

    # ------------------------------------------------------------------ item pools
    def pool(self, cmap, obj, include_bank=False):
        items = [dict(it) for it in cmap['check_items'] if it.get('obj') == obj]
        if include_bank:
            from curriculum_v2.exam_supplement import SUPPLEMENT
            from curriculum_v2.itsup_core import EXPANSION
            for src, bank in (('bank', EXPANSION), ('supplement', SUPPLEMENT)):
                for it in bank:
                    if it.get('obj') == obj:
                        items.append(dict(it, src=src, ref=it.get('bank_id')))
        seen, out = set(), []
        for it in items:
            k = ' '.join((it.get('text') or it.get('q') or '').lower().split())
            if not k or k in seen or not it.get('options') or it.get('correct') not in it['options']:
                continue
            seen.add(k)
            out.append({'bank_id': it.get('bank_id') or it.get('ref'), 'obj': obj, 'src': it.get('src', 'check'),
                        'text': it.get('text') or it.get('q'), 'options': list(it['options']), 'correct': it['correct']})
        return out

    @staticmethod
    def _answered(checks, kind=None):
        ids = defaultdict(int)
        for c in checks:
            if kind and c.kind != kind:
                continue
            try:
                for it in json.loads(c.items_json or '[]'):
                    ids[it.get('bank_id')] += 1
            except ValueError:
                pass
        return ids

    def pick_items(self, cmap, objs, per_obj, cap, checks, include_bank):
        used = self._answered(checks)
        out = []
        for obj in objs:
            pool = self.pool(cmap, obj, include_bank)
            pool.sort(key=lambda it: (used.get(it['bank_id'], 0), it['bank_id'] or ''))
            out.extend(pool[:per_obj])
        return out[:cap]

    # ------------------------------------------------------------------ student-facing path
    def path(self, st, url_for):
        sec = st['section']
        cmap = st['cmap']
        steps = []
        nl = st['next_lesson']
        cur_ch = nl['chapter'] if nl else max(cmap['chapters'] or [0])
        # what matters before the next lesson comes first; reviews for later chapters follow
        acts = sorted(st['decision']['actions'], key=lambda a: cmap['objs'][a['obj']]['chapter'] > cur_ch)
        for a in acts[:3]:
            o = cmap['objs'][a['obj']]
            les = cmap['obj_lesson'].get(a['obj'], {})
            title = {'review': 'Short review', 'alt_review': 'Another way to see it',
                     'helix_offer': 'Optional review'}[a['type']]
            steps.append({'kind': a['type'], 'title': f"{title}: {short_text(o['text'], 64)}",
                          'detail': f"{a['obj']} · about 5 min · uses lesson {les.get('label', '')}"
                                    + (' · required by your instructor' if a['required'] and a['source'] == 'instructor'
                                       else (' · required' if a['required'] else '')),
                          'url': url_for('mastery_review', section_id=sec.id, obj=a['obj']),
                          'required': a['required'], 'why': a['reasons'], 'source': a['source'], 'obj': a['obj']})
        if nl:
            steps.append({'kind': 'lesson', 'title': 'Next lesson', 'detail': nl['title'],
                          'url': url_for('view_lesson', section_id=sec.id, module_id=nl['module_id'], lesson_id=nl['id']),
                          'required': False, 'why': [], 'source': 'path'})
        for o in st['decision']['testout']:
            n = len(self.pick_items(cmap, cmap['chapter_objs'].get(o['chapter'], []), TESTOUT_PER_OBJ, TESTOUT_MAX,
                                    st['checks'], st['settings']['testout_bank']))
            if not n:
                continue
            steps.append({'kind': 'testout', 'title': f"Already know chapter {o['chapter']}? Take the mastery check",
                          'detail': f'{n} questions · not graded · pass to skip ahead',
                          'url': url_for('mastery_testout', section_id=sec.id, chapter=o['chapter']),
                          'required': False, 'why': o['reasons'], 'source': o['source']})
        stuck = [{'obj': ob, 'text': cmap['objs'][ob]['text']} for ob in st['decision']['stuck']]
        return {'steps': steps, 'next': steps[0] if steps else None, 'stuck': stuck,
                'enabled': st['settings']['enabled'], 'demo': st['demo']}

    def gate(self, st, lesson_chapter):
        return P.gate(st['decision'], {k: o['chapter'] for k, o in st['cmap']['objs'].items()}, lesson_chapter)
