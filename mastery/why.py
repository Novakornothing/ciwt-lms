"""'Why this student is struggling': one synthesis per student combining the explanation ladder, lab process flags
and (only with consent) Helix attention signals, plus one recommended next action. Read-only; never graded."""
from collections import Counter

from flask import url_for

from curriculum_v2 import ladder as LD


def _model(db, name):
    return next((mp.class_ for mp in db.Model.registry.mappers if mp.class_.__name__ == name), None)


def helix_signals(db, user_id, section_id):
    Consent, Sess = _model(db, 'HelixConsent'), _model(db, 'HelixGazeSession')
    if not Consent or not Consent.query.filter_by(user_id=user_id, revoked_at=None).first():
        return {'consented': False, 'pills': ['Helix: Not opted in'], 'text': None}
    rows = Sess.query.filter_by(user_id=user_id, section_id=section_id).all() if Sess else []
    if not rows:
        return {'consented': True, 'pills': ['Helix: Opted in, no sessions yet'], 'text': None}
    low = sum(1 for s in rows if (s.total_ms or 0) > 60000 and (s.attentive_ms or 0) < 0.5 * (s.total_ms or 1))
    long = sum(1 for s in rows if (s.total_ms or 0) > 20 * 60000)
    uncal = sum(1 for s in rows if (s.mode or 'gaze') == 'gaze' and not (s.calibration_points or 0))
    pills = [f'Helix: {len(rows)} session{"s" if len(rows) != 1 else ""}']
    pills += [f'Low attention in {low}'] if low else []
    pills += [f'High dwell (20+ min) in {long}'] if long else []
    pills += [f'Uncalibrated in {uncal} (treat as rough)'] if uncal else []
    text = (f'Helix shows low on-page attention in {low} of {len(rows)} sessions' if low else
            f'Helix shows long re-reading in {long} session{"s" if long != 1 else ""}' if long else None)
    return {'consented': True, 'pills': pills, 'text': text}


def lab_flags(app, section, user_id, limit=8):
    labs = app.extensions.get('ciwt_lab_progress')
    if not labs:
        return [], Counter()
    flags, count = [], Counter()
    rows = labs.LabProgress.query.filter_by(user_id=user_id).order_by(labs.LabProgress.updated_at.desc()).limit(limit).all()
    for r in rows:
        try:
            ana = labs.lab_analysis_for(user_id, r.lab_id, section)
        except Exception:
            continue
        for p in (ana or {}).get('concerns', []):
            count[p['label']] += 1
            flags.append({'lab_id': r.lab_id, 'label': p['label'], 'ref': p.get('ref'),
                          'url': url_for('instructor_lab_student', section_id=section.id, user_id=user_id, lab_id=r.lab_id)})
    return flags, count


def exam_sim_signal(db, section, user):
    """Latest submitted Exam-Day Simulator sitting in this class (Option B pass 5), or None."""
    ESA = _model(db, 'ExamSimAttempt')
    if ESA is None:
        return None
    try:
        att = (ESA.query.filter(ESA.user_id == user.id, ESA.section_id == section.id, ESA.submitted_at.isnot(None),
                                ESA.mode != 'drill').order_by(ESA.submitted_at.desc()).first())
    except Exception:
        db.session.rollback()
        return None
    if not att:
        return None
    import json as _json
    from curriculum_v2.cert import exam_sim as ES
    from curriculum_v2.cert.exams import ALL_DOMAINS as DOMAINS, ALL_EXAMS as EXAMS
    names = {dd: n for dd, n, _w in DOMAINS[att.exam]}
    doms = []
    for dom, ct in (_json.loads(att.domains or '{}') or {}).items():
        if isinstance(ct, list) and len(ct) == 2 and ct[1]:
            doms.append((round(100 * ct[0] / ct[1]), dom))
    weak = sorted(x for x in doms if x[0] < ES.DOMAIN_FLOOR)
    worst = weak[0] if weak else None
    code = EXAMS[att.exam]['code']
    label = {'ready': 'Voucher ready', 'borderline': 'Borderline'}.get(att.badge, 'Needs remediation')
    pill = f'Exam Sim ({code}): {att.score}/900 · {label}' + (f' (weak: {worst[1]} {names.get(worst[1], "")})' if worst else '')
    flagged = att.badge == 'remediate' or bool(weak)
    return {'att': att, 'pill': pill, 'flagged': flagged, 'worst': worst and {'domain': worst[1], 'name': names.get(worst[1], ''),
                                                                              'pct': worst[0]},
            'code': code, 'label': label}


