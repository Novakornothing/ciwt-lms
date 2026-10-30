"""Daily Review deck: SM-2 scheduling and a catalog of commands, ports, protocols, and terms.

SM-2 (SuperMemo 2), per card, quality 0–5:

* ease starts at 2.5 and moves by ``0.1 - (5-q) * (0.08 + (5-q) * 0.02)``, floored at 1.3
* quality under 3 is a lapse: repetitions return to 0 and the interval returns to 1 day
* otherwise the interval is 1 day, then 6 days, then round(interval * ease)

A new student is introduced to a few unseen cards each day. Cards already scheduled are due
on their date. Today's sitting is the overdue cards plus that day's new cards, capped so the
sitting stays about five minutes. State is stored per user; the browser keeps a copy in IndexedDB.
"""
import random
import re
from datetime import date, timedelta

EASE_START = 2.5
EASE_MIN = 1.3
NEW_PER_DAY = 8
SESSION_MAX = 12
MINUTES = 5

_WS = re.compile(r'\s+')


def sm2_step(ease, interval, reps, quality):
    """Return (ease, interval_days, reps) after one review."""
    q = max(0, min(5, int(quality)))
    ease = float(ease) + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    if ease < EASE_MIN:
        ease = EASE_MIN
    ease = round(ease, 4)
    if q < 3:
        return ease, 1, 0
    if reps <= 0:
        interval = 1
    elif reps == 1:
        interval = 6
    else:
        interval = max(1, int(round(float(interval) * ease)))
    return ease, interval, int(reps) + 1


def apply_review(state, quality, today):
    """state is None for a first review. Returns a new state dict."""
    ease = EASE_START if not state else state['ease']
    interval = 0 if not state else state['interval']
    reps = 0 if not state else state['reps']
    lapses = 0 if not state else state['lapses']
    ease, interval, reps = sm2_step(ease, interval, reps, quality)
    if int(quality) < 3:
        lapses += 1
    return {
        'ease': ease,
        'interval': interval,
        'reps': reps,
        'lapses': lapses,
        'due': today + timedelta(days=interval),
        'last': today,
    }


def norm(text):
    s = (text or '').strip().lower().replace('–', '-').replace('—', '-')
    s = s.rstrip('.').strip()
    return _WS.sub(' ', s)


def typed_quality(raw, accept):
    """5 exact, 3 close, 1 wrong, 0 blank."""
    got = norm(raw)
    if not got:
        return 0
    keys = [norm(a) for a in (accept or []) if norm(a)]
    if got in keys:
        return 5
    squish = got.replace(' ', '')
    if any(k.replace(' ', '') == squish for k in keys):
        return 5
    if any(k in got and len(got) <= len(k) + 16 for k in keys):
        return 3
    return 1


def choice_quality(raw, answer):
    if not (raw or '').strip():
        return 0
    return 5 if (raw or '').strip() == answer else 1


def _prefer(card, course_code):
    courses = card.get('courses') or ()
    return (0 if course_code and course_code in courses else 1, card['id'])


def due_queue(cards, states, today, course_code='', new_per_day=NEW_PER_DAY):
    """Full list of cards due today: overdue reviews, then up to ``new_per_day`` unseen cards."""
    reviews = []
    for card in cards:
        st = states.get(card['id'])
        if st and st['due'] <= today:
            reviews.append(card)
    reviews.sort(key=lambda c: (states[c['id']]['due'], c['id']))
    unseen = [c for c in cards if c['id'] not in states]
    unseen.sort(key=lambda c: _prefer(c, course_code))
    buckets = {}
    for card in unseen:
        buckets.setdefault(card['topic'], []).append(card)
    fresh = []
    topics = sorted(buckets)
    while len(fresh) < new_per_day and any(buckets.values()):
        for topic in topics:
            if buckets[topic]:
                fresh.append(buckets[topic].pop(0))
            if len(fresh) >= new_per_day:
                break
    return reviews + fresh


def session_cards(queue, cap=SESSION_MAX):
    return list(queue[:cap])


def due_count(queue):
    return len(queue)


