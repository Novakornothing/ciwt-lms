"""Security topic prose must be real English, not a repeated opening or invented words."""
import ast
import collections
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BODIES = ROOT / 'curriculum_sec' / 'bodies'
WORDS = ROOT / 'curriculum_sec' / 'words' / 'en_US.txt'
ALLOW = ROOT / 'curriculum_sec' / 'words' / 'security_allowlist.txt'

# Adverbs that were stuffed into generated sentences to fake variety.
FILLER_ADVERBS = {
    'briskly', 'specifically', 'firstly', 'secondly', 'outerward', 'upperly',
    'lowerwise', 'briskwise', 'briskward', 'calmward', 'calmlyward',
}

def _label_prefix(sentence, name):
    """A sentence that starts with the topic name and a colon, used to dodge opening checks."""
    if ':' not in sentence[: len(name) + 8]:
        return False
    prefix = sentence.split(':', 1)[0].strip().lower()
    first = name.split()[0].lower()
    return prefix == name.lower() or prefix == first


def _sentences(text):
    text = re.sub(r'\s+', ' ', text or '').strip()
    return [part.strip() for part in re.split(r'(?<=[.!?])\s+', text) if part.strip()]


def _tokens(text):
    return re.findall(r"[A-Za-z0-9']+(?:-[A-Za-z0-9']+)*", text or '')


def _lexicon():
    words = set()
    for line in WORDS.read_text(encoding='utf-8').splitlines():
        word = line.strip().lower()
        if word:
            words.add(word)
    expanded = set(words)
    for word in words:
        expanded.add(word + 's')
        expanded.add(word + 'es')
        expanded.add(word + 'ed')
        expanded.add(word + 'ing')
        expanded.add(word + 'ly')
        expanded.add(word + 'er')
        expanded.add(word + 'est')
        if word.endswith('e'):
            expanded.add(word[:-1] + 'ing')
            expanded.add(word + 'd')
        if len(word) > 2 and word.endswith('y') and word[-2] not in 'aeiou':
            expanded.add(word[:-1] + 'ies')
            expanded.add(word[:-1] + 'ied')
    expanded.update('has had having is are was were been being does did doing goes went gone '
                    'its his her hers their our your'.split())
    allow = set()
    if ALLOW.exists():
        allow = {line.strip().lower() for line in ALLOW.read_text(encoding='utf-8').splitlines() if line.strip()}
    return expanded, allow


def _known(token, lexicon, allow):
    if any(ch.isdigit() for ch in token):
        return True
    if '-' in token:
        return all(_known(part, lexicon, allow) for part in token.split('-') if part)
    low = token.lower().strip("'")
    if not low:
        return True
    cands = [low]
    if low.endswith("'s"):
        cands.append(low[:-2])
    return any(cand in lexicon or cand in allow for cand in cands)


def _bodies():
    found = {}
    for path in sorted(BODIES.glob('g*.py')):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'BODIES':
                    found.update(ast.literal_eval(node.value))
    return found


def _blob(row):
    return '\n'.join(row.get(key, '') for key in ('body', 'r0', 'r1', 'r2', 'r4', 'exam'))


def test_openings_and_sentences_are_not_repeated():
    bodies = _bodies()
    assert len(bodies) == 491
    opening_hits = []
    seen = {}
    shared = []
    for name, row in bodies.items():
        text = row.get('body') or ''
        counts = collections.Counter(
            ' '.join(_tokens(sentence)[:4]).lower()
            for sentence in _sentences(text)
            if len(_tokens(sentence)) >= 4
        )
        for opening, count in counts.items():
            if count > 2:
                opening_hits.append(f'{name}: {opening!r} x{count}')
        for sentence in _sentences(text):
            if len(_tokens(sentence)) < 6:
                continue
            key = re.sub(r'\s+', ' ', sentence.lower())
            prior = seen.get(key)
            if prior and prior != name:
                shared.append(f'{prior} and {name}: {sentence[:90]}')
            else:
                seen[key] = name
    assert opening_hits == [], opening_hits[:12]
    assert shared == [], shared[:12]


def test_topic_names_do_not_open_most_sentences():
    bodies = _bodies()
    bad = []
    for name, row in bodies.items():
        sentences = _sentences(row.get('body') or '')
        if not sentences:
            bad.append(f'{name}: empty body')
            continue
        first = name.split()[0].lower()
        named = 0
        for sentence in sentences:
            low = sentence.lower()
            if low.startswith(name.lower()) or low.startswith(first + ' ') or low.startswith(first + ':'):
                named += 1
        if named / len(sentences) > 0.30:
            bad.append(f'{name}: {named}/{len(sentences)} start with the topic name')
    assert bad == [], bad[:15]


def test_no_label_prefixes_unknown_words_or_stuffed_adverbs():
    bodies = _bodies()
    lexicon, allow = _lexicon()
    prefixes = []
    unknown = []
    adverbs = []
    for name, row in bodies.items():
        blob = _blob(row)
        for sentence in _sentences(blob):
            if _label_prefix(sentence, name):
                prefixes.append(f'{name}: {sentence[:80]}')
        counts = collections.Counter()
        for token in _tokens(blob):
            low = token.lower().strip("'")
            if low in FILLER_ADVERBS:
                counts[low] += 1
            if not _known(token, lexicon, allow):
                unknown.append(f'{name}: {token}')
        for word, count in counts.items():
            if count > 3:
                adverbs.append(f'{name}: {word} x{count}')
    assert prefixes == [], prefixes[:12]
    assert unknown == [], unknown[:20]
    assert adverbs == [], adverbs[:12]