def why(app, db, section, user):
    lad = app.extensions['ciwt_mastery'].ladder
    c = lad.clicked(user.id, section.id)
    exhausted = [s for s in c['sections'] if s['exhausted'] and not s['rung']]
    repeated = [s for s in c['sections'] if not s['rung'] and not s['exhausted'] and s['misses'] >= 2]
    flags, fcount = lab_flags(app, section, user.id)
    hx = helix_signals(db, user.id, section.id)
    parts = []
    if exhausted:
        parts.append(f'ran out of explanations on {", ".join("“" + s["heading"] + "”" for s in exhausted[:2])}')
    if repeated:
        parts.append(f'missed {", ".join("“" + s["heading"] + "”" for s in repeated[:2])} repeatedly')
    if fcount:
        lab_txt = '; '.join(f'{k.lower()} in {n} lab{"s" if n != 1 else ""}' for k, n in fcount.most_common(2))
        parts.append(lab_txt)
    if hx['text']:
        parts.append(hx['text'].lower())
    es = exam_sim_signal(db, section, user)
    if es and es['flagged']:
        parts.append(f'scored {es["att"].score}/900 on the {es["code"]} exam simulator'
                     + (f', weakest in {es["worst"]["domain"]} {es["worst"]["name"]} ({es["worst"]["pct"]}%)' if es['worst'] else ''))
    style = lad.STYLE.get(c['best']) if c['best'] else None
    sentence = (f'{user.first_name or user.full_name} ' + '; '.join(parts) + '.' if parts else
                f'{user.first_name or user.full_name} has nothing open right now: {c["resolved"]} struggle{"s" if c["resolved"] != 1 else ""} resolved by an alternative explanation.')
    if style and c['best'] != 'R0':
        sentence += f' {style} explanations usually work for them.'
    pills = {'ladder': ([c['best_text']] if c['best_text'] else []) + [s['text'] + f' ({s["heading"]})' for s in (exhausted + repeated)[:3]],
             'lab': [f'{k} ×{n}' for k, n in fcount.most_common(3)], 'helix': hx['pills'],
             'exam_sim': [es['pill']] if es else []}
    focus = (exhausted + repeated)[:1]
    actions = []
    subject = f'Let us go through “{focus[0]["heading"]}” together' if focus else ('Let us go through your recent labs together' if flags else 'Let us go through this week together')
    body = f'Hi {user.first_name or ""},\n\n' + (f'I noticed “{focus[0]["heading"]}” has been tricky. ' if focus else '') + \
        'Could we spend ten minutes on it together? Reply with a time that suits you.\n'
    actions.append({'kind': 'message', 'text': 'Draft message', 'url': url_for('messages_new', to=user.id, subject=subject, body=body)})
    if focus:
        anchor = f'#pv-{focus[0]["sid"]}'
        actions.append({'kind': 'preview', 'text': f'Open {c["best"]} preview' if c['best'] and c['best'] != 'R0' else 'Open explanations preview',
                        'url': url_for('ladder_preview', section_id=section.id, label=focus[0]['label']) + anchor})
        les = _lesson_id(app, db, section, focus[0]['label'])
        if les:
            actions.append({'kind': 'bypass', 'text': 'Grant gate bypass', 'form': True, 'lesson_id': les,
                            'url': url_for('ladder_settings', section_id=section.id)})
    stuck = [{'text': f'{s["label"]} · {s["heading"]}', 'detail': (f'every explanation tried ({s["misses"]} misses)' if s['exhausted']
                                                                       else f'{s["misses"]} misses, still open')} for s in (exhausted + repeated)[:3]]
    stuck += [{'text': f'Lab {f["lab_id"]}', 'detail': f['label'], 'url': f['url']} for f in flags[:1]] if not stuck else []
    if es and es['flagged']:
        res_url = url_for('exam_sim_result', section_id=section.id, attempt_id=es['att'].id)
        if es['worst']:
            stuck.append({'text': f'Exam Sim {es["code"]} · {es["worst"]["domain"]} {es["worst"]["name"]}',
                          'detail': f'{es["worst"]["pct"]}% in the latest sitting ({es["att"].score}/900, {es["label"].lower()})',
                          'url': res_url})
        actions.append({'kind': 'exam_sim', 'text': 'Open Exam-Day Simulator result', 'url': res_url})
        actions.append({'kind': 'exam_sim_class', 'text': 'Class simulator overview',
                        'url': url_for('instructor_exam_sim', section_id=section.id)})
    best_badge = f'✓ Best style: {style} ({c["best"]})' if style else None
    return {'user': user, 'sentence': sentence, 'stuck': stuck, 'best_badge': best_badge,
            'lab_tags': [{'text': f'Lab: {k} ×{n}' if n > 1 else f'Lab: {k}', 'url': next(f['url'] for f in flags if f['label'] == k)}
                         for k, n in fcount.most_common(2)], 'pills': pills, 'flags': flags[:4], 'clicked': c, 'helix': hx,
            'actions': actions, 'exam_sim': es,
            'severity': len(exhausted) * 3 + len(repeated) * 2 + sum(fcount.values())
            + ((3 if es['att'].badge == 'remediate' else 2) if es and es['flagged'] else 0)}


