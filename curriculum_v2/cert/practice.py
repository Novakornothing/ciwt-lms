"""Pass 11: certification-coverage page (staff) and practice-exam mode (everyone signed in).

Registered from app.py with ``register(app, db, deps)`` like curriculum_v2.materials.

Practice exams are drawn from the CIWT item bank using the committed alignment (alignment.json): a full practice
exam allocates questions to domains by the published domain weights; a domain drill draws from one domain.
Timing follows the published ratio for these exams (maximum of 90 questions in 90 minutes, i.e. one minute per
question). Scores are reported as percent correct by domain — CompTIA reports scaled scores (100–900), and a
percentage on this practice exam does not convert to one. This is practice, not an official CompTIA exam.
"""
import json
import os
import random
from datetime import timedelta

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from .exams import ALL_DOMAINS, ALL_EXAMS, ALL_OBJECTIVES, DISCLAIMER, DOMAINS, EXAMS, OBJECTIVES, label, sort_key
from .tech_plus import build_tech_pool, tech_coverage_rows

HERE = os.path.dirname(os.path.abspath(__file__))
FULL_LENGTH = 45          # questions in a full practice exam (CompTIA's maximum is 90; see EXAMS[...]['official'])
DRILL_LENGTH = 12         # questions in a domain drill
SECONDS_PER_QUESTION = 60  # 90 questions / 90 minutes in the published exam details
GRACE_SECONDS = 30         # network latency allowance after the deadline
PRACTICE_LABEL = 'Practice exam — not an official CompTIA exam'

_cache = {}


def _extra_items():
    if 'extra_items' not in _cache:
        from .bank_a1_extra import ITEMS as a1_extra
        from .bank_n_extra import ITEMS as n_extra
        items = []
        for it in list(a1_extra) + list(n_extra):
            it.setdefault('raw', it)
            items.append(it)
        _cache['extra_items'] = items
    return _cache['extra_items']


def alignment():
    if 'a' not in _cache:
        with open(os.path.join(HERE, 'alignment.json'), encoding='utf-8') as f:
            a = json.load(f)
        for it in _extra_items():
            iid = it['id']
            oids = [c for c in (it.get('cert') or []) if c in a['objectives']]
            a.setdefault('item_map', {})[iid] = oids
            for oid in oids:
                items_list = a['objectives'][oid]['items']
                if iid not in items_list:
                    items_list.append(iid)
        for ex, s in a.get('summary', {}).items():
            s['items'] = sum(len(v['items']) for oid, v in a['objectives'].items() if oid.startswith(ex + ':'))
        _cache['a'] = a
    return _cache['a']


def baseline():
    if 'b' not in _cache:
        with open(os.path.join(HERE, 'coverage_baseline.json'), encoding='utf-8') as f:
            _cache['b'] = json.load(f)
    return _cache['b']


def bank():
    """{item_id: item} for every bank item (keys included — server side only)."""
    if 'bank' not in _cache:
        from .mapping import bank_items
        from .sim_pbq import items as sim_items
        _cache['bank'] = {it['id']: it for it in bank_items()}
        for it in _extra_items():
            _cache['bank'][it['id']] = it
        # Option B pass 4: interactive simulation PBQs (exam simulator only; not in the alignment pools)
        _cache['bank'].update({it['id']: it for it in sim_items()})
    return _cache['bank']


def pool(exam, domain=None):
    """{objective_id: [item ids]} for one exam (optionally one domain), from the committed alignment."""
    if exam == 'T':
        tpool = build_tech_pool(bank())
        return {oid: ids for oid, ids in tpool.items()
                if ids and (not domain or ALL_OBJECTIVES[oid]['domain'] == domain)}
    objs = alignment()['objectives']
    out = {}
    for oid, v in objs.items():
        if not oid.startswith(exam + ':'):
            continue
        if domain and ALL_OBJECTIVES[oid]['domain'] != domain:
            continue
        ids = [i for i in v['items'] if i in bank()]
        if ids:
            out[oid] = ids
    return out


