"""Helpers that wrap a section's original lines in five different explanations."""


def _dot(text):
    text = str(text).strip()
    return text if text.endswith('.') else text + '.'


def Sec(heading, topic, r0, plain, story, steps, key, bad1, bad2, why, covers=(), family='sort', widget='sort',
        r1=None, r2=None, r4=None, boxes=None, note=None, neighbor='', scene=''):
    """A section whose standard, plain, and analogy paths are original sentences."""
    if isinstance(r0, str):
        r0 = [r0]
    if isinstance(plain, str):
        plain = [plain]
    if isinstance(story, str):
        story = [story]
    why_out = why if len(why.split()) >= 12 else why + ' The other choices describe a different goal or a different control.'
    spoken = _dot(plain[0])
    tale = _dot(story[0])
    if r1 is None:
        r1 = [spoken, tale]
    if r2 is None:
        r2 = [tale, spoken]
    if r4 is None:
        r4 = [f'Sort {topic} evidence before opening the station.', f'{topic} cards teach one decision.']
    if boxes is None:
        boxes = [(heading[:22] or 'Topic', 'definition'), (heading[:22] or 'Topic', 'ticket'), (heading[:22] or 'Topic', 'decision')]
    fit_a = spoken.rstrip('.')
    fit_b = (scene or heading)[:90]
    other = neighbor or 'a neighboring idea'
    return {
        'heading': heading,
        'topic': topic,
        'covers': list(covers),
        'family': family,
        'widget': widget,
        'r0': list(r0),
        'r1': list(r1),
        'r2': list(r2),
        'steps': list(steps),
        'key': key,
        'bad': [bad1, bad2],
        'why': why_out,
        'note': _dot(note if note is not None else plain[0]),
        'diagram': heading[:42],
        'boxes': list(boxes),
        'diagram_r3': f'{heading[:32]} trace',
        'boxes_r3': [('Begin', steps[0][:28]), ('Middle', steps[1][:28]), ('Confirm', steps[2][:28])],
        'r4': list(r4),
        'sort_prompt': f'Which cards belong with {topic}?',
        'sort': {
            'Fits this idea': [f'{topic}: {fit_a[:80]}', f'{topic} evidence: {fit_b[:80]}'],
            'Does not fit': [f'{other}: a different fact', f'{topic}: guess and skip the note'],
        },
        'sort_done': f'The fitting pile is the {topic} decision you will write on the next ticket.',
        'lab_note': f'Open the linked station and compare the live state with the safe {topic} state.',
        'neighbor': other,
    }


def S(heading, topic, tech, example, plain, story, steps, key, bad1, bad2, why):
    """tech/example stay in the standard path. plain, story, and steps stay in their own paths."""
    return {
        'heading': heading,
        'topic': topic,
        'r0': [
            f'This concept treats {tech}.',
            f'A failure shows up when {example}.',
            'The repair is a setting or a habit that blocks the bad outcome.',
            'Record that outcome in the ticket before any technical change.',
            'A new gadget is not the default repair.',
        ],
        'r1': [
            'The everyday version is simple.',
            plain if plain.endswith('.') else plain + '.',
            'A person can repeat that line.',
            'When the line is fuzzy, stop.',
            'Do not touch the machine yet.',
            'Ask which person, which object, and which bad result.',
            'Three answers are enough to start.',
        ],
        'r2': [
            'Picture a clinic front desk.',
            story if story.endswith('.') else story + '.',
            'The desk picture is only a mirror.',
            'Match each piece to one job you actually perform.',
            'When the mirror breaks, the job remains.',
            'A story is a memory aid, not proof.',
            'Keep the picture in the margin as a memory hook beside the real task.',
        ],
        'steps': steps,
        'key': key,
        'bad': [bad1, bad2],
        'why': why if len(why.split()) >= 10 else why + ' The other choices describe a different goal.',
        'note': 'Record the outcome in the ticket before any technical change.',
        'diagram': heading,
        'boxes': [('Asset', 'what matters'), ('Rule', 'who or what'), ('Proof', 'how you know')],
        'diagram_r3': 'Order of the trace',
        'boxes_r3': [('Begin', steps[0][:22]), ('Middle', steps[1][:22]), ('Confirm', steps[2][:22])],
        'r4': [
            'Sort the cards into two piles.',
            'The piles are the whole exercise.',
            'When both piles feel settled, open the station linked from this lesson if one is listed.',
        ],
        'sort_prompt': 'Sort the cards.',
        'sort': {
            'Fits this idea': ['careful choice', 'written reason'],
            'Does not fit': ['wild guess', 'skipped note'],
        },
        'sort_done': 'The fitting pile is the habit you will use on a ticket.',
        'lab_note': 'Open the linked station and compare the live state with the safe state.',
    }


def lesson(n, title, skill, objective, fits, intro, sections, lab=None, mc_label='', mc_fix='', mc_terms=None):
    return L(n, title, skill, objective, fits, intro, sections, lab=lab, mc_label=mc_label, mc_fix=mc_fix, mc_terms=mc_terms)


def L(n, title, skill, objective, fits, intro, sections, lab=None, mc_label='', mc_fix='', mc_terms=None, skill_name=''):
    return {
        'order': n,
        'title': title,
        'minutes': 45,
        'skill': skill,
        'skill_name': skill_name or objective,
        'objective': objective,
        'fits': fits,
        'intro': intro if isinstance(intro, list) else [intro],
        'sections': sections,
        'lab': lab,
        'mc_label': mc_label,
        'mc_fix': mc_fix,
        'mc_terms': mc_terms or [skill, 'control', 'ticket'],
    }


def Ch(order, title, overview, lessons):
    return {'order': order, 'title': title, 'overview': overview, 'minutes': 180, 'lessons': lessons}
