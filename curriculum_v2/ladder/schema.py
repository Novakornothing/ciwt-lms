"""Explanation ladder: content model, authoring helpers and validator (schema v1, pass 19).

One concept section of a lesson (see sections.py) gets a ladder of genuinely different explanations:

  R0  the original section, unchanged (the lesson as written)
  R1  plain    simpler plain language: short sentences, everyday words, one idea at a time
  R2  analogy  a different analogy or real-world story that maps onto the idea
  R3  visual   a diagram (inline SVG/HTML) or a numbered step-by-step trace
  R4  try      a hands-on "try it": a mini interactive (order / sort / reveal) and/or a link into the matching lab

Every rung (and R0) carries 1-2 quick checks that test the same idea in a different way, with misconception tags on
the distractors. Everything authored here is 'Pending SME review' and names its source.

Authoring uses the helpers below (section, plain, analogy, visual, tryit, check, order, sort, reveal, same_as,
skip); see docs/EXPLANATION_LADDER.md and curriculum_v2/ladder/itsup/ch01.py for a complete worked example.
"""
import hashlib
import re

SCHEMA = 1
REVIEW = 'Pending SME review'
COURSES = ('ITSUP', 'NETOPS', 'CLIENT', 'SEC')
RUNGS = ('R1', 'R2', 'R3', 'R4')
KIND = {'R1': 'plain', 'R2': 'analogy', 'R3': 'visual', 'R4': 'try'}
LABEL = {'R0': 'Original explanation', 'R1': 'Explained more simply', 'R2': 'Explained another way: analogy',
         'R3': 'Explained another way: step by step', 'R4': 'Explained another way: try it'}
SKIP_REASONS = {
    'plan': 'a timing or hour plan for the class, not an explanation',
    'activity': 'a drill or exercise that is itself practice (the ladder would explain an activity, not a concept)',
    'orientation': 'a start-here list, vocabulary list or signpost with no single concept to re-explain',
    'reference': 'reference material (tables or lists to look up) rather than a concept',
}
WIDGETS = ('order', 'sort', 'reveal')
MIN_WORDS = {'R1': 40, 'R2': 50, 'R3': 30, 'R4': 15}
MAX_SIMILARITY = 0.55          # token Jaccard between two explanations of one section; above this = paraphrase

_TAG = re.compile(r'<[^>]+>')
_WORD = re.compile(r"[a-z0-9][a-z0-9'\-]*")
_UNSAFE = re.compile(r'<\s*(script|iframe|object|embed|form|style|link|meta)\b|\son[a-z]+\s*=|javascript:|\ssrc\s*=\s*["\']?(https?:)?//', re.I)


# ---------------------------------------------------------------- authoring helpers
def check(q, correct, wrong, why, mc=None):
    """A quick check. wrong: 2-3 distractors. mc: list aligned with wrong (None = untagged) or {distractor: mc_id}."""
    wrong = list(wrong)
    if isinstance(mc, (list, tuple)):
        mc = {d: t for d, t in zip(wrong, mc) if t}
    return {'q': q, 'correct': correct, 'wrong': wrong, 'why': why, 'mc': dict(mc or {}), 'review': REVIEW}


def _rung(kind, html, source, checks, title=None, **extra):
    r = {'kind': kind, 'html': html.strip(), 'source': source, 'checks': list(checks), 'review': REVIEW}
    if title:
        r['title'] = title
    r.update({k: v for k, v in extra.items() if v is not None})
    return r


def plain(html, source, checks, title=None):
    return _rung('plain', html, source, checks, title)


def analogy(html, source, checks, title=None):
    return _rung('analogy', html, source, checks, title)


def visual(html, source, checks, title=None):
    return _rung('visual', html, source, checks, title)


def tryit(html, source, checks, widget=None, lab=None, title=None):
    """widget: order(...), sort(...) or reveal(...). lab: {'id': lab id, 'note': what to do there}."""
    return _rung('try', html, source, checks, title, widget=widget, lab=lab)


def order(prompt, steps, done):
    """Put the steps in order. steps: the correct order (shown shuffled). done: what the student should notice."""
    return {'type': 'order', 'prompt': prompt, 'steps': list(steps), 'done': done}


