"""HTTP for Skip What You Know, Help Desk Queue, and Daily Review."""
import json
from types import SimpleNamespace

from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from . import placement as P
from .deck import (MINUTES, NEW_PER_DAY, apply_review, cards as all_cards, due_queue,
                   public_card, score_card, session_cards, streak_after)
from .models import define_models, utcnow
from .placement_bank import by_id as placement_by_id, items_for
from .tickets import (PRIORITIES, get_ticket, grade as grade_ticket, public_steps, questions_at,
                      replay, tickets_for)


def register(app, db, deps):
    d = SimpleNamespace(**deps)
    m = define_models(db)
    catalog = all_cards()
    by_card = {c['id']: c for c in catalog}

    def course_of(section):
        return db.session.get(d.Course, section.course_id)

    def enrolled(section_id):
        section = db.get_or_404(d.ClassSection, section_id)
        if current_user.role != 'student':
            abort(403)
        if not d.Enrollment.query.filter_by(user_id=current_user.id, section_id=section.id).first():
            abort(404)
        return section

    def staff(section_id):
        section = db.get_or_404(d.ClassSection, section_id)
        if current_user.role == 'admin':
            return section
        if current_user.role != 'instructor' or not d.can_access_section(current_user, section):
            abort(403)
        return section

    def students_of(section):
        return (d.User.query.join(d.Enrollment, d.Enrollment.user_id == d.User.id)
                .filter(d.Enrollment.section_id == section.id, d.User.role == 'student')
                .order_by(d.User.last_name, d.User.first_name).all())

    def chapter_meta(section):
        course = course_of(section)
        code = course.code if course else ''
        mods = d.Module.query.filter_by(course_id=section.course_id).order_by(d.Module.order).all()
        titles = {mod.order: mod.title for mod in mods}
        items = items_for(code, list(titles))
        chapters = sorted({it['chapter'] for it in items})
        return course, code, chapters, items, titles

    def load_state(text, chapters):
        state = P.blank(chapters)
        try:
            raw = json.loads(text or '{}')
        except ValueError:
            raw = {}
        for key, val in raw.items():
            try:
                ch = int(key)
            except (TypeError, ValueError):
                continue
            if ch not in state or not isinstance(val, dict):
                continue
            state[ch]['p'] = float(val.get('p', state[ch]['p']))
            state[ch]['n_eff'] = float(val.get('n_eff', 0))
            state[ch]['n'] = int(val.get('n', 0))
            state[ch]['correct'] = int(val.get('correct', 0))
        return state

    def dump_state(state):
        return json.dumps({str(k): v for k, v in state.items()})

    def overrides_for(user_id, course_id):
        rows = (m.PlacementOverride.query.filter_by(user_id=user_id, course_id=course_id, active=True)
                .order_by(m.PlacementOverride.id).all())
        return {r.chapter: r.kind for r in rows}

    def attempt_for(user_id, course_id):
        return m.PlacementAttempt.query.filter_by(user_id=user_id, course_id=course_id).first()

    def finish_placement(attempt, state, reason):
        ovs = overrides_for(attempt.user_id, attempt.course_id)
        plan = P.plan(state, ovs)
        attempt.status = 'complete'
        attempt.stop_reason = reason
        attempt.current_id = None
        attempt.state_json = dump_state(state)
        attempt.plan_json = json.dumps(plan)
        attempt.completed_at = utcnow()
        db.session.commit()
        return plan

    # ------------------------------------------------------------------ placement
    @login_required
    def placement_student(section_id):
        section = enrolled(section_id)
        course, code, chapters, items, titles = chapter_meta(section)
        if not chapters:
            abort(404)
        attempt = attempt_for(current_user.id, course.id)
        if request.method == 'POST':
            action = request.form.get('action') or 'answer'
            if action == 'start':
                if attempt and attempt.status == 'complete':
                    flash('You already took Skip What You Know for this course.', 'info')
                    return redirect(url_for('placement_student', section_id=section.id))
                if not attempt:
                    state = P.blank(chapters)
                    item, _why = P.next_item(state, items, [], 0)
                    attempt = m.PlacementAttempt(
                        user_id=current_user.id, course_id=course.id, section_id=section.id,
                        status='active', state_json=dump_state(state), used_json='[]',
                        current_id=item['id'] if item else None, n_asked=0, started_at=utcnow())
                    db.session.add(attempt)
                    db.session.commit()
                return redirect(url_for('placement_student', section_id=section.id))
            if not attempt or attempt.status != 'active' or not attempt.current_id:
                return redirect(url_for('placement_student', section_id=section.id))
            bank = placement_by_id(code)
            item = bank.get(attempt.current_id)
            if not item:
                abort(404)
            choice = request.form.get('choice') or ''
            correct = choice == item['correct'] and choice in item['options']
            state = load_state(attempt.state_json, chapters)
            P.observe(state, item['chapter'], correct)
            used = json.loads(attempt.used_json or '[]')
            used.append(item['id'])
            attempt.used_json = json.dumps(used)
            attempt.n_asked = len(used)
            attempt.state_json = dump_state(state)
            attempt.current_id = None
            elapsed = (utcnow() - (attempt.started_at or utcnow())).total_seconds()
            nxt, why = P.next_item(state, items, used, len(used))
            if nxt and elapsed >= 20 * 60 and len(used) >= P.MIN_ITEMS:
                nxt, why = None, 'time'
            if nxt is None:
                finish_placement(attempt, state, why or 'no_items')
                return redirect(url_for('placement_student', section_id=section.id))
            attempt.current_id = nxt['id']
            db.session.commit()
            return redirect(url_for('placement_student', section_id=section.id))
        if attempt and attempt.status == 'complete':
            state = load_state(attempt.state_json, chapters)
            plan = P.plan(state, overrides_for(current_user.id, course.id))
            return render_template('learner/placement.html', section=section, course=course, mode='plan',
                                   plan=plan, titles=titles, attempt=attempt, minutes=P.minutes_for(P.MAX_ITEMS))
        item = None
        if attempt and attempt.status == 'active':
            if not attempt.current_id:
                state = load_state(attempt.state_json, chapters)
                used = json.loads(attempt.used_json or '[]')
                nxt, why = P.next_item(state, items, used, len(used))
                if nxt is None:
                    finish_placement(attempt, state, why or 'no_items')
                    return redirect(url_for('placement_student', section_id=section.id))
                attempt.current_id = nxt['id']
                db.session.commit()
            item = placement_by_id(code).get(attempt.current_id)
        return render_template('learner/placement.html', section=section, course=course,
                               mode='ask' if item else 'intro', item=item, attempt=attempt,
                               minutes=P.minutes_for(P.MAX_ITEMS), n_chapters=len(chapters))

    @login_required
    def placement_staff(section_id):
        section = staff(section_id)
        course, _code, chapters, _items, titles = chapter_meta(section)
        rows = []
        for u in students_of(section):
            attempt = attempt_for(u.id, course.id) if course else None
            plan = None
            if attempt and attempt.status == 'complete':
                state = load_state(attempt.state_json, chapters)
                plan = P.plan(state, overrides_for(u.id, course.id))
            rows.append({'user': u, 'attempt': attempt, 'plan': plan})
        return render_template('learner/placement_staff.html', section=section, course=course, rows=rows,
                               mode='list', titles=titles)

    @login_required
    def placement_staff_student(section_id, user_id):
        section = staff(section_id)
        course, _code, chapters, _items, titles = chapter_meta(section)
        user = db.get_or_404(d.User, user_id)
        if not d.Enrollment.query.filter_by(section_id=section.id, user_id=user.id).first() or user.role != 'student':
            abort(404)
        attempt = attempt_for(user.id, course.id) if course else None
        if request.method == 'POST':
            action = request.form.get('action') or ''
            if action == 'reset':
                if attempt:
                    db.session.delete(attempt)
                for row in m.PlacementOverride.query.filter_by(user_id=user.id, course_id=course.id, active=True):
                    row.active = False
                db.session.commit()
                if d.audit:
                    d.audit('placement_reset', f'section={section.id} user={user.id} course={course.code}')
                flash(f'{user.full_name} can take Skip What You Know again.', 'success')
                return redirect(url_for('placement_staff', section_id=section.id))
            if not attempt or attempt.status != 'complete':
                flash('There is no finished placement to change.', 'info')
                return redirect(url_for('placement_staff_student', section_id=section.id, user_id=user.id))
            note = (request.form.get('note') or '').strip()[:300]
            if not note:
                flash('Add a short note so the change is clear.', 'warning')
                return redirect(url_for('placement_staff_student', section_id=section.id, user_id=user.id))
            changed = False
            for ch in chapters:
                kind = (request.form.get(f'kind-{ch}') or '').strip()
                if kind not in ('tested_out', 'review', 'placement'):
                    continue
                for row in m.PlacementOverride.query.filter_by(user_id=user.id, course_id=course.id, chapter=ch, active=True):
                    row.active = False
                if kind in ('tested_out', 'review'):
                    db.session.add(m.PlacementOverride(
                        user_id=user.id, course_id=course.id, chapter=ch, kind=kind, note=note,
                        active=True, created_by=current_user.id, created_at=utcnow()))
                changed = True
            if changed:
                db.session.flush()
                state = load_state(attempt.state_json, chapters)
                attempt.plan_json = json.dumps(P.plan(state, overrides_for(user.id, course.id)))
                db.session.commit()
                if d.audit:
                    d.audit('placement_override', f'section={section.id} user={user.id}')
                flash('Saved.', 'success')
            return redirect(url_for('placement_staff_student', section_id=section.id, user_id=user.id))
        plan = None
        if attempt and attempt.status == 'complete':
            plan = P.plan(load_state(attempt.state_json, chapters), overrides_for(user.id, course.id))
        return render_template('learner/placement_staff.html', section=section, course=course, mode='detail',
                               user=user, attempt=attempt, plan=plan, titles=titles, chapters=chapters)

    # ------------------------------------------------------------------ help desk
    @login_required
    def helpdesk_queue(section_id):
        section = enrolled(section_id)
        course = course_of(section)
        code = course.code if course else ''
        tickets = tickets_for(code)
        if not tickets:
            abort(404)
        attempts = {a.ticket_id: a for a in m.HelpdeskAttempt.query.filter_by(user_id=current_user.id).all()
                    if a.ticket_id in {t['id'] for t in tickets}}
        rows = []
        for t in tickets:
            a = attempts.get(t['id'])
            if a and a.phase == 'done':
                status = f'Resolved {a.total}'
            elif a:
                status = 'In progress'
            else:
                status = 'Open'
            rows.append({'ticket': t, 'attempt': a, 'status': status})
        done = sum(1 for r in rows if r['attempt'] and r['attempt'].phase == 'done')
        return render_template('learner/helpdesk.html', section=section, course=course, mode='queue',
                               rows=rows, done=done, total=len(rows))

    @login_required
    def helpdesk_ticket(section_id, ticket_id):
        section = enrolled(section_id)
        course = course_of(section)
        ticket = get_ticket(ticket_id)
        if not ticket or not course or ticket['course'] != course.code:
            abort(404)
        attempt = m.HelpdeskAttempt.query.filter_by(user_id=current_user.id, ticket_id=ticket_id).first()
        if request.method == 'POST':
            if attempt and attempt.phase == 'done':
                return redirect(url_for('helpdesk_ticket', section_id=section.id, ticket_id=ticket_id))
            if not attempt:
                attempt = m.HelpdeskAttempt(
                    user_id=current_user.id, section_id=section.id, course_code=course.code,
                    ticket_id=ticket_id, phase='triage', started_at=utcnow())
                db.session.add(attempt)
                db.session.flush()
            action = request.form.get('action') or ''
            if action == 'priority' and attempt.phase == 'triage':
                pri = (request.form.get('priority') or '').lower()
                if pri in PRIORITIES:
                    attempt.priority = pri
                    attempt.phase = 'clarify'
            elif action == 'ask' and attempt.phase == 'clarify':
                _lines, node = replay(ticket, json.loads(attempt.asked_json or '[]'))
                qid = request.form.get('qid') or ''
                if any(q['id'] == qid for q in questions_at(ticket, node)):
                    asked = json.loads(attempt.asked_json or '[]')
                    asked.append(qid)
                    attempt.asked_json = json.dumps(asked)
            elif action == 'diagnose' and attempt.phase == 'clarify':
                if json.loads(attempt.asked_json or '[]'):
                    attempt.phase = 'diagnose'
                else:
                    flash('Ask the user at least one question first.', 'info')
            elif action == 'step' and attempt.phase == 'diagnose':
                sid = request.form.get('step') or ''
                known = {s['id'] for s in ticket['steps']}
                chosen = json.loads(attempt.steps_json or '[]')
                if sid in known and sid not in chosen:
                    chosen.append(sid)
                    attempt.steps_json = json.dumps(chosen)
            elif action == 'close' and attempt.phase == 'diagnose':
                if json.loads(attempt.steps_json or '[]'):
                    attempt.phase = 'close'
                else:
                    flash('Pick at least one diagnostic step.', 'info')
            elif action == 'resolve' and attempt.phase == 'close':
                note = (request.form.get('note') or '').strip()
                steps = json.loads(attempt.steps_json or '[]')
                seconds = int((utcnow() - (attempt.started_at or utcnow())).total_seconds())
                result = grade_ticket(ticket, priority=attempt.priority, steps=steps, note=note, seconds=seconds)
                attempt.note = note[:2000]
                attempt.score_json = json.dumps(result)
                attempt.total = result['total']
                attempt.phase = 'done'
                attempt.finished_at = utcnow()
            db.session.commit()
            return redirect(url_for('helpdesk_ticket', section_id=section.id, ticket_id=ticket_id))
        if attempt and attempt.phase == 'done':
            score = json.loads(attempt.score_json or '{}')
            return render_template('learner/helpdesk.html', section=section, course=course, mode='result',
                                   ticket=ticket, attempt=attempt, score=score)
        if not attempt:
            lines, node = replay(ticket, [])
            return render_template('learner/helpdesk.html', section=section, course=course, mode='work',
                                   ticket=ticket, attempt=None, phase='triage', lines=lines,
                                   questions=[], steps=public_steps(ticket), priorities=PRIORITIES,
                                   chosen=[], lab_id=ticket.get('lab_id'))
        asked = json.loads(attempt.asked_json or '[]')
        lines, node = replay(ticket, asked)
        return render_template('learner/helpdesk.html', section=section, course=course, mode='work',
                               ticket=ticket, attempt=attempt, phase=attempt.phase, lines=lines,
                               questions=questions_at(ticket, node), steps=public_steps(ticket),
                               priorities=PRIORITIES, chosen=json.loads(attempt.steps_json or '[]'),
                               lab_id=ticket.get('lab_id'))

    @login_required
    def helpdesk_staff(section_id):
        section = staff(section_id)
        course = course_of(section)
        code = course.code if course else ''
        ids = {t['id'] for t in tickets_for(code)}
        rows = []
        for u in students_of(section):
            attempts = [a for a in m.HelpdeskAttempt.query.filter_by(user_id=u.id, section_id=section.id) if a.ticket_id in ids]
            done = [a for a in attempts if a.phase == 'done' and a.total is not None]
            minutes = []
            for a in done:
                if a.started_at and a.finished_at:
                    minutes.append(max(1, int((a.finished_at - a.started_at).total_seconds() // 60)))
            avg = round(sum(a.total for a in done) / len(done)) if done else None
            avg_min = round(sum(minutes) / len(minutes)) if minutes else None
            rows.append({'user': u, 'resolved': len(done), 'open': len(attempts) - len(done), 'avg': avg, 'minutes': avg_min})
        return render_template('learner/helpdesk_staff.html', section=section, course=course, rows=rows,
                               n_tickets=len(ids))

    # ------------------------------------------------------------------ daily review
    def deck_states(user_id):
        out = {}
        for row in m.DeckState.query.filter_by(user_id=user_id):
            out[row.card_id] = {
                'ease': row.ease, 'interval': row.interval_days, 'reps': row.reps,
                'lapses': row.lapses, 'due': row.due_on, 'last': row.last_on,
            }
        return out

    def progress_row(user_id, create=False):
        row = db.session.get(m.DeckProgress, user_id)
        if not row and create:
            row = m.DeckProgress(user_id=user_id, streak=0)
            db.session.add(row)
        return row

    def ensure_session(user, course_code):
        today = utcnow().date()
        prog = progress_row(user.id, create=True)
        if prog.session_day != today:
            queue = due_queue(catalog, deck_states(user.id), today, course_code)
            sitting = [c['id'] for c in session_cards(queue)]
            prog.session_day = today
            prog.session_json = json.dumps(sitting)
            prog.done_json = '[]'
            db.session.commit()
        try:
            session_ids = json.loads(prog.session_json or '[]')
            done_ids = json.loads(prog.done_json or '[]')
        except ValueError:
            session_ids, done_ids = [], []
        return prog, session_ids, done_ids, today

    def due_now(user, course_code):
        today = utcnow().date()
        states = deck_states(user.id)
        prog = progress_row(user.id, create=False)
        streak = (prog.streak if prog else 0) or 0
        overdue = [cid for cid, st in states.items() if st['due'] <= today]
        if prog and prog.session_day == today:
            try:
                session_ids = json.loads(prog.session_json or '[]')
                done_ids = json.loads(prog.done_json or '[]')
            except ValueError:
                session_ids, done_ids = [], []
            if session_ids and set(done_ids) >= set(session_ids):
                return len(overdue), streak
            left = len([i for i in session_ids if i not in set(done_ids)])
            extra = len([cid for cid in overdue if cid not in session_ids])
            return left + extra, streak
        unseen = sum(1 for c in catalog if c['id'] not in states)
        return len(overdue) + min(NEW_PER_DAY, unseen), streak

    def apply_grade(user, card, raw):
        today = utcnow().date()
        quality = score_card(card, raw)
        row = m.DeckState.query.filter_by(user_id=user.id, card_id=card['id']).first()
        before = None
        if row:
            before = {'ease': row.ease, 'interval': row.interval_days, 'reps': row.reps, 'lapses': row.lapses,
                      'due': row.due_on, 'last': row.last_on}
        after = apply_review(before, quality, today)
        if not row:
            row = m.DeckState(user_id=user.id, card_id=card['id'])
            db.session.add(row)
        row.ease = after['ease']
        row.interval_days = after['interval']
        row.reps = after['reps']
        row.lapses = after['lapses']
        row.due_on = after['due']
        row.last_on = after['last']
        return quality

    @login_required
    def daily_review(section_id):
        section = enrolled(section_id)
        course = course_of(section)
        code = course.code if course else ''
        prog, session_ids, done_ids, today = ensure_session(current_user, code)
        if request.method == 'POST':
            card_id = (request.form.get('card_id') or (request.json or {}).get('card_id') or '').strip()
            raw = request.form.get('answer')
            if raw is None and request.is_json:
                raw = (request.json or {}).get('answer')
            card = by_card.get(card_id)
            already = card_id in done_ids
            quality = None
            if card and card_id in session_ids and not already:
                quality = apply_grade(current_user, card, raw or '')
                done_ids.append(card_id)
                prog.done_json = json.dumps(done_ids)
                if set(done_ids) >= set(session_ids) and session_ids:
                    streak, last = streak_after(prog.streak or 0, prog.last_completed, today, True)
                    prog.streak = streak
                    prog.last_completed = last
                db.session.commit()
            wants_json = request.is_json or request.headers.get('X-Requested-With') == 'fetch'
            if wants_json:
                return jsonify({'ok': True, 'quality': quality, 'already': already,
                                'done': len(done_ids), 'total': len(session_ids),
                                'answer': card['answer'] if card and quality is not None else None})
            if quality is not None and card:
                if quality >= 3:
                    flash('Recorded.', 'success')
                else:
                    flash(f'The answer is {card["answer"]}.', 'info')
            return redirect(url_for('daily_review', section_id=section.id))
        remaining = [i for i in session_ids if i not in done_ids]
        if not remaining:
            return render_template('learner/daily.html', section=section, course=course, mode='done',
                                   streak=prog.streak or 0, done=len(done_ids), total=len(session_ids),
                                   minutes=MINUTES, sync=_sync_payload(current_user, code, prog, session_ids, done_ids))
        card = by_card.get(remaining[0])
        return render_template('learner/daily.html', section=section, course=course, mode='ask',
                               card=public_card(card) if card else None, streak=prog.streak or 0,
                               n_done=len(done_ids), n_total=len(session_ids), minutes=MINUTES,
                               sync=_sync_payload(current_user, code, prog, session_ids, done_ids))

    def _sync_payload(user, course_code, prog, session_ids, done_ids):
        today = utcnow().date()
        due, streak = due_now(user, course_code)
        return {
            'user_id': user.id,
            'day': today.isoformat(),
            'streak': streak,
            'due': due,
            'session': [public_card(by_card[i]) for i in session_ids if i in by_card],
            'done': list(done_ids),
        }

    @login_required
    def daily_sync(section_id):
        section = enrolled(section_id)
        course = course_of(section)
        prog, session_ids, done_ids, _today = ensure_session(current_user, course.code if course else '')
        return jsonify(_sync_payload(current_user, course.code if course else '', prog, session_ids, done_ids))

    @login_required
    def daily_review_staff(section_id):
        section = staff(section_id)
        course = course_of(section)
        code = course.code if course else ''
        today = utcnow().date()
        rows = []
        for u in students_of(section):
            n_cards = m.DeckState.query.filter_by(user_id=u.id).count()
            prog = progress_row(u.id, create=False)
            due, streak = due_now(u, code)
            rows.append({'user': u, 'streak': (prog.streak if prog else 0) or 0, 'learned': n_cards,
                         'due': due, 'last': prog.last_completed if prog else None})
        return render_template('learner/daily_staff.html', section=section, course=course, rows=rows, today=today)

    def home(user, section):
        course = course_of(section)
        code = course.code if course else ''
        due, streak = due_now(user, code)
        attempt = attempt_for(user.id, course.id) if course else None
        skip = []
        if attempt and attempt.status == 'complete' and course:
            _c, _code, chapters, _items, _titles = chapter_meta(section)
            state = load_state(attempt.state_json, chapters)
            skip = P.plan(state, overrides_for(user.id, course.id))['skip']
        return {
            'due': due,
            'streak': streak,
            'skip': skip,
            'placement_done': bool(attempt and attempt.status == 'complete'),
            'has_placement': bool(items_for(code)),
            'has_helpdesk': bool(tickets_for(code)),
            'daily_url': url_for('daily_review', section_id=section.id),
            'placement_url': url_for('placement_student', section_id=section.id),
            'helpdesk_url': url_for('helpdesk_queue', section_id=section.id),
        }

    for rule, ep, fn, methods in [
        ('/student/section/<int:section_id>/placement', 'placement_student', placement_student, ['GET', 'POST']),
        ('/instructor/section/<int:section_id>/placement', 'placement_staff', placement_staff, ['GET']),
        ('/instructor/section/<int:section_id>/placement/<int:user_id>', 'placement_staff_student', placement_staff_student, ['GET', 'POST']),
        ('/student/section/<int:section_id>/helpdesk', 'helpdesk_queue', helpdesk_queue, ['GET']),
        ('/student/section/<int:section_id>/helpdesk/<ticket_id>', 'helpdesk_ticket', helpdesk_ticket, ['GET', 'POST']),
        ('/instructor/section/<int:section_id>/helpdesk', 'helpdesk_staff', helpdesk_staff, ['GET']),
        ('/student/section/<int:section_id>/daily-review', 'daily_review', daily_review, ['GET', 'POST']),
        ('/student/section/<int:section_id>/daily-review/sync', 'daily_sync', daily_sync, ['GET']),
        ('/instructor/section/<int:section_id>/daily-review', 'daily_review_staff', daily_review_staff, ['GET']),
    ]:
        app.add_url_rule(rule, ep, fn, methods=methods)

    api = SimpleNamespace(models=m, home=home, cards=catalog, due_now=due_now)
    app.extensions['novak_learner'] = api
    return api
