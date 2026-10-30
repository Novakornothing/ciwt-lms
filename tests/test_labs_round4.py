"""Round-4 real Linux VM labs (labs_vm_r4.py): registration, course mapping, SME tag, hints, fallbacks, and the
process rules that make them more than a typed answer (order of evidence, network evidence, answers not in the probe).
The real-machine runs (solution → complete, nothing → only boot) are in tests/test_vm_real.py, which covers every
VM lab including these five."""
import json

import interactive_labs as IL
import lab_runtime as RT
import labs_vm as V
from curriculum_v2.objectives import OBJECTIVES

R4 = ["linux-vm-perf", "linux-vm-restore", "linux-vm-web", "linux-vm-nat", "linux-vm-incident", "linux-vm-ipv6"]


def _j(r):
    assert r.status_code == 200, (r.status_code, r.data[:300])
    return r.get_json()


def _state(lab_id, email="student1@lms.local"):
    import app as lms
    api = lms.app.extensions["ciwt_lab_progress"]
    with lms.app.app_context():
        u = lms.User.query.filter_by(email=email).first()
        return json.loads(api.LabProgress.query.filter_by(user_id=u.id, lab_id=lab_id).first().state_json)


def _grade(lab, cmds, fabric=None):
    st = V.fresh(lab, 7)
    V.record_commands(st, cmds)
    res, st, done = V.grade(lab, st, [], V.solved_probes(st, lab), booted=True, fabric=fabric)
    return done


def test_round4_labs_are_registered_mapped_and_tagged():
    for lid in R4:
        lab = RT.get_lab(lid)
        assert lab and lab["kind"] == "vm" and lid in V.VM_BY_ID, lid
        assert lab.get("review") == IL.SME_PENDING, lid
        assert all(o in OBJECTIVES for o in lab["course_objectives"]), lid
        assert any(lid in ids for ids in IL.CHAPTER_LABS.values()), lid
        assert set(lab["obj_hints"]) == {o["id"] for o in lab["objectives"]}, lid
        assert all(len(h) == 2 and all(x.strip() for x in h) for h in lab["obj_hints"].values()), lid
        assert lab["fallback"] and all(RT.get_lab(f) and RT.get_lab(f)["kind"] != "vm" for f in lab["fallback"]), lid
        json.dumps(lab["vm"]), json.dumps(lab["vm_checks"])


def test_round4_solution_history_earns_everything_and_empty_earns_only_boot():
    for lid in R4:
        lab = V.VM_BY_ID[lid]
        want = sorted(o["id"] for o in lab["objectives"])
        assert sorted(_grade(lab, lab["solution"]["vm_commands"], lab["solution"].get("fabric"))) == want, lid
        st = V.fresh(lab, 7)
        _, _, done = V.grade(lab, st, [], {}, booted=True)
        assert done == [] or done == ["boot"], (lid, done)


def test_round4_evidence_must_come_before_the_change():
    perf = V.VM_BY_ID["linux-vm-perf"]
    done = _grade(perf, ["killall thumbgen", "uptime", "free", "top -b -n 1"])
    assert "baseline" not in done and "identify" in done
    rs = V.VM_BY_ID["linux-vm-restore"]
    done = _grade(rs, ["zcat /backup/share-20261016-0100.tar.gz | tar -xf - -C /srv/share", "cd /backup", "sha256sum -c SHA256SUMS",
                       "zcat share-20261016-0100.tar.gz | tar -tf -", "ls -l /srv/share/finance/budget-2027"])
    assert "inspect" not in done and "verified" in done
    web = V.VM_BY_ID["linux-vm-web"]
    done = _grade(web, ["[srv] sed -i 's/^ADDR=127.0.0.1/ADDR=0.0.0.0/' /etc/default/intranet", "[ws] curl -s http://app-05/",
                        "[srv] curl -s http://127.0.0.1/", "[srv] chmod 644 /srv/www/reports/q3.html", "[ws] curl -s http://app-05/reports/q3.html"])
    assert "scope" not in done and "forbidden" not in done
    nat = V.VM_BY_ID["linux-vm-nat"]
    done = _grade(nat, ["[rtr] iptables -t nat -A POSTROUTING -s 10.5.0.0/24 -o eth0 -j MASQUERADE", "[pc] ping -c 2 203.0.113.10",
                        "[rtr] ping -c 2 203.0.113.10", "[rtr] tcpdump -nr /tmp/before.pcap"], nat["solution"]["fabric"])
    assert "symptom" not in done and "capture" in done