def sort(prompt, buckets, done):
    """Sort items into buckets. buckets: {bucket label: [items that belong there]}."""
    return {'type': 'sort', 'prompt': prompt, 'buckets': {k: list(v) for k, v in buckets.items()}, 'done': done}


def reveal(prompt, answer):
    """Predict first, then reveal: the student commits to an answer in their head (or types it), then opens it."""
    return {'type': 'reveal', 'prompt': prompt, 'answer': answer}


def section(heading, obj, checks, R1, R2, R3, R4, r0_sha=None, note=None):
    """A fully laddered concept section. heading: the section's <h3> text (checked against the lesson).
    checks: the R0 micro-check (1-2) shown after the original. r0_sha: sections.r0_sha of the original when the
    rungs were written (tools/ladder_check.py --stamp fills it in)."""
    return {'type': 'section', 'heading': heading, 'obj': obj, 'checks': list(checks),
            'rungs': {'R1': R1, 'R2': R2, 'R3': R3, 'R4': R4}, 'r0_sha': r0_sha, 'note': note, 'review': REVIEW}


def same_as(sid, heading, note=''):
    """This section restates the same concept as another section of the same lesson: it uses that ladder."""
    return {'type': 'same_as', 'target': sid, 'heading': heading, 'note': note}


def skip(heading, reason, note):
    """Not a concept section (reason in SKIP_REASONS). Shown as-is with no micro-check; counted in coverage."""
    return {'type': 'skip', 'heading': heading, 'reason': reason, 'note': note}


# ---------------------------------------------------------------- derived values
def words(html):
    return _WORD.findall(_TAG.sub(' ', (html or '').lower()).replace('’', "'"))


def similarity(a, b):
    sa, sb = set(w for w in words(a) if len(w) > 3), set(w for w in words(b) if len(w) > 3)
    return len(sa & sb) / len(sa | sb) if sa and sb else 0.0


def options(chk):
    """Deterministic option order (hash of the question), so the key is not always first."""
    opts = [chk['correct']] + list(chk['wrong'])
    return sorted(opts, key=lambda o: hashlib.sha256((chk['q'] + '|' + o).encode()).hexdigest())


def check_id(course, label, sid, rung, i):
    return f'L-{course}-{label}-{sid}-{rung}-{i + 1}'


def widget_text(wd):
    if not wd:
        return ''
    parts = [wd.get('prompt', ''), wd.get('done', ''), wd.get('answer', '')] + list(wd.get('steps') or [])
    for k, v in (wd.get('buckets') or {}).items():
        parts += [k] + list(v)
    return ' '.join(parts)


def all_checks(mod):
    for label, secs in (getattr(mod, 'LESSONS', {}) or {}).items():
        for sid, ent in secs.items():
            if ent.get('type') == 'section':
                yield from ent.get('checks') or []
                for g in (ent.get('rungs') or {}).values():
                    yield from (g or {}).get('checks') or []


def key_longest_share(mod):
    cs = list(all_checks(mod))
    n = sum(1 for c in cs if c.get('wrong') and len(c['correct']) > max(len(w) for w in c['wrong']))
    return n, len(cs)


MAX_KEY_LONGEST = 0.30         # same rule as the chapter-check audit (pass 15): chance with 3 options is ~33%


