"""Original teaching rows for Security.

Each row is one section. The paraphrase of the exam idea is in the name and the gist.
Nothing here is copied from a vendor objective list or a commercial study guide.
"""


def R(ch, bid, name, gist, scene, mix, noun, story, plain, key, bad1, bad2):
    return (ch, bid, name, gist, scene, mix, noun, story, plain, key, bad1, bad2)


from curriculum_sec.d1 import ROWS as _D1
from curriculum_sec.d1b import ROWS as _D1B
from curriculum_sec.d1c import ROWS as _D1C
from curriculum_sec.d2 import ROWS as _D2
from curriculum_sec.d2b import ROWS as _D2B
from curriculum_sec.d3 import ROWS as _D3
from curriculum_sec.d4 import ROWS as _D4
from curriculum_sec.d4b import ROWS as _D4B
from curriculum_sec.d5 import ROWS as _D5

ROWS = _D1 + _D1B + _D1C + _D2 + _D2B + _D3 + _D4 + _D4B + _D5