def _slug(text, n=24):
    s = re.sub(r'[^a-z0-9]+', '-', (text or '').lower()).strip('-')
    return s[:n] or 'card'


def _options(card_id, answer, pool):
    pool = [p for p in pool if p and p != answer]
    rng = random.Random(card_id)
    wrong = rng.sample(pool, 3) if len(pool) >= 3 else list(pool)
    opts = [answer] + wrong
    rng.shuffle(opts)
    return opts


def build_cards(ports, commands, terms):
    """ports: (service, answer, courses). commands: (prompt, answer, aliases, courses).
    terms: (prompt, answer, topic, courses)."""
    cards = []
    port_pool = []
    service_by_answer = {}
    for service, answer, courses in ports:
        cid = 'port-' + _slug(service)
        port_pool.append(answer)
        service_by_answer.setdefault(answer, []).append((service, courses))
        cards.append({
            'id': cid, 'kind': 'concept', 'topic': 'port', 'courses': tuple(courses),
            'prompt': f'Which port does {service} use?', 'answer': answer,
            'accept': [answer], 'pool': 'port',
        })
    for answer, owners in service_by_answer.items():
        if len(owners) != 1:
            continue
        service, courses = owners[0]
        cards.append({
            'id': 'svc-' + _slug(answer + '-' + service), 'kind': 'concept', 'topic': 'protocol',
            'courses': tuple(courses),
            'prompt': f'Which service uses {answer}?', 'answer': service,
            'accept': [service], 'pool': 'service',
        })
    for prompt, answer, aliases, courses in commands:
        acc = [answer] + list(aliases or [])
        cards.append({
            'id': 'cmd-' + _slug(prompt), 'kind': 'command', 'topic': 'command',
            'courses': tuple(courses), 'prompt': prompt, 'answer': answer,
            'accept': acc, 'pool': '',
        })
    term_pools = {}
    term_rows = []
    for prompt, answer, topic, courses in terms:
        term_pools.setdefault(topic, []).append(answer)
        term_rows.append((prompt, answer, topic, courses))
    for prompt, answer, topic, courses in term_rows:
        cards.append({
            'id': 'term-' + _slug(prompt), 'kind': 'concept', 'topic': topic,
            'courses': tuple(courses), 'prompt': prompt, 'answer': answer,
            'accept': [answer], 'pool': topic,
        })
    pools = {'port': port_pool, 'service': [s for s, _a, _c in ports]}
    for topic, answers in term_pools.items():
        pools[topic] = answers
    seen = set()
    out = []
    for card in cards:
        if card['id'] in seen:
            card = dict(card, id=card['id'] + '-' + str(len(seen)))
        seen.add(card['id'])
        if card['kind'] == 'concept':
            card['options'] = _options(card['id'], card['answer'], pools.get(card['pool']) or [])
        else:
            card['options'] = []
        out.append(card)
    out.sort(key=lambda c: c['id'])
    return out


def public_card(card):
    """Fields safe to send to the browser. The answer stays on the server."""
    row = {'id': card['id'], 'kind': card['kind'], 'topic': card['topic'], 'prompt': card['prompt']}
    if card['kind'] == 'concept':
        row['options'] = list(card['options'])
    return row


def score_card(card, raw):
    if card['kind'] == 'command':
        return typed_quality(raw, card['accept'])
    return choice_quality(raw, card['answer'])


def load_cards():
    from .deck_data import COMMANDS, PORTS, TERMS
    return build_cards(PORTS, COMMANDS, TERMS)


_CARDS = None


def cards():
    global _CARDS
    if _CARDS is None:
        _CARDS = load_cards()
    return _CARDS


def card_by_id(card_id):
    return next((c for c in cards() if c['id'] == card_id), None)


def streak_after(streak, last_completed, today, finished):
    """New streak once today's sitting is finished. Same-day repeats do not add a day."""
    if not finished:
        return streak or 0, last_completed
    if last_completed == today:
        return streak or 1, last_completed
    if last_completed == today - timedelta(days=1):
        return (streak or 0) + 1, today
    return 1, today