# ---------------------------------------------------------------- validation
def validate_module(mod, objectives, misconceptions, labs=None):
    """Static checks of one ladder module. Returns (errors, warnings) as lists of strings."""
    E, W = [], []
    name = getattr(mod, '__name__', '?')
    if getattr(mod, 'SCHEMA', None) != SCHEMA:
        E.append(f'{name}: SCHEMA must be {SCHEMA}')
    course = getattr(mod, 'COURSE', None)
    if course not in COURSES:
        E.append(f'{name}: COURSE must be one of {COURSES}')
    if not isinstance(getattr(mod, 'CHAPTER', None), int):
        E.append(f'{name}: CHAPTER must be an int (module order in the course)')
    local_mc = getattr(mod, 'MISCONCEPTIONS', {}) or {}
    for mid, m in local_mc.items():
        if not mid.startswith('MC-L-'):
            E.append(f'{name}: new misconception ids start with MC-L- ({mid})')
        for f in ('obj', 'label', 'fix', 'terms', 'source'):
            if not m.get(f):
                E.append(f'{name}: {mid} needs {f}')
        if m.get('review') != REVIEW:
            E.append(f'{name}: {mid} review must be {REVIEW!r}')
        if m.get('obj') and m['obj'] not in objectives:
            E.append(f'{name}: {mid} obj {m["obj"]} is not a course objective')
    all_mc = dict(misconceptions)
    all_mc.update(local_mc)
    lessons = getattr(mod, 'LESSONS', None)
    if not isinstance(lessons, dict) or not lessons:
        E.append(f'{name}: LESSONS must be a non-empty dict {{"1.1": {{sid: entry}}}}')
        return E, W
    n, tot = key_longest_share(mod)
    if tot and n / tot > MAX_KEY_LONGEST:
        E.append(f'{name}: the key is the uniquely longest option in {n}/{tot} checks ({100 * n / tot:.0f}%); '
                 f'balance option lengths to {int(100 * MAX_KEY_LONGEST)}% or less')
    for label, secs in lessons.items():
        if not re.fullmatch(r'\d+\.\d+', label):
            E.append(f'{name}: lesson key {label!r} must be the lesson label, e.g. "1.1"')
        for sid, ent in secs.items():
            where = f'{course} {label} {sid}'
            t = ent.get('type')
            if t == 'skip':
                if ent.get('reason') not in SKIP_REASONS:
                    E.append(f'{where}: skip reason must be one of {sorted(SKIP_REASONS)}')
                if len(words(ent.get('note'))) < 4:
                    E.append(f'{where}: skip needs a note saying why')
                continue
            if t == 'same_as':
                tgt = secs.get(ent.get('target'))
                if not tgt or tgt.get('type') != 'section':
                    E.append(f'{where}: same_as must name a laddered section of the same lesson')
                continue
            if t != 'section':
                E.append(f'{where}: unknown entry type {t!r}')
                continue
            _validate_section(where, ent, objectives, all_mc, labs, E, W)
    return E, W


def _validate_checks(where, chks, obj, mc, E, W, lo=1, hi=2):
    if not lo <= len(chks) <= hi:
        E.append(f'{where}: needs {lo}-{hi} checks (has {len(chks)})')
    for i, c in enumerate(chks, 1):
        w = f'{where} check {i}'
        if not c.get('q') or not c.get('correct'):
            E.append(f'{w}: question and correct answer required')
        wrong = c.get('wrong') or []
        if not 2 <= len(wrong) <= 3 or len(set(wrong)) != len(wrong) or c.get('correct') in wrong:
            E.append(f'{w}: 2-3 distinct distractors, none equal to the key')
        if len(words(c.get('why'))) < 10:
            E.append(f'{w}: "why" needs at least 10 words (why the key is right and the distractor wrong)')
        tags = c.get('mc') or {}
        if not tags:
            E.append(f'{w}: tag at least one distractor with a misconception')
        for d, t in tags.items():
            if d not in wrong:
                E.append(f'{w}: tagged text {d[:40]!r} is not one of the distractors')
            if t not in mc:
                E.append(f'{w}: unknown misconception {t}')
            elif mc[t].get('obj') and obj and mc[t]['obj'].split('.')[0] != obj.split('.')[0]:
                W.append(f'{w}: {t} belongs to {mc[t]["obj"]}, section objective is {obj}')
        if c.get('review') != REVIEW:
            E.append(f'{w}: review must be {REVIEW!r}')
        longest = max([c.get('correct') or ''] + wrong, key=len)
        if longest == c.get('correct') and all(len(c['correct']) > 1.15 * len(x) for x in wrong):
            W.append(f'{w}: the key is clearly the longest option')


