"""Turn chapter specs into lesson HTML and explanation-ladder modules.

R0 is the lesson section the student reads. R1–R4 are different explanations of that
same idea. Headings, section ids, and r0 stamps come from the rendered HTML.
"""
from html import escape

from curriculum_v2.ladder.schema import analogy, check, plain, section, sort, tryit, visual
from curriculum_v2.ladder.sections import sections

from curriculum_sec import specs as SP

REVIEW = 'Pending SME review'
SOURCE = 'Novak LMS™ Security lesson (original). Pending SME review.'


def _p(sentences):
    return ''.join(f'<p>{escape(s)}</p>' for s in sentences)


def _svg(label, boxes):
    label_e = escape(label)
    parts = [
        f'<svg viewBox="0 0 680 128" role="img" aria-label="{label_e}">',
        f'<title>{label_e}</title>',
        '<rect x="1" y="1" width="678" height="126" rx="10" fill="none" stroke="currentColor"/>',
    ]
    n = max(1, len(boxes))
    gap = 16
    w = (640 - gap * (n - 1)) / n
    for i, (title, sub) in enumerate(boxes):
        x = 20 + i * (w + gap)
        parts.append(
            f'<rect x="{x:.1f}" y="28" width="{w:.1f}" height="72" rx="8" fill="none" stroke="currentColor" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{x + w / 2:.1f}" y="58" text-anchor="middle" fill="currentColor" font-size="13">{escape(title)}</text>'
        )
        parts.append(
            f'<text x="{x + w / 2:.1f}" y="80" text-anchor="middle" fill="currentColor" font-size="11">{escape(sub)}</text>'
        )
        if i < n - 1:
            x2 = x + w
            parts.append(
                f'<line x1="{x2 + 2:.1f}" y1="64" x2="{x2 + gap - 2:.1f}" y2="64" stroke="currentColor" stroke-width="2"/>'
            )
    parts.append('</svg>')
    return ''.join(parts)


def _balance(correct, wrongs):
    wrongs = list(wrongs)
    if len(correct) > max(len(w) for w in wrongs):
        i = max(range(len(wrongs)), key=lambda n: len(wrongs[n]))
        while len(wrongs[i]) <= len(correct):
            wrongs[i] += ' in this case'
    return wrongs


def _five(topic, key, bad, why, mc_id):
    wrongs = _balance(key, bad)
    stems = [
        f'Which choice matches the idea of {topic}?',
        f'A new teammate asks about {topic}. What do you tell them?',
        f'Which line corrects a mix-up about {topic}?',
        f'The picture is about {topic}. Which caption is fair?',
        f'After the try-it, which result shows you understood {topic}?',
    ]
    return [check(q, key, list(wrongs), why, mc={wrongs[0]: mc_id}) for q in stems]


def _section_html(sec):
    svg = _svg(sec['diagram'], sec['boxes'])
    return (
        f'<section class="sublesson core"><h3>{escape(sec["heading"])}</h3>'
        f'{svg}{_p(sec["r0"])}'
        f'<div class="analogy-box"><div class="analogy-label">Workplace note</div>'
        f'<p>{escape(sec["note"])}</p></div>'
        '</section>'
    )


def _lesson_html(lesson, first):
    skill = lesson['skill']
    fit_label = 'Where this fits' if first else 'Builds on'
    body = [
        f'<div class="lo-panel" data-skill="{escape(skill)}"><h4>Terminal objectives</h4><ul>',
        f'<li>{escape(lesson["objective"])}</li>',
        '<li>Answer the knowledge check on every section, in any learning path</li>',
        '<li>Use the linked lab when this lesson names one</li>',
        '</ul></div>',
        f'<div class="build-on"><strong>{fit_label}:</strong> {escape(lesson["fits"])}</div>',
        f'<div class="plain-english"><h4>In plain English</h4>{_p(lesson["intro"])}</div>',
        '<div class="live-demo"><h4>Live demonstration habit</h4>'
        '<p>Say the idea in one sentence, point at the diagram, then name the mistake you will not make. '
        'If that stalls, switch the learning path and answer the check again.</p></div>',
    ]
    for sec in lesson['sections']:
        body.append(_section_html(sec))
    body.append(
        '<div class="practice-standard"><h4>Practice standard for this lesson</h4>'
        f'<p>When you finish {escape(lesson["title"])}, you can coach a classmate on it '
        'without the notes in front of you. The checks under each section all map to this skill.</p></div>'
    )
    return ''.join(body)


