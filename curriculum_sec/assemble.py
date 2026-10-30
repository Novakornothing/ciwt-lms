"""Build Security chapter specs from the objective rows.

Each row is one concept section. Rows in a chapter are grouped three to a lesson.
Every section carries five learning paths and a quick check, rendered by curriculum_sec.render.
"""


def _words(text):
    return len((text or '').split())


def _story(noun, line):
    line = line.strip()
    if not line.endswith('.'):
        line += '.'
    body = (
        f'Picture a {noun}. {line} '
        'The picture is only a stand-in for the real job. '
        'Point at one piece of the picture and name the matching part of the ticket. '
        'If the picture gets in the way, drop the picture and keep the fact. '
        'A story helps memory. It is not the evidence you will paste into the note.'
    )
    if _words(body) < 50:
        body += ' Keep the measured fact when the picture fades.'
    return body


def _plain(line):
    line = line.strip()
    if not line.endswith('.'):
        line += '.'
    lines = [
        line,
        'Use short words a new coworker already knows.',
        'Say one calm line, then pause.',
        'If you cannot say it back, do not touch the system yet.',
        'Name the person, the object, and the bad result.',
        'Three answers are enough to start the note.',
    ]
    return lines


def _section(row):
    (ch, bid, name, gist, scene, mix, noun, story, plain, key, bad1, bad2) = row
    fits = (key, f'Named in the ticket as {name}')
    misses = (bad1, bad2)
    labels = list(fits) + list(misses)
    if len(set(labels)) != 4:
        raise RuntimeError(f'Sort cards are not distinct for {bid}: {labels}')
    gist = gist.strip()
    scene = scene.strip()
    mix = mix.strip()
    if not gist.endswith('.'):
        gist += '.'
    if not scene.endswith('.'):
        scene += '.'
    if not mix.endswith('.'):
        mix += '.'
    steps = [
        f'Name {name} before you pick a tool',
        'Write the one fact another person can re-check',
        'Change one setting only after that fact is written',
        'Record what the system shows after the change',
    ]
    why = (
        f'{key} matches {name}. '
        f'{bad1} describes a different job. '
        f'{bad2} would send the ticket the wrong way.'
    )
    sort = {
        'Fits this idea': list(fits),
        'Does not fit': list(misses),
    }
    return {
        'id': bid,
        'heading': name,
        'topic': name,
        'r0': [
            gist,
            scene,
            f'People mix this up. {mix}',
            'Write the fact you observed, then change one thing, then write what the system shows.',
            'A new product is not the first answer. The first answer is the right idea, named in plain words.',
        ],
        'r1': _plain(plain),
        'r2': [
            _story(noun, story),
        ],
        'steps': steps,
        'key': key,
        'bad': [bad1, bad2],
        'why': why,
        'note': scene,
        'diagram': name[:42],
        'boxes': [('Idea', name[:18]), ('Fact', 'what you saw'), ('Note', 'what you write')],
        'diagram_r3': 'Order of the trace',
        'boxes_r3': [('Name it', steps[0][:22]), ('One fact', steps[1][:22]), ('Then write', steps[3][:22])],
        'r4': [
            'Sort each card once.',
            'The fitting pile is the habit you will use on the next ticket.',
            'When the piles look settled, say the idea in one sentence without looking.',
        ],
        'sort_prompt': f'Sort the cards for {name}.',
        'sort': sort,
        'sort_done': f'The fitting pile is how you will handle {name} on a ticket.',
        'lab_note': 'Open the linked station if this lesson names one, and compare the live state with the safe state.',
    }


def _lesson(ch, n, sections, lab):
    first = sections[0]
    names = ', '.join(s['heading'] for s in sections)
    title_bit = first['heading']
    if len(title_bit) > 62:
        title_bit = title_bit[:59].rstrip() + '...'
    return {
        'order': n,
        'title': f'{ch}.{n} {title_bit}',
        'minutes': 40,
        'skill': f'SEC-{ch}.{n}',
        'skill_name': first['heading'],
        'objective': f'Explain {names} and use the distinction on a workplace ticket',
        'fits': (
            'This is the first lesson of Security. It assumes you can already triage a ticket, read a basic network path, and find your way around Windows and Linux.'
            if ch == 1 and n == 1 else
            'Builds on the previous idea. The words stay precise so the next control, attack, or decision is not a blur.'
        ),
        'intro': [
            f'This lesson covers {names}.',
            'Each section is one idea. Name it, match it to a ticket, and reject the look-alike before you pick a tool.',
        ],
        'sections': sections,
        'lab': lab,
        'mc_label': f'Treating {first["heading"]} as if it were the same job as a neighboring idea',
        'mc_fix': first['key'],
        'mc_terms': [first['heading'].split()[0].lower(), 'ticket', 'control'],
        'bullet_ids': [s['id'] for s in sections],
    }


def chapters_from(rows, plan, lesson_labs):
    """plan: list of (order, title, overview, section_count). rows are in plan order."""
    rows = list(rows)
    need = sum(p[3] for p in plan)
    if len(rows) != need:
        raise RuntimeError(f'Security catalog has {len(rows)} sections; the chapter plan needs {need}')
    out = []
    i = 0
    for order, title, overview, count in plan:
        if count % 3 != 0:
            raise RuntimeError(f'Chapter {order} has {count} sections; lessons need groups of 3')
        chunk = rows[i:i + count]
        i += count
        lessons = []
        for n in range(1, count // 3 + 1):
            block = chunk[(n - 1) * 3:n * 3]
            sections = [_section(r) for r in block]
            lab = (lesson_labs or {}).get((order, n))
            lessons.append(_lesson(order, n, sections, lab))
        out.append({
            'order': order,
            'title': f'Chapter {order} — {title}',
            'overview': overview,
            'minutes': 40 * len(lessons),
            'lessons': lessons,
        })
    return out


def bullet_index(chapters):
    """bullet id -> {chapter, lesson, heading, skill}."""
    found = {}
    for ch in chapters:
        for les in ch['lessons']:
            for sec in les['sections']:
                found[sec['id']] = {
                    'chapter': ch['order'],
                    'chapter_title': ch['title'],
                    'lesson': les['title'],
                    'heading': sec['heading'],
                    'skill': les['skill'],
                }
    return found
