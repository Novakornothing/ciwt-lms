"""Cmd-K hits for the three learner pages. Plain names only."""

FEATURES = (
    (('skip what you know', 'placement', 'tested out'),
     'placement_student', 'placement_staff',
     'Skip What You Know',
     'About 20 minutes. Once per course. Chapters you can skip are marked tested out.'),
    (('help desk', 'helpdesk', 'ticket queue'),
     'helpdesk_queue', 'helpdesk_staff',
     'Help Desk Queue',
     'Triage a ticket, ask the user, and close it with a note.'),
    (('daily review', 'spaced', 'flashcard'),
     'daily_review', 'daily_review_staff',
     'Daily Review',
     'About five minutes of commands, ports, protocols, and terms.'),
)


def feature_hits(query, role, section_id, url_for_fn):
    if not section_id:
        return []
    q = (query or '').lower()
    staff = role in ('instructor', 'admin')
    out = []
    for keys, ep_student, ep_staff, title, blurb in FEATURES:
        if not any(k in q for k in keys):
            continue
        ep = ep_staff if staff else ep_student
        out.append({
            'kind': 'Page',
            'title': title,
            'chapter': '',
            'course': 'Novak LMS™',
            'snippet': blurb,
            'snippet_html': blurb,
            'locked': False,
            'url': url_for_fn(ep, section_id=section_id),
            'score': 500,
        })
    return out