def _validate_section(where, s, objectives, mc, labs, E, W):
    if not s.get('heading'):
        E.append(f'{where}: heading required')
    obj = s.get('obj')
    if obj not in objectives:
        E.append(f'{where}: obj {obj!r} is not a course objective')
    _validate_checks(f'{where} R0', s.get('checks') or [], obj, mc, E, W)
    rungs = s.get('rungs') or {}
    qs = [c['q'] for c in s.get('checks') or []]
    texts = {}
    for r in RUNGS:
        g = rungs.get(r)
        w = f'{where} {r}'
        if not g:
            E.append(f'{w}: missing')
            continue
        if g.get('kind') != KIND[r]:
            E.append(f'{w}: kind must be {KIND[r]!r}')
        html = g.get('html') or ''
        n = len(words(html)) + (len(words(widget_text(g.get('widget')))) if r == 'R4' else 0)
        if n < MIN_WORDS[r]:
            E.append(f'{w}: at least {MIN_WORDS[r]} words (has {n})')
        if _UNSAFE.search(html):
            E.append(f'{w}: html may not contain scripts, event handlers, forms, styles or remote src')
        if not (g.get('source') or '').strip():
            E.append(f'{w}: source required')
        if g.get('review') != REVIEW:
            E.append(f'{w}: review must be {REVIEW!r}')
        if r == 'R3' and not re.search(r'<svg\b|<ol\b', html):
            E.append(f'{w}: a visual rung needs an inline <svg> diagram or a numbered <ol> trace')
        if r == 'R3' and '<svg' in html and not re.search(r'<svg\b[^>]*(role="img"|aria-label)', html):
            E.append(f'{w}: an <svg> needs role="img" and an aria-label (or <title>)')
        if r == 'R4':
            wd, lab = g.get('widget'), g.get('lab')
            if not wd and not lab:
                E.append(f'{w}: a try-it rung needs a widget (order/sort/reveal) or a lab link')
            if wd:
                if wd.get('type') not in WIDGETS:
                    E.append(f'{w}: widget type must be one of {WIDGETS}')
                elif wd['type'] == 'order' and len(wd.get('steps') or []) < 3:
                    E.append(f'{w}: an order widget needs at least 3 steps')
                elif wd['type'] == 'sort' and (len(wd.get('buckets') or {}) < 2 or sum(len(v) for v in wd['buckets'].values()) < 4):
                    E.append(f'{w}: a sort widget needs 2+ buckets and 4+ items')
                elif wd['type'] == 'reveal' and not (wd.get('prompt') and wd.get('answer')):
                    E.append(f'{w}: a reveal widget needs a prompt and an answer')
            if lab and labs is not None and lab.get('id') not in labs:
                E.append(f'{w}: lab {lab.get("id")!r} does not exist')
        _validate_checks(w, g.get('checks') or [], obj, mc, E, W)
        for c in g.get('checks') or []:
            if c.get('q') in qs:
                E.append(f'{w}: check question repeats another check in this section')
            qs.append(c.get('q'))
        texts[r] = html
    for a in texts:
        for b in texts:
            if a < b and similarity(texts[a], texts[b]) > MAX_SIMILARITY:
                E.append(f'{where}: {a} and {b} are too similar ({similarity(texts[a], texts[b]):.2f}); rungs must differ')


def validate_against_lesson(where, ent, r0_html, r0_sha_now, E, W):
    """Checks that need the lesson itself: heading match, rungs differ from the original, stale originals."""
    from .sections import text_of
    if ent.get('type') == 'section':
        for r, g in (ent.get('rungs') or {}).items():
            sim = similarity(r0_html, g.get('html') or '')
            if sim > MAX_SIMILARITY:
                E.append(f'{where} {r}: too close to the original ({sim:.2f}); write a genuinely different explanation')
        if ent.get('r0_sha') and ent['r0_sha'] != r0_sha_now:
            W.append(f'{where}: the original changed since these rungs were written (r0_sha {ent["r0_sha"]} -> {r0_sha_now}); re-review')
        r1 = (ent.get('rungs') or {}).get('R1') or {}

        def avg_sentence(h):
            t = text_of(h)
            ss = [s for s in re.split(r'[.!?]+\s', t) if s.strip()]
            return sum(len(s.split()) for s in ss) / len(ss) if ss else 0
        if r1.get('html') and avg_sentence(r1['html']) > max(18, avg_sentence(r0_html)):
            W.append(f'{where} R1: sentences are not shorter than the original (plain-language rung)')
