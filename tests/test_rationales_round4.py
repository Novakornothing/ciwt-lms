"""Content round 4: the last one-line chapter-check rationales (spot-check round 3 listed 23 ITSUP items) now explain
why the key is right and why each distractor is wrong, with a source, and are marked Pending SME review.

"Thin" is the round-3 measure: a served rationale under 90 characters that starts with a section pointer
("1.1 — …", "2.1 / hw-board card — …"). Measured on what is served: the quiz payloads and the engine's course map."""
import re

import pilot_slice as PS
from curriculum_v2 import rationales_round4 as R4
from curriculum_v2.netops_checks import NETOPS_CHECKS, netops_quiz_payload

PTR = re.compile(r'^\s*\d+(\.\d+)?(\s*/\s*[\w .-]+?)*\s*[—–-]\s')
ROUND3_THIN = ['Q1.0', 'Q1.1', 'Q1.5', 'Q1.6', 'Q1.8', 'Q2.0', 'Q2.1', 'Q2.2', 'Q2.4', 'Q2.5', 'Q2.6', 'Q2.8', 'Q4.0',
               'Q4.2', 'Q4.3', 'Q4.6', 'Q5.7', 'Q6.0', 'Q6.1', 'Q6.6', 'Q6.7', 'Q7.0', 'Q7.3']
# keys as served before round 4 (keys, stems and options must not change)
KEYS = {'Q1.0': 'Service request', 'Q1.1': 'Incident', 'Q1.5': 'Classify incident, stop, escalate', 'Q1.6': 'A change', 'Q1.8': 'classify incident, impact many, escalate yes', 'Q2.0': 'microATX', 'Q2.1': 'socket lga1700', 'Q2.2': 'memory ddr5', 'Q2.4': 'post memory', 'Q2.5': 'Before Windows, to check hardware and start boot', 'Q2.6': 'Firmware starts only a signed bootloader', 'Q2.8': 'CPU_FAN, the header firmware monitors', 'Q4.0': 'Stop — suspected swollen pack, battery procedure', 'Q4.2': 'No. Isolate the WLAN / portal / proxy', 'Q4.3': 'Shop-managed enrollment you do not sidestep', 'Q4.6': 'App → spooler → driver/port → link → device', 'Q5.7': 'No. Fix admin password, guest isolation, access', 'Q6.0': 'A guest PC made of files, running on a host', 'Q6.1': 'Host or shared virtual switch / uplink', 'Q6.6': 'A full datastore and slow guests', 'Q6.7': 'The hypervisor owner (vNIC, port group, uplink)', 'Q7.0': 'Identify who, what, how many, safety', 'Q7.3': 'The outcome the user called about works', 'NQ5.5': 'Events from many devices can be correlated in order'}


def thin(e):
    e = (e or '').strip()
    return len(e) < 90 and bool(PTR.match(e))


def _payload():
    its = [q for o in sorted(PS.PILOT_CHECKS) for q in PS.quiz_payload(o, '')]
    net = [q for o in sorted(NETOPS_CHECKS) for q in netops_quiz_payload(o)]
    return its, net


def test_measure_still_recognises_the_round3_one_liners():
    assert thin('1.1 — new access is a request, not a repair.')
    assert thin('2.1 / hw-board card — measure the board, not the case slogan.')
    assert thin('7.3 / 1.1 — closing is not the same as fixed.')
    assert not thin('Routers choose the longest matching prefix; /16 is more specific than /8.')


def test_no_chapter_check_item_has_a_thin_rationale_in_the_payloads():
    its, net = _payload()
    assert len(its) + len(net) == 200
    assert [q['bank_id'] for q in its + net if thin(q['explanation'])] == []


def test_no_chapter_check_item_has_a_thin_rationale_as_the_engine_serves_it(app, mod):
    with app.app_context():
        eng = app.extensions['ciwt_mastery'].engine
        served = []
        for code in ('ITSUP', 'NETOPS'):
            course = mod.Course.query.filter_by(code=code).first()
            sec = mod.ClassSection.query.filter_by(course_id=course.id).first()
            served += eng.course_map(sec)['check_items']
    by = {it.get('bank_id'): it for it in served}
    assert set(ROUND3_THIN) | {'NQ5.5'} <= set(by)
    assert [b for b, it in by.items() if thin(it.get('explanation') or it.get('study_tip'))] == []
    for k in ROUND3_THIN + ['NQ5.5']:
        assert by[k]['explanation'] == R4.served(k)


def test_round4_rationales_are_full_sourced_pending_and_keys_unchanged():
    its, net = _payload()
    by = {q['bank_id']: q for q in its + net}
    assert set(R4.RATIONALE) == set(ROUND3_THIN) | {'NQ5.5'} == set(R4.SOURCE) == set(KEYS)
    for k in R4.RATIONALE:
        q = by[k]
        assert q['correct'] == KEYS[k], k
        assert q['explanation'] == f'{R4.RATIONALE[k]} Source: {R4.SOURCE[k]}.'
        assert len(R4.RATIONALE[k].split()) >= 45, k                      # key and every distractor addressed
        assert 'Pending SME review' in q.get('review', ''), k
        if k.startswith('Q'):
            assert re.search(r'See \d+\.\d+(\s*/\s*[\w -]+(\.\d+)?)?\.$', R4.RATIONALE[k]), k    # original section pointer kept


def test_every_distractor_is_answered_in_the_round4_rationale():
    """Each distractor's distinctive word (longest word not shared with the key) appears in the rationale."""
    its, net = _payload()
    by = {q['bank_id']: q for q in its + net}
    stop = {'the', 'and', 'with', 'from', 'that', 'this', 'when', 'only', 'first', 'every', 'each'}
    misses = []
    for k, why in R4.RATIONALE.items():
        q, low = by[k], why.lower()
        keyw = set(re.findall(r'[a-z0-9_]+', q['correct'].lower()))
        for d in q['options']:
            if d == q['correct']:
                continue
            words = [w for w in re.findall(r'[a-z0-9_]+', d.lower()) if w not in keyw and w not in stop and len(w) > 2]
            if words and not any(w in low or w.rstrip('s') in low for w in words):
                misses.append((k, d))
    assert misses == []