def test_round4_nat_needs_real_network_evidence():
    nat = V.VM_BY_ID["linux-vm-nat"]
    cmds = nat["solution"]["vm_commands"]
    done = _grade(nat, cmds, {"events": []})
    assert "capture" not in done and "reach" not in done
    # the internet saw the private source (before NAT) but never the public one: reach stays open
    done = _grade(nat, cmds, {"events": [{"type": "ping", "from": "10.5.0.10", "to": "203.0.113.10"}]})
    assert "capture" in done and "reach" not in done


def test_round4_answers_are_hashed_not_in_the_probe():
    st = V.fresh(V.VM_BY_ID["linux-vm-restore"], 1)
    probe = V.probe_script(st, V.VM_BY_ID["linux-vm-restore"])
    assert "share-20261016" not in probe and "share-20261017" not in probe
    st = V.fresh(V.VM_BY_ID["linux-vm-web"], 1)
    srv = V.probe_scripts(st, V.VM_BY_ID["linux-vm-web"])["srv"]
    assert "bound=" not in srv and "403" not in srv


def test_round4_ipv6_order_link_local_scope_and_live_record():
    v6 = V.VM_BY_ID["linux-vm-ipv6"]
    # changing the router before reading the client's state does not earn the diagnosis
    done = _grade(v6, ["[rtr] ip -6 addr add 2001:db8:40::1/64 dev eth0", "[ws] ip -6 a", "[ws] ip -6 route"])
    assert "diagnose" not in done
    # dnsmasq --test is only a syntax check, not a change: the diagnosis still counts after it
    done = _grade(v6, ["[rtr] dnsmasq --test", "[ws] ip -6 a", "[ws] ip -6 route"])
    assert "diagnose" in done
    # the link-local ping must name the interface; the service ping alone is not enough
    sol = v6["solution"]["vm_commands"]
    no_scope = [c for c in sol if "%eth0" not in c]
    assert "reach" not in _grade(v6, no_scope)
    assert "reach" in _grade(v6, no_scope + ["[ws] ping -6 -c 2 fe80::222:15ff:fe00:1%eth0"])
    # the record is compared with the live address and default router in the VM, not a fixed answer
    probe = V.probe_scripts(V.fresh(v6, 1), v6)["ws"]
    assert "ip -6 addr show dev eth0 scope global" in probe and "^default" in probe


def test_round4_pages_and_http_flow(student, instructor):
    for lid in R4:
        lab = RT.get_lab(lid)
        page = student.get(f"/labs/{lid}").data.decode()
        assert lab["title"].split("—")[0].strip() in page and "Pending SME review" not in page, lid
        assert all(f'/labs/{f}' in page for f in lab["fallback"]), lid     # the simulated fallback is linked
        assert "Pending SME review" in instructor.get(f"/labs/{lid}").data.decode(), lid
        student.post(f"/labs/{lid}/reset")
        st = _state(lid)
        j = _j(student.get(f"/labs/{lid}/vm-probe"))
        assert set(j["scripts"]) == set(V.machines(lab))
        _j(student.post(f"/labs/{lid}/vm-log", json={"lines": [], "booted": True, "boot_ms": 1}))
        _j(student.post(f"/labs/{lid}/vm-log", json={"lines": lab["solution"]["vm_commands"]}))
        probes = RT.PX.probes_with_real_px(lab, st, V.solved_probes(st, lab))
        r = _j(student.post(f"/labs/{lid}/vm-check", json={"probes": probes, "fabric": lab["solution"].get("fabric")}))
        assert r["complete"] and r["score"] == 100, (lid, r)
