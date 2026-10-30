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
from . import memory as MEM
from . import model as M
from . import policy as P
from curriculum_v2 import misconceptions as MCS
from .models import utcnow

DEMO_DOMAIN = '@lms.local'          # accounts created by seed_database(); their test attempts are generated
HELIX_SKIM_MS = 3000                # a section seen for under 3 s in a measured session counts as skimmed
HELIX_REREAD_VISITS = 3             # 3+ separate visits to one section counts as re-read
HELIX_MIN_SESSION_MS = 60_000       # only sessions with at least a minute of measured reading are used
REVIEW_ITEMS = 3
TESTOUT_PER_OBJ = 2
TESTOUT_MAX = 12
TESTOUT_PASS = 80
DAILY_MIN, DAILY_MAX = 5, 10
REVIEW_MINUTES = {'review': 5, 'alt_review': 5, 'helix_offer': 5, 'misconception': 2}   # rough, not measured
CHECK_KIND = {'review': 'review_check', 'testout': 'testout', 'daily': 'daily', 'inline': 'inline'}
CHECK_SOURCE = {'review_check': 'Review check', 'testout': 'Mastery check', 'daily': 'Daily review', 'inline': 'In-lesson check'}

_lock = threading.Lock()
_course_cache = {}


def short_text(text, n=70):
    t = (text or '').strip()
    return t if len(t) <= n else t[:n - 1].rsplit(' ', 1)[0] + '…'


def misconception_summary(ev):
    """{mc_id: {obj, hits, last_hit, resolved_at, active, refs}} from tagged wrong answers. A misconception is
    resolved by a later right answer on an item that carries a tag for it (the student now avoids that trap)."""
    tagged_items = {}
    for (bank, _d), mc in MCS.TAGS.items():
        tagged_items.setdefault(bank, set()).add(mc)
    out = {}
    for obj, obs in ev.items():
        for o in sorted(obs, key=lambda x: x.get('when') or datetime.min):
            mc = o.get('mc')
            if mc:
                m = out.setdefault(mc, {'obj': obj, 'hits': 0, 'last_hit': None, 'resolved_at': None, 'refs': []})
                m['hits'] += 1
                m['last_hit'] = max(m['last_hit'] or datetime.min, o.get('when') or datetime.min)
                m['refs'].append({'source': o.get('source'), 'when': o.get('when')})
        for o in obs:
            if o.get('correct') and o.get('bank_id') in tagged_items:
                for mc in tagged_items[o['bank_id']]:
                    if mc in out and (o.get('when') or datetime.min) > (out[mc]['last_hit'] or datetime.min):
                        out[mc]['resolved_at'] = max(out[mc]['resolved_at'] or datetime.min, o['when'])
    for m in out.values():
        m['active'] = not m['resolved_at']
        m['label'] = ''
    for mc, m in out.items():
        m['label'] = MCS.MISCONCEPTIONS[mc]['label']
    return out


TYPED = ('multi', 'order', 'match')


SRC_RANK = {'check': 0, 'cert': 1, 'bank': 2, 'supplement': 2}   # least-used first, then this order
_CERT_BY_OBJ = {}


def cert_items_for(obj):
    """Certification items whose aligned objective is ``obj`` (single-answer only; typed items stay in the practice exams)."""
    if not _CERT_BY_OBJ:
        try:
            from curriculum_v2.cert.items import CERT_ITEMS
        except ImportError:
            CERT_ITEMS = []
        _CERT_BY_OBJ['_loaded'] = []
        for it in CERT_ITEMS:
            if (it.get('type') or 'single') == 'single' and it.get('obj'):
                _CERT_BY_OBJ.setdefault(it['obj'], []).append(it)
    return _CERT_BY_OBJ.get(obj, [])


