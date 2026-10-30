"""Helpers that wrap a section's original lines in five different explanations."""


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
