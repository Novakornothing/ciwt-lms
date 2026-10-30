"""Security topic prose must teach, not repeat a sentence opening."""
import ast
import collections
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'curriculum_sec' / 'bodies'


def _sentences(text):
    text = re.sub(r'\s+', ' ', text or '').strip()
    return [part.strip() for part in re.split(r'(?<=[.!?])\s+', text) if part.strip()]


def _words(sentence):
    return re.findall(r"[A-Za-z0-9']+", sentence)


def _opening(sentence):
    return ' '.join(_words(sentence)[:4]).lower()


def _bodies():
    found = {}
    for path in sorted(ROOT.glob('g*.py')):
        tree = ast.parse(path.read_text(encoding='utf-8'))
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'BODIES':
                    found.update(ast.literal_eval(node.value))
    return found


def test_openings_and_sentences_are_not_repeated():
    bodies = _bodies()
    assert len(bodies) == 491
    opening_hits = []
    seen = {}
    shared = []
    for name, row in bodies.items():
        text = row.get('body') or ''
        counts = collections.Counter(
            _opening(sentence) for sentence in _sentences(text) if len(_words(sentence)) >= 4
        )
        for opening, count in counts.items():
            if count > 2:
                opening_hits.append(f'{name}: {opening!r} x{count}')
        for sentence in _sentences(text):
            if len(_words(sentence)) < 6:
                continue
            key = re.sub(r'\s+', ' ', sentence.lower())
            prior = seen.get(key)
            if prior and prior != name:
                shared.append(f'{prior} and {name}: {sentence[:90]}')
            else:
                seen[key] = name
    assert opening_hits == [], opening_hits[:12]
    assert shared == [], shared[:12]