def _lesson_id(app, db, section, label):
    Lesson, Module = _model(db, 'Lesson'), _model(db, 'Module')
    try:
        ch = int(label.split('.')[0])
    except ValueError:
        return None
    mod = Module.query.filter_by(course_id=section.course_id, order=ch).first()
    if not mod:
        return None
    from curriculum_v2.ladder.sections import lesson_label
    return next((x.id for x in Lesson.query.filter_by(module_id=mod.id).all() if lesson_label(x.title) == label), None)


def for_section(app, db, section, users, limit=None):
    out = [why(app, db, section, u) for u in users]
    out = [w for w in out if w['severity'] or w['clicked']['struggles']]
    out.sort(key=lambda w: -w['severity'])
    return out[:limit] if limit else out


def install(app, db):
    """Template helpers: why_struggling(section, user), why_section(section, limit), ladder_clicked(uid, section_id),
    class_clicked(section_id). Failures render nothing rather than break a staff page."""
    def safe(fn):
        def inner(*a, **k):
            try:
                return fn(*a, **k)
            except Exception as exc:   # noqa: BLE001
                db.session.rollback()
                print('why:', exc)
                return None
        return inner

    def section_list(section, limit=None):
        Enr, User = _model(db, 'Enrollment'), _model(db, 'User')
        users = (User.query.join(Enr, Enr.user_id == User.id)
                 .filter(Enr.section_id == section.id, User.role == 'student').all())
        return for_section(app, db, section, users, limit)

    lad = lambda: app.extensions['ciwt_mastery'].ladder   # noqa: E731
    app.jinja_env.globals.update(
        why_struggling=safe(lambda section, user: why(app, db, section, user)),
        why_section=safe(section_list),
        ladder_clicked=safe(lambda uid, sid: lad().clicked(uid, sid)),
        class_clicked=safe(lambda sid: lad().class_clicked(sid)),
        helix_optins=safe(helix_optins_for(db)))


def helix_optins_for(db):
    def count(section):
        Consent, Enr, User = _model(db, 'HelixConsent'), _model(db, 'Enrollment'), _model(db, 'User')
        if not Consent:
            return 0
        ids = [u.id for u in User.query.join(Enr, Enr.user_id == User.id)
               .filter(Enr.section_id == section.id, User.role == 'student').all()]
        if not ids:
            return 0
        return len({c.user_id for c in Consent.query.filter(Consent.user_id.in_(ids), Consent.revoked_at.is_(None)).all()})
    return count