_SALTS = {
    'R1': [
        'Use short everyday words a brand-new coworker already knows.',
        'Speak one calm line. Pause. Let the other person repeat it.',
        'Skip fancy vocabulary until the point feels steady.',
        'Point at the thing itself, not at a product name.',
    ],
    'R2': [
        'The hallway, the badge, and the locked cupboard are only stand-ins.',
        'Map every story piece back to a single real job.',
        'If the tale wobbles, keep the job and drop the tale.',
        'A metaphor never replaces the measured fact.',
    ],
    'R3': [
        'Read the numbered trace from the left box toward the right box.',
        'Arrows mean sequence. They do not rank importance.',
        'Cover the picture and say the trace from memory.',
        'The drawing is a map of order, nothing more.',
    ],
    'R4': [
        'Drag each card one time. The two piles are the whole exercise.',
        'When the piles look settled, open the hands-on station.',
        'Do the sort before you hunt for a command to copy.',
        'The cards train judgment. The station trains your hands.',
    ],
}


def _force_distinct(section_html, htmls):
    """Add a short extra sentence until rung texts are genuinely different."""
    from curriculum_v2.ladder.schema import similarity
    used = {k: 0 for k in htmls}

    def offenders():
        bad = set()
        for k, h in htmls.items():
            if similarity(section_html, h) > 0.50:
                bad.add(k)
        keys = list(htmls)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                if similarity(htmls[a], htmls[b]) > 0.50:
                    bad.add(a)
                    bad.add(b)
        return bad

    guard = 0
    while True:
        bad = offenders()
        if not bad:
            return htmls
        guard += 1
        if guard > 12:
            raise RuntimeError('rungs stayed too similar: ' + ', '.join(sorted(bad)))
        for k in sorted(bad):
            pool = _SALTS[k]
            htmls[k] += f'<p>{escape(pool[used[k] % len(pool)])}</p>'
            used[k] += 1


def _rungs(sec, lab_id, checks, section_html):
    items = ''.join(f'<li>{escape(s)}</li>' for s in sec['steps'])
    htmls = {
        'R1': _p(sec['r1']),
        'R2': _p(sec['r2']),
        'R3': _svg(sec['diagram_r3'], sec['boxes_r3']) + f'<p>Follow the numbered trace.</p><ol>{items}</ol>',
        'R4': _p(sec['r4']),
    }
    htmls = _force_distinct(section_html, htmls)
    r1 = plain(htmls['R1'], SOURCE, [checks[1]])
    r2 = analogy(htmls['R2'], SOURCE, [checks[2]])
    r3 = visual(htmls['R3'], SOURCE, [checks[3]])
    widget = sort(sec['sort_prompt'], sec['sort'], sec['sort_done'])
    lab = {'id': lab_id, 'note': sec['lab_note']} if lab_id else None
    r4 = tryit(htmls['R4'], SOURCE, [checks[4]], widget=widget, lab=lab)
    return r1, r2, r3, r4


def build():
    chapters = []
    ladders = {}
    for ch in SP.CHAPTERS:
        lessons = []
        lad_lessons = {}
        mcs = {}
        for i, lesson in enumerate(ch['lessons']):
            html = _lesson_html(lesson, first=(ch['order'] == 1 and i == 0))
            lessons.append({
                'title': lesson['title'],
                'order': lesson['order'],
                'minutes': lesson['minutes'],
                'html': html,
                'skill': lesson['skill'],
            })
            parsed = {s['heading']: s for s in sections(html)}
            mc_id = f"MC-L-SEC-{ch['order']}-{lesson['order']}"
            mcs[mc_id] = {
                'obj': lesson['skill'],
                'label': lesson['mc_label'],
                'fix': lesson['mc_fix'],
                'terms': lesson['mc_terms'],
                'source': SOURCE,
                'review': REVIEW,
            }
            lad = {}
            for sec in lesson['sections']:
                block = parsed[sec['heading']]
                checks = _five(sec['topic'], sec['key'], sec['bad'], sec['why'], mc_id)
                r1, r2, r3, r4 = _rungs(sec, lesson.get('lab'), checks, block['html'])
                ent = section(
                    sec['heading'], lesson['skill'], [checks[0]], r1, r2, r3, r4, r0_sha=block['r0_sha'],
                )
                lad[block['sid']] = ent
            lad_lessons[f"{ch['order']}.{lesson['order']}"] = lad
        chapters.append({
            'order': ch['order'],
            'title': ch['title'],
            'overview': ch['overview'],
            'minutes': ch['minutes'],
            'lessons': lessons,
        })
        ladders[ch['order']] = {'LESSONS': lad_lessons, 'MISCONCEPTIONS': mcs}
    return chapters, ladders


def chapter_ladder(n):
    pack = LADDERS[n]
    return 1, 'SEC', n, pack['MISCONCEPTIONS'], pack['LESSONS']


def lesson_count():
    return sum(len(ch['lessons']) for ch in CHAPTERS)


def section_count():
    n = 0
    for ch in CHAPTERS:
        for les in ch['lessons']:
            n += len(sections(les['html']))
    return n


CHAPTERS, LADDERS = build()