def _allocate(total, weights):
    """Largest-remainder allocation of ``total`` questions over {key: weight}."""
    s = sum(weights.values()) or 1
    raw = {k: total * w / s for k, w in weights.items()}
    alloc = {k: int(v) for k, v in raw.items()}
    for k in sorted(raw, key=lambda k: raw[k] - alloc[k], reverse=True)[:total - sum(alloc.values())]:
        alloc[k] += 1
    return alloc


def draw(exam, domain=None, n=None, rng=None):
    """Objective-weighted draw of item ids. Within a domain, objectives are visited round-robin in a random order,
    so every objective is sampled before any is sampled twice."""
    rng = rng or random.Random()
    if domain:
        plan = {domain: n or DRILL_LENGTH}
    else:
        plan = _allocate(n or FULL_LENGTH, {d: w for d, _name, w in ALL_DOMAINS[exam]})
    chosen, used = [], set()
    for dom, k in plan.items():
        objs = pool(exam, dom)
        queues = {oid: rng.sample(ids, len(ids)) for oid, ids in objs.items()}
        order = list(queues)
        rng.shuffle(order)
        picked = 0
        while picked < k and any(queues.values()):
            for oid in order:
                if picked >= k:
                    break
                while queues[oid] and queues[oid][0] in used:
                    queues[oid].pop(0)
                if queues[oid]:
                    iid = queues[oid].pop(0)
                    used.add(iid)
                    chosen.append((iid, oid))
                    picked += 1
    if not domain:
        _ensure_item_types(exam, chosen, used, rng)
    rng.shuffle(chosen)
    return chosen


def _ensure_item_types(exam, chosen, used, rng):
    """A full practice exam carries at least one item of every type its pool has (single, multi, order, match),
    the way the real exams always include performance-based items. Without this, about 1 full A+ Core 2 draw in 11
    had no ordering item (16 of 447 pool items; pass 16b). A missing type is swapped in for a single-answer item of the
    same domain, so the domain weighting and uniqueness are unchanged."""
    b = bank()
    have = {b[i]['type'] for i, _o in chosen}
    objs = pool(exam)
    for t in ('multi', 'order', 'match'):
        if t in have:
            continue
        cands = [(i, o) for o, ids in sorted(objs.items()) for i in ids if b[i]['type'] == t and i not in used]
        rng.shuffle(cands)
        for iid, oid in cands:
            dom = ALL_OBJECTIVES[oid]['domain']
            slots = [k for k, (j, o2) in enumerate(chosen) if b[j]['type'] == 'single' and ALL_OBJECTIVES[o2]['domain'] == dom]
            if slots:
                k = rng.choice(slots)
                used.discard(chosen[k][0])
                chosen[k] = (iid, oid)
                used.add(iid)
                have.add(t)
                break


def public_item(it, oid):
    """What the browser receives for one item: stem, options and type metadata. Never the key or rationale."""
    raw = it['raw']
    out = {'text': it['text'], 'options': [str(o) for o in it['options']], 'lo': label(oid), 'lo_text': ALL_OBJECTIVES[oid]['title']}
    if it['type'] != 'single':
        out['type'] = it['type']
        if it['type'] == 'multi':
            out['choose'] = int(raw.get('choose') or len(it['correct']))
        if it['type'] == 'match':
            out['prompts'] = [str(p) for p in raw.get('prompts') or []]
    return out


def grade(it, submitted):
    """True if ``submitted`` (form value) is correct. Typed items are scored all-or-nothing."""
    if submitted in (None, ''):
        return False
    if it['type'] == 'single':
        return submitted == it['correct']
    try:
        val = json.loads(submitted)
    except ValueError:
        return False
    if not isinstance(val, list):
        return False
    if it['type'] == 'multi':
        return sorted(map(str, val)) == sorted(map(str, it['correct']))
    return [str(v) for v in val] == [str(v) for v in it['correct']]