def judge(q, ans):
    """(judgeable, correct) for one stored answer. Single-answer items: the answer must be one of the current
    options (an older wording cannot be judged). Typed items (pass 12, content merge: multi-select, ordering,
    matching) are stored as a JSON list and scored all-or-nothing like curriculum_v2.cert.practice.grade;
    the list must only use current options. Unanswered (None) is judgeable and wrong, as before."""
    if ans is None:
        return True, False
    t = q.get('type') or 'single'
    opts = [str(o) for o in (q.get('options') or [])]
    if t not in TYPED:
        return (ans in (q.get('options') or [])), ans == q.get('correct')
    try:
        val = json.loads(ans) if isinstance(ans, str) else ans
    except ValueError:
        return False, False
    if not isinstance(val, list) or any(str(v) not in opts for v in val):
        return False, False
    key = [str(v) for v in (q.get('correct') or [])]
    if t == 'multi':
        return True, sorted(map(str, val)) == sorted(key)
    return True, [str(v) for v in val] == key


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
            return {'enabled': True, 'testout': True, 'testout_bank': False, 'cert_items': True, 'row': None}
        return {'enabled': bool(s.enabled), 'testout': bool(s.testout), 'testout_bank': bool(s.testout_bank),
                'cert_items': s.cert_items is not False, 'row': s}

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
                if (c.variant or '').startswith('mc:'):
                    h.setdefault('mc_done', set()).add(c.variant[3:])
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
                ok_judge, right = judge(q, ans)
                if not ok_judge:
                    sources['stale'] += 1   # answered an older wording of this question: cannot be judged now
                    continue
                ev[obj].append({'kind': 'test', 'correct': right,
                                'when': a.completed_at, 'ref': q.get('bank_id') or f'test:{a.test_id}:{i}', 'source': t['title'],
                                'mc': MCS.tag_for(q, ans), 'bank_id': q.get('bank_id')})
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
                ok_judge, right = judge(q, ans)
                if not ok_judge:
                    sources['stale'] += 1
                    continue
                ev[obj].append({'kind': 'quiz', 'correct': right,
                                'when': a.completed_at, 'ref': q.get('bank_id') or f'quiz:{a.quiz_id}:{i}', 'source': qz['title'],
                                'mc': MCS.tag_for(q, ans), 'bank_id': q.get('bank_id')})
                sources['quiz'] += 1
        # the engine's own review checks and mastery checks
        for c in checks:
            if not c.completed_at or c.skipped:
                continue
            try:
                items, answers = json.loads(c.items_json or '[]'), json.loads(c.answers_json or '{}')
            except ValueError:
                continue
            kind = CHECK_KIND.get(c.kind, 'review_check')
            for i, it in enumerate(items):
                obj = it.get('obj')
                if obj not in cmap['objs']:
                    continue
                ans = answers.get(str(i))
                if ans is None and c.kind == 'inline':
                    continue          # an in-lesson check only holds the one question that was answered
                ev[obj].append({'kind': kind, 'correct': ans is not None and ans == it.get('correct'),
                                'when': c.completed_at, 'ref': it.get('bank_id', ''), 'source': CHECK_SOURCE.get(kind, 'Review check'),
                                'mc': MCS.tag_for(it, ans), 'bank_id': it.get('bank_id')})
                sources[kind] += 1
        # practice exams (pass 12, content merge): submitted attempts, items mapped to this course's objectives.
        # Account-level (not per class), so they count in every class of the course. Blank answers are skipped.
        PA, bank, grade = getattr(d, 'PracticeAttempt', None), getattr(d, 'practice_bank', None), getattr(d, 'practice_grade', None)
        if PA is not None and bank and grade:
            items = bank()
            for a in PA.query.filter(PA.user_id == user.id, PA.submitted_at.isnot(None)).all():
                try:
                    chosen, answers = json.loads(a.items or '[]'), json.loads(a.answers or '{}')
                except ValueError:
                    continue
                for i, pair in enumerate(chosen):
                    it = items.get(pair[0]) if pair else None
                    obj = (it or {}).get('obj')
                    if obj not in cmap['objs']:
                        continue
                    ans = answers.get(str(i))
                    if ans in (None, ''):
                        continue
                    ev[obj].append({'kind': 'practice', 'correct': bool(grade(it, ans)), 'when': a.submitted_at,
                                    'ref': it['id'], 'source': 'Practice exam', 'mc': MCS.tag_for(dict(it, bank_id=it['id']), ans)
                                    if (it.get('type') or 'single') == 'single' else None, 'bank_id': it['id']})
                    sources['practice'] += 1
        # Exam-Day Readiness Simulator sittings (Option B pass 5): submitted attempts, weight 0.85 (WEIGHTS['exam_sim']).
        # Each [item_id, exam_oid] maps back to its course objective (it['raw']['obj']); blank answers are skipped.
        ESA = getattr(d, 'ExamSimAttempt', None)
        if ESA is not None and bank and grade:
            items = bank()
            for a in ESA.query.filter(ESA.user_id == user.id, ESA.submitted_at.isnot(None)).all():
                try:
                    chosen, answers = json.loads(a.items or '[]'), json.loads(a.answers or '{}')
                except ValueError:
                    continue
                for i, pair in enumerate(chosen):
                    it = items.get(pair[0]) if pair else None
                    obj = ((it or {}).get('raw') or {}).get('obj') or (it or {}).get('obj')
                    if obj not in cmap['objs']:
                        continue
                    ans = answers.get(str(i))
                    if ans in (None, ''):
                        continue
                    ev[obj].append({'kind': 'exam_sim', 'correct': bool(grade(it, ans)), 'when': a.submitted_at,
                                    'ref': it['id'], 'source': 'Practice Exam', 'mc': MCS.tag_for(dict(it, bank_id=it['id']), ans)
                                    if (it.get('type') or 'single') == 'single' else None, 'bank_id': it['id']})
                    sources['exam_sim'] += 1
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
        mcs = misconception_summary(ev)
        decision = P.apply_misconceptions(decision, mcs, settings=settings, history=hist,
                                          labels={k: v['label'] for k, v in MCS.MISCONCEPTIONS.items()})
        memory = {obj: MEM.schedule(ev.get(obj, [])) for obj in cmap['objs']}
        st = {'section': section, 'user': user, 'cmap': cmap, 'settings': settings, 'overrides': overrides,
              'checks': checks, 'history': hist, 'testout_history': tout, 'evidence': ev, 'sources': sources,
              'states': states, 'helix_status': helix_status, 'helix': helix, 'decision': decision,
              'next_lesson': nxt, 'upcoming': upcoming, 'reading': reading, 'misconceptions': mcs, 'memory': memory,
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
            if r.action in ('review', 'alt_review', 'misconception', 'helix_offer', 'testout_offer', 'stuck_flag', 'struggle_offer'):
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
    def pool(self, cmap, obj, include_bank=False, include_cert=True):
        """Single-answer items for one objective, in preference order: the class's chapter-check items,
        then certification items aligned to the objective (curriculum_v2/cert, mapped to IT-/NO- objectives
        through the alignment; Pending SME review), then — if the class allows it — the X-IT bank and supplement."""
        items = [dict(it) for it in cmap['check_items'] if it.get('obj') == obj]
        if include_cert:
            items += [dict(it, src='cert', ref=it['bank_id']) for it in cert_items_for(obj)]
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
            if (not k or k in seen or not it.get('options') or (it.get('type') or 'single') != 'single'
                    or it.get('correct') not in it['options']):
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

    def pick_items(self, cmap, objs, per_obj, cap, checks, include_bank, prefer=None, include_cert=True):
        used = self._answered(checks)
        out = []
        for obj in objs:
            pool = self.pool(cmap, obj, include_bank, include_cert)
            pool.sort(key=lambda it: (0 if prefer and it['bank_id'] in prefer else 1, used.get(it['bank_id'], 0),
                                      SRC_RANK.get(it['src'], 3), it['bank_id'] or ''))
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
                     'helix_offer': 'Optional review', 'misconception': 'Fix a mix-up'}[a['type']]
            subject = MCS.MISCONCEPTIONS[a['mc']]['label'] if a.get('mc') else o['text']
            steps.append({'kind': a['type'], 'title': f"{title}: {short_text(subject, 64)}",
                          'optional': bool(a.get('offer')) or a['type'] == 'helix_offer',
                          # same estimate as the review page's eyebrow (templates/mastery/review.html)
                          'detail': f"{a['obj']} · about {REVIEW_MINUTES.get(a['type'], 5)} min · uses lesson {les.get('label', '')}"
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
                                    st['checks'], st['settings']['testout_bank'], include_cert=st['settings']['cert_items']))
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
