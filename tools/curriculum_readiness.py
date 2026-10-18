#!/usr/bin/env python3
"""Curriculum readiness audit for ITSUP and NETOPS (pass 13). Runs on a DB COPY only:

    DATABASE_URL=sqlite:////tmp/copy.db ./venv/bin/python tools/curriculum_readiness.py out.json [--package DIR]

Checks: every lesson renders (staff and an enrolled student); every objective has lessons, items, a lab and
glossary terms; answer keys match the delivered items; no orphaned or duplicate items; lesson plans and syllabus
match the current content and credit hours; optionally the course package regenerated from this tree matches the
document model (MANIFEST.json with per-document hashes). Writes JSON; CURRICULUM_READINESS.md summarises it.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from html import unescape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
if not os.environ.get('DATABASE_URL'):
    raise SystemExit('Set DATABASE_URL to a copy of the DB (this tool logs in and renders pages).')

import app as M  # noqa: E402
from curriculum_v2 import course_package as CP  # noqa: E402
from curriculum_v2 import documents as D  # noqa: E402
from curriculum_v2.objectives import OBJECTIVES  # noqa: E402
import interactive_labs as IL  # noqa: E402
import pilot_slice as PS  # noqa: E402
import question_bank as QB  # noqa: E402
from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload  # noqa: E402
from curriculum_v2.exam_supplement import SUPPLEMENT  # noqa: E402
from curriculum_v2.itsup_core import EXPANSION  # noqa: E402
from curriculum_v2.cert.items import CERT_ITEMS  # noqa: E402

COURSES = ('ITSUP', 'NETOPS')
PREFIX = {'ITSUP': 'IT-', 'NETOPS': 'NO-'}
BAD_RENDER = [r'\{\{', r'\{%', r'Traceback', r'\bundefined\b', r'jinja2']


def norm(s):
    return ' '.join(unescape(re.sub(r'<[^>]+>', ' ', s or '')).lower().split())


def original_pools():
    """Original course items (not certification items): chapter checks, knowledge-test pools, supplement, bank."""
    pools = {}
    for o in PS.PILOT_CHECKS:
        pools[f'ITSUP check {o}'] = PS.quiz_payload(o, '')
    for o in NETOPS_CHECKS:
        pools[f'NETOPS check {o}'] = netops_quiz_payload(o)
    for n in ('A1', 'A2', 'A3', 'N1', 'N2', 'N3'):
        pools[f'question_bank.{n}'] = getattr(QB, n)
    pools['exam_supplement'] = SUPPLEMENT
    pools['itsup_core.EXPANSION'] = EXPANSION
    return pools


def key_ok(q):
    t = q.get('type') or 'single'
    opts = q.get('options') or []
    c = q.get('correct')
    if t == 'single':
        return c in opts and len(set(map(norm, opts))) == len(opts) and len(opts) >= 2
    if t == 'multi':
        return isinstance(c, list) and c and set(c) <= set(opts) and len(c) < len(opts)
    if t in ('order', 'match'):
        return isinstance(c, list) and len(c) >= 2
    return False


def doc_hash(kind, code):
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    from build_course_package import model_sha256
    return model_sha256(D.build(kind, code))


def package_manifest(folder):
    """Compare MANIFEST.json (written by build_course_package.py) with a fresh build of each document model."""
    path = os.path.join(folder, 'MANIFEST.json')
    if not os.path.exists(path):
        return {'ok': False, 'bad': ['no MANIFEST.json; rebuild with tools/build_course_package.py']}
    man = json.load(open(path))
    bad = []
    for e in man['documents']:
        if doc_hash(e['kind'], e['course']) != e['model_sha256']:
            bad.append((e['course'], e['kind'], 'document model changed since the package was built'))
        for f in e['files']:
            if not os.path.exists(os.path.join(folder, f)):
                bad.append((f, 'missing'))
    return {'ok': not bad, 'bad': bad, 'head': man.get('git_head'), 'n': len(man['documents'])}


def run(package=''):
    app, db = M.app, M.db
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    R = {'checks': [], 'details': {}}

    def check(name, ok, detail=None, area=''):
        R['checks'].append({'area': area, 'check': name, 'ok': bool(ok), 'detail': detail})
        print(('PASS ' if ok else 'FAIL ') + f'[{area}] {name}' + ('' if ok or detail is None else f' — {str(detail)[:300]}'), flush=True)

    def login(email, pw):
        c = app.test_client()
        r = c.post('/login', data={'email': email, 'password': pw})
        assert r.status_code in (302, 303), email
        return c

    staff = login('admin@lms.local', 'admin123')
    with app.app_context():
        courses = {c.code: c for c in M.Course.query.filter(M.Course.code.in_(COURSES))}
        sections = {code: M.ClassSection.query.filter_by(course_id=c.id).order_by(M.ClassSection.id).first()
                    for code, c in courses.items()}
        eng = app.extensions['ciwt_mastery'].engine
        # ------------------------------------------------------------ 1. lessons render
        for code in COURSES:
            sec = sections[code]
            enr = M.Enrollment.query.filter_by(section_id=sec.id).first()
            stu_user = db.session.get(M.User, enr.user_id)
            stu = login(stu_user.email, 'student123')
            bad, n, short = [], 0, []
            mods = M.Module.query.filter_by(course_id=courses[code].id).order_by(M.Module.order).all()
            for mod in mods:
                for les in mod.lessons:
                    n += 1
                    for who, cl in (('staff', staff), ('student', stu)):
                        r = cl.get(f'/student/module/{sec.id}/{mod.id}/lesson/{les.id}')
                        h = r.get_data(as_text=True)
                        if r.status_code != 200:
                            bad.append((who, les.id, les.title, r.status_code))
                            continue
                        hits = [p for p in BAD_RENDER if re.search(p, h)]
                        # a bare None from a template variable (lesson tables legitimately contain the word)
                        if h.count('>None<') > (les.content or '').count('>None<'):
                            hits.append('>None< from a template variable')
                        if hits:
                            bad.append((who, les.id, les.title, hits))
                    if len(norm(les.content)) < 900:
                        short.append((les.id, les.title, len(norm(les.content))))
            R['details'][f'{code}_lessons'] = {'n': n, 'bad': bad, 'short': short}
            check(f'{code}: all {n} lessons render for staff and an enrolled student (200, no template leftovers)', not bad, bad, 'lessons')
            check(f'{code}: every lesson has substantive text (≥900 characters of prose; lab walk-throughs are shortest)', not short, short, 'lessons')
        # ------------------------------------------------------------ 2. objectives
        gl_terms = [t for t, _d in CP.GLOSSARY]
        cert_by_obj = Counter(it['obj'] for it in CERT_ITEMS)
        pools = original_pools()
        orig_by_obj = Counter(q.get('obj') for p in pools.values() for q in p if q.get('obj'))
        for code in COURSES:
            sec = sections[code]
            cmap = eng.course_map(sec)
            objs = sorted(k for k, v in OBJECTIVES.items() if v['course'] == code)
            chapters_in_lms = {m_.order for m_ in M.Module.query.filter_by(course_id=courses[code].id)}
            lab_objs = defaultdict(set)
            for lab_id, os_ in cmap['lab_objs'].items():
                for o in os_:
                    lab_objs[o].add(lab_id)
            rows, problems = [], defaultdict(list)
            for o in objs:
                ch = OBJECTIVES[o]['chapter']
                lessons = [l for l in cmap['lessons'] if o in (cmap['lesson_objs'].get(l['id']) or [])]
                checks_n = len([i for i in cmap['check_items'] if i.get('obj') == o])
                ch_labs = IL.CHAPTER_LABS.get((code, ch), [])
                text = ' '.join(norm(l['html']) for l in lessons)
                terms = [t for t in gl_terms if re.search(r'(?<![a-z0-9])' + re.escape(t.lower()) + r'(?![a-z0-9])', text)]
                row = {'obj': o, 'chapter': ch, 'in_lms': ch in chapters_in_lms, 'lessons': len(lessons), 'check_items': checks_n,
                       'original_items': orig_by_obj.get(o, 0), 'cert_items': cert_by_obj.get(o, 0),
                       'lesson_labs': sorted(lab_objs.get(o, ())), 'chapter_labs': len(ch_labs), 'glossary_terms': len(terms)}
                rows.append(row)
                if not row['in_lms']:
                    problems['chapter not in the LMS'].append(o)
                    continue
                if not lessons:
                    problems['no lesson'].append(o)
                if not (row['original_items'] or checks_n):
                    problems['no original items'].append(o)
                if not (row['lesson_labs'] or ch_labs):
                    problems['no lab'].append(o)
                if not checks_n:
                    problems['no chapter-check item'].append(o)   # pass 14
                if not terms:
                    problems['no glossary term in its lessons'].append(o)
            R['details'][f'{code}_objectives'] = rows
            for what in ('chapter not in the LMS', 'no lesson', 'no original items', 'no chapter-check item', 'no lab',
                         'no glossary term in its lessons'):
                label = {'chapter not in the LMS': 'its chapter is in the LMS', 'no lesson': 'has a lesson',
                         'no original items': 'has original (non-certification) items',
                         'no chapter-check item': 'has chapter-check items', 'no lab': 'has a lab',
                         'no glossary term in its lessons': 'has glossary terms in its lessons'}[what]
                check(f'{code}: every objective {label}',
                      not problems[what], problems[what], 'objectives')
        # ------------------------------------------------------------ 3. answer keys
        bad_keys = [(name, q.get('bank_id'), (q.get('text') or '')[:80]) for name, p in pools.items() for q in p if not key_ok(q)]
        check(f'every original item has a valid key ({sum(len(p) for p in pools.values())} items)', not bad_keys, bad_keys, 'keys')
        bad_cert = [(q['bank_id'], q.get('type')) for q in CERT_ITEMS if not key_ok(q)]
        check(f'every certification item has a valid key ({len(CERT_ITEMS)} items)', not bad_cert, bad_cert, 'keys')
        mism = []
        for code in COURSES:
            delivered = {}
            for qz in M.Quiz.query.join(M.Module).filter(M.Module.course_id == courses[code].id):
                for q in json.loads(qz.questions or '[]'):
                    if q.get('bank_id'):
                        delivered[(qz.module.order, q['bank_id'])] = q
            for key in CP.answer_keys(code):
                mt = re.match(r'Chapter (\d+) check', key['title'])
                if not mt:
                    continue
                ch = int(mt.group(1))
                for r in key['rows']:
                    q = delivered.get((ch, r['id']))
                    if q is None:
                        mism.append((code, ch, r['id'], 'in answer key but not delivered'))
                    elif q['correct'] != r['answer'] or [f'{"ABCD"[j]}. {o}' for j, o in enumerate(q['options'])] != r['options']:
                        mism.append((code, ch, r['id'], 'key or option order differs from the LMS'))
                n_del = len([k for k in delivered if k[0] == ch])
                if n_del != len(key['rows']):
                    mism.append((code, ch, f'{n_del} delivered vs {len(key["rows"])} in key'))
            for t in M.KnowledgeTest.query.filter_by(course_id=courses[code].id):
                qs = json.loads(t.questions or '[]')
                if M.is_practical_payload(qs):
                    continue
                for q in qs:
                    if not key_ok(q):
                        mism.append((code, t.title, q.get('bank_id'), 'test item key not among options'))
        check('chapter-check answer keys match the delivered LMS items (key and option order); test items keyed', not mism, mism, 'keys')
        # ------------------------------------------------------------ 4. orphans and duplicates
        by_id = defaultdict(set)
        for name, p in pools.items():
            for q in p:
                if q.get('bank_id'):
                    by_id[q['bank_id']].add(norm(q.get('text')))
        dup_ids = sorted(k for k, v in by_id.items() if len(v) > 1)
        check('no bank_id is reused for different stems across the original pools', not dup_ids, dup_ids, 'items')
        stems = defaultdict(set)
        for name, p in pools.items():
            for q in p:
                stems[norm(q.get('text'))].add(q.get('bank_id'))
        dup_stems = sorted((s[:70], sorted(map(str, v))) for s, v in stems.items() if len(v) > 1)
        check('no identical stem appears under two different bank ids', not dup_stems, dup_stems, 'items')
        orphan_obj = sorted({(q.get('bank_id'), q.get('obj')) for p in pools.values() for q in p
                             if q.get('obj') and q.get('obj') not in OBJECTIVES})
        check('every original item maps to a current objective', not orphan_obj, orphan_obj, 'items')
        no_obj = sorted({q.get('bank_id') for p in pools.values() for q in p if not q.get('obj')})
        check('every original item has an objective', not no_obj, no_obj, 'items')
        orphan_q = [qz.id for qz in M.Quiz.query.all() if not qz.module]
        check('no chapter check without a chapter', not orphan_q, orphan_q, 'items')
        # pass 14: a chapter-check rationale must explain the answer, not just point at a section
        terse = [q.get('bank_id') for name, p in pools.items() if ' check ' in name for q in p
                 if len(re.sub(r'^[\d\s./]+(overview)?\.?\s*(—|-)?\s*', '', (q.get('explanation') or q.get('study_tip') or '').strip()).split()) < 4]
        check('every chapter-check rationale explains the answer (not only a section reference)', not terse, terse, 'items')
        # ------------------------------------------------------------ 5. plans and syllabus
        plan_bad, syl_bad = [], []
        for code in COURSES:
            for mod in M.Module.query.filter_by(course_id=courses[code].id).order_by(M.Module.order):
                p = CP.lesson_plan(code, mod.order)
                if not p:
                    plan_bad.append((code, mod.order, 'no lesson plan'))
                    continue
                db_titles = [l.title for l in mod.lessons]
                if [norm(t) for t in p['lessons']] != [norm(t) for t in db_titles]:
                    plan_bad.append((code, mod.order, 'lesson list differs', p['lessons'], db_titles))
                plan_objs = [o['code'] for o in p['objectives']]
                cur = sorted(k for k, v in OBJECTIVES.items() if v['course'] == code and v['chapter'] == mod.order)
                if sorted(plan_objs) != cur:
                    plan_bad.append((code, mod.order, 'objectives differ', plan_objs, cur))
                mins = sum(l.estimated_minutes or 0 for l in mod.lessons)
                if p.get('minutes') and abs((p['minutes'] or 0) - mins) > max(30, 0.15 * mins):
                    plan_bad.append((code, mod.order, f'plan says {p["minutes"]} min, lessons total {mins} min'))
            syl = D.build('syllabus', code)
            txt = norm(json.dumps(syl['blocks'], ensure_ascii=False))
            for mod in M.Module.query.filter_by(course_id=courses[code].id):
                if norm(mod.title) not in txt:
                    syl_bad.append((code, mod.order, 'chapter title missing from syllabus', mod.title))
            cr = CP.credit_mapping(code)
            if f"{cr['contact_hours']} contact hours" not in json.dumps(syl['blocks'], ensure_ascii=False):
                syl_bad.append((code, 'contact hours not stated as computed', cr['contact_hours']))
            lms_hours = sum(l.estimated_minutes or 0 for mod in M.Module.query.filter_by(course_id=courses[code].id)
                            for l in mod.lessons) / 60
            R['details'][f'{code}_hours'] = {'credit_mapping': cr, 'lms_lesson_hours': round(lms_hours, 1)}
            if lms_hours > cr['contact_hours'] + cr['out_of_class_hours']:
                syl_bad.append((code, f'LMS lesson time {lms_hours:.0f} h exceeds contact + out-of-class hours'))
        check('lesson plans match the current chapters (lessons, objectives, minutes)', not plan_bad, plan_bad, 'documents')
        check('syllabus lists every current chapter and states the computed contact hours', not syl_bad, syl_bad, 'documents')
        # ------------------------------------------------------------ 6. package
        if package:
            man = package_manifest(package)
            check('course package regenerated from this tree; every document hash matches its MANIFEST entry',
                  man['ok'], man['bad'], 'package')
            R['details']['package'] = man
    R['summary'] = {'passed': sum(c['ok'] for c in R['checks']), 'total': len(R['checks'])}
    return R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--package', default='')
    a = ap.parse_args()
    R = run(a.package)
    with open(a.out, 'w') as f:
        json.dump(R, f, indent=1, default=str)
    print(f"{R['summary']['passed']}/{R['summary']['total']} checks passed")
    return 0 if R['summary']['passed'] == R['summary']['total'] else 1


if __name__ == '__main__':
    sys.exit(main())