def partial(it, submitted):
    """(parts right, parts) for a typed item (sim_pbq / match / order); (int(correct), 1) for single and multi."""
    if it['type'] in ('single', 'multi'):
        return int(grade(it, submitted)), 1
    try:
        val = json.loads(submitted) if submitted else []
    except ValueError:
        val = []
    key = [str(c) for c in it['correct']]
    val = [str(v) for v in val] if isinstance(val, list) else []
    return sum(1 for k, v in zip(key, val) if k == v), len(key)


def display_answer(it, submitted):
    if submitted in (None, ''):
        return '—'
    if it['type'] == 'single':
        return submitted
    try:
        val = json.loads(submitted)
    except ValueError:
        return '—'
    if it['type'] in ('match', 'sim_pbq'):
        prompts = it['raw'].get('prompts') or []
        return '; '.join(f'{p} → {v or "—"}' for p, v in zip(prompts, val))
    if it['type'] == 'order':
        return ' → '.join(map(str, val))
    return '; '.join(map(str, val))


def display_key(it):
    c = it['correct']
    if it['type'] in ('match', 'sim_pbq'):
        return '; '.join(f'{p} → {v}' for p, v in zip(it['raw'].get('prompts') or [], c))
    if it['type'] == 'order':
        return ' → '.join(map(str, c))
    if it['type'] == 'multi':
        return '; '.join(map(str, c))
    return str(c)


def lesson_ref(ref):
    """'ITSUP 4.2' -> ('ITSUP', 4, 2)."""
    course, num = ref.split(' ')
    ch, les = num.split('.')
    return course, int(ch), int(les)


def register(app, db, deps):
    """deps: Course, Module, Lesson, ClassSection, Enrollment, utcnow, audit."""
    Course, Module, Lesson = deps['Course'], deps['Module'], deps['Lesson']
    ClassSection, Enrollment = deps['ClassSection'], deps['Enrollment']
    utcnow = deps['utcnow']
    audit = deps.get('audit') or (lambda *a, **k: None)

    class PracticeAttempt(db.Model):
        __tablename__ = 'practice_attempt'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
        exam = db.Column(db.String(4), nullable=False)
        domain = db.Column(db.String(8))            # NULL = full practice exam
        items = db.Column(db.Text, nullable=False)  # JSON [[item_id, objective_id], ...]
        started_at = db.Column(db.DateTime, nullable=False)
        deadline = db.Column(db.DateTime, nullable=False)
        submitted_at = db.Column(db.DateTime)
        answers = db.Column(db.Text)                # JSON {index: submitted value}
        correct = db.Column(db.Integer)
        total = db.Column(db.Integer)
        timed_out = db.Column(db.Boolean, default=False)

    def is_staff():
        return current_user.is_authenticated and current_user.role in ('instructor', 'admin')

    def _naive(dt):
        return dt.replace(tzinfo=None) if dt is not None and dt.tzinfo else dt

    def lesson_links(refs, limit=3):
        """Lesson URLs the current user can open: via one of their sections for that course; staff get the
        first section of the course."""
        out, seen = [], set()
        for ref in refs:
            if len(out) >= limit:
                break
            try:
                code, ch, lo = lesson_ref(ref)
            except ValueError:
                continue
            course = Course.query.filter_by(code=code).first()
            if not course:
                continue
            mod = Module.query.filter_by(course_id=course.id, order=ch).first()
            les = Lesson.query.filter_by(module_id=mod.id, order=lo).first() if mod else None
            if not les or les.id in seen:
                continue
            q = ClassSection.query.filter_by(course_id=course.id)
            if not is_staff():
                q = q.join(Enrollment, Enrollment.section_id == ClassSection.id).filter(Enrollment.user_id == current_user.id)
            sec = q.order_by(ClassSection.id).first()
            seen.add(les.id)
            out.append({'ref': ref, 'title': les.title,
                        'url': url_for('view_lesson', section_id=sec.id, module_id=mod.id, lesson_id=les.id) if sec else None})
        return out

    # ------------------------------------------------------------------------------ coverage (staff)
    @login_required
    def cert_coverage():
        if not is_staff():
            abort(403)
        a, b = alignment(), baseline()
        t_objs, t_sum, t_bef = tech_coverage_rows(bank())
        all_obj_rows = dict(a['objectives'], **t_objs)
        all_sum = dict(a['summary'], T=t_sum)
        all_bef = dict(b['summary'], T=t_bef)
        exam = request.args.get('exam') if request.args.get('exam') in ALL_EXAMS else None
        status = request.args.get('status') if request.args.get('status') in ('covered', 'partial', 'gap') else None
        rows = []
        for oid, v in all_obj_rows.items():
            o = ALL_OBJECTIVES[oid]
            if exam and o['exam'] != exam:
                continue
            if status and v['status'] != status:
                continue
            rows.append({'oid': oid, 'o': o, 'v': v, 'before': b['status'].get(oid, 'covered'), 'lessons': lesson_links(v['lessons'], limit=6)})
        rows.sort(key=lambda r: sort_key(r['oid']))
        return render_template('cert_coverage.html', rows=rows, exams=ALL_EXAMS, domains=ALL_DOMAINS, summary=all_sum,
                               before=all_bef, disclaimer=DISCLAIMER, exam=exam, status=status)

    # ------------------------------------------------------------------------------ practice exams
    @login_required
    def practice_index():
        recent = (PracticeAttempt.query.filter_by(user_id=current_user.id)
                  .order_by(PracticeAttempt.started_at.desc()).limit(10).all())
        return render_template('practice_index.html', exams=ALL_EXAMS, domains=ALL_DOMAINS, recent=recent, label=PRACTICE_LABEL,
                               disclaimer=DISCLAIMER, full_len=FULL_LENGTH, drill_len=DRILL_LENGTH,
                               pools={ex: sum(len(v) for v in pool(ex).values()) for ex in ALL_EXAMS})

    @login_required
    def practice_start():
        exam = request.form.get('exam')
        domain = request.form.get('domain') or None
        if exam not in ALL_EXAMS or (domain and domain not in {d for d, _n, _w in ALL_DOMAINS[exam]}):
            abort(400)
        chosen = draw(exam, domain)
        if not chosen:
            flash('No questions are available for that selection yet.', 'warning')
            return redirect(url_for('practice_index'))
        now = _naive(utcnow())
        att = PracticeAttempt(user_id=current_user.id, exam=exam, domain=domain, items=json.dumps(chosen), started_at=now,
                              deadline=now + timedelta(seconds=SECONDS_PER_QUESTION * len(chosen)), total=len(chosen))
        db.session.add(att)
        db.session.commit()
        audit('practice_start', f'{exam}/{domain or "full"}/{att.id}')
        return redirect(url_for('practice_take', attempt_id=att.id))

    def _own(attempt_id):
        att = db.get_or_404(PracticeAttempt, attempt_id)
        if att.user_id != current_user.id:
            abort(404)
        return att

    def _title(att):
        base = f'{ALL_EXAMS[att.exam]["name"]} ({ALL_EXAMS[att.exam]["code"]})'
        if att.domain:
            name = {d: n for d, n, _w in ALL_DOMAINS[att.exam]}[att.domain]
            return f'{base} — domain {att.domain} {name} drill'
        return f'{base} — full practice'

    @login_required
    def practice_take(attempt_id):
        att = _own(attempt_id)
        if att.submitted_at:
            return redirect(url_for('practice_result', attempt_id=att.id))
        chosen = json.loads(att.items)
        now = _naive(utcnow())
        if request.method == 'POST':
            late = now > _naive(att.deadline) + timedelta(seconds=GRACE_SECONDS)
            answers, correct = {}, 0
            for i, (iid, _oid) in enumerate(chosen):
                val = request.form.get(f'q{i}')
                if val is not None:
                    answers[str(i)] = val[:4000]
                it = bank().get(iid)
                if it and grade(it, val):
                    correct += 1
            att.answers = json.dumps(answers)
            att.correct, att.total = correct, len(chosen)
            att.submitted_at = now
            att.timed_out = late or request.form.get('timed_out') == '1'
            db.session.commit()
            audit('practice_submit', f'{att.exam}/{att.domain or "full"}/{att.id}: {correct}/{len(chosen)}')
            return redirect(url_for('practice_result', attempt_id=att.id))
        questions = [public_item(bank()[iid], oid) for iid, oid in chosen if iid in bank()]
        remaining = max(0, int((_naive(att.deadline) - now).total_seconds()))
        return render_template('practice_take.html', att=att, questions=questions, remaining=remaining,
                               title=_title(att), label=PRACTICE_LABEL)

    @login_required
    def practice_result(attempt_id):
        att = _own(attempt_id)
        if not att.submitted_at:
            return redirect(url_for('practice_take', attempt_id=att.id))
        chosen = json.loads(att.items)
        answers = json.loads(att.answers or '{}')
        a = alignment()['objectives']
        by_dom, review = {}, []
        for i, (iid, oid) in enumerate(chosen):
            it = bank().get(iid)
            if not it:
                continue
            ok = grade(it, answers.get(str(i)))
            dom = OBJECTIVES[oid]['domain']
            d = by_dom.setdefault(dom, {'correct': 0, 'total': 0, 'missed': {}})
            d['total'] += 1
            d['correct'] += int(ok)
            if not ok:
                d['missed'].setdefault(oid, 0)
                d['missed'][oid] += 1
            review.append({'n': i + 1, 'text': it['text'], 'ok': ok, 'oid': oid, 'type': it['type'],
                           'yours': display_answer(it, answers.get(str(i))), 'key': display_key(it), 'why': it['explanation']})
        names = {d: n for d, n, _w in ALL_DOMAINS[att.exam]}
        weights = {d: w for d, _n, w in ALL_DOMAINS[att.exam]}
        domains = []
        for dom in sorted(by_dom, key=lambda d: float(d)):
            d = by_dom[dom]
            missed = [{'oid': oid, 'label': label(oid), 'title': OBJECTIVES[oid]['title'], 'n': n,
                       'lessons': lesson_links(a.get(oid, {}).get('lessons', []), limit=2)}
                      for oid, n in sorted(d['missed'].items(), key=lambda kv: sort_key(kv[0]))]
            domains.append({'id': dom, 'name': names[dom], 'weight': weights[dom], 'correct': d['correct'], 'total': d['total'],
                            'pct': round(100 * d['correct'] / d['total']) if d['total'] else 0, 'missed': missed})
        pct = round(100 * (att.correct or 0) / att.total) if att.total else 0
        return render_template('practice_result.html', att=att, title=_title(att), domains=domains, review=review, pct=pct,
                               exam=ALL_EXAMS[att.exam], label=PRACTICE_LABEL, disclaimer=DISCLAIMER)

    for rule, ep, fn, methods in (
        ('/staff/cert-coverage', 'cert_coverage', cert_coverage, ['GET']),
        ('/practice', 'practice_index', practice_index, ['GET']),
        ('/practice/start', 'practice_start', practice_start, ['POST']),
        ('/practice/attempt/<int:attempt_id>', 'practice_take', practice_take, ['GET', 'POST']),
        ('/practice/attempt/<int:attempt_id>/result', 'practice_result', practice_result, ['GET']),
    ):
        app.add_url_rule(rule, ep, fn, methods=methods)
    return PracticeAttempt
