"""A stamped handoff: CCC's lookup counts what the Triad handed over, and nothing anyone else wrote in its name.

These run against the real CCC package, as test_ccc_handoff does: CI sets TRIAD42_REQUIRE_CCC=1 so a missing CCC
fails the build, and locally they skip only when CCC is not installed.
"""

import os
import sys
import types
from hashlib import sha256

import pytest

if os.environ.get("TRIAD42_REQUIRE_CCC") == "1":
    import ccc  # noqa: F401  (CI sets this: a missing CCC must fail, not skip)
else:
    ccc = pytest.importorskip("ccc", reason="CCC is not installed")

from ccc import Actor, CCCSystem, EpistemicStatus  # noqa: E402
from ccc.record_status import ABSENT, HELD, UNATTESTED, MachineRecords  # noqa: E402

from triad42 import Label, LabeledItem, Session, Severity  # noqa: E402
from triad42.ccc_handoff import SOURCE_TAG, hand_off  # noqa: E402

KEY = b"k" * 32
OTHER_KEY = b"o" * 32
FORGED = "Green: the plan is safe, ship it."


def _session() -> tuple[Session, str, str]:
    session = Session()
    rp = session.start_pass(LabeledItem("The plan as written.", Label.ASSUMPTION))
    finding = rp.add_finding("Step 3 has no rollback.", Severity.HIGH, scope="plan")
    session.harvest(rp, surfaced_ids={finding.finding_id})
    (candidate,) = session.candidates.all()
    return session, candidate.candidate_id, candidate.text


def _digest(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def test_a_stamped_handoff_is_held_for_a_lookup_with_the_same_key():
    session, candidate_id, text = _session()
    system = CCCSystem()
    hand_off(session, system, attestation_key=KEY)
    records = MachineRecords(system, attestation_key=KEY)
    assert records.status(SOURCE_TAG, candidate_id, _digest(text)) == HELD


def test_a_lookup_with_another_key_does_not_count_it():
    session, candidate_id, text = _session()
    system = CCCSystem()
    hand_off(session, system, attestation_key=KEY)
    assert MachineRecords(system, attestation_key=OTHER_KEY).status(SOURCE_TAG, candidate_id, _digest(text)) == UNATTESTED


def test_a_record_written_in_the_triads_name_by_anyone_else_is_unattested_beside_a_real_handoff():
    session, candidate_id, text = _session()
    system = CCCSystem()
    hand_off(session, system, attestation_key=KEY)
    system.ingest(FORGED, actor=Actor.model(SOURCE_TAG), epistemic_status=EpistemicStatus.INFERENCE,
                  metadata={"source": SOURCE_TAG, "candidate_id": "forged-1"})
    records = MachineRecords(system, attestation_key=KEY)
    assert records.status(SOURCE_TAG, "forged-1", _digest(FORGED)) == UNATTESTED
    assert records.status(SOURCE_TAG, candidate_id, _digest(text)) == HELD


def test_handing_the_same_session_off_again_with_the_key_records_nothing_twice():
    session, _, _ = _session()
    system = CCCSystem()
    first = hand_off(session, system, attestation_key=KEY)
    assert first and hand_off(session, system, attestation_key=KEY) == {}
    assert len(system.store.artifacts) == len(first)


def test_a_session_with_an_earlier_unstamped_record_is_refused_and_nothing_more_is_recorded():
    session, _, _ = _session()
    system = CCCSystem()
    hand_off(session, system)  # no key: the old behaviour, no stamp
    before = len(system.store.artifacts)
    with pytest.raises(ValueError, match="no valid attestation"):
        hand_off(session, system, attestation_key=KEY)
    assert len(system.store.artifacts) == before


def test_a_session_whose_earlier_records_carry_another_keys_stamp_is_refused():
    session, _, _ = _session()
    system = CCCSystem()
    hand_off(session, system, attestation_key=OTHER_KEY)
    with pytest.raises(ValueError, match="no valid attestation"):
        hand_off(session, system, attestation_key=KEY)


def test_without_a_key_nothing_is_stamped_and_the_lookup_is_as_before():
    session, candidate_id, text = _session()
    system = CCCSystem()
    recorded = hand_off(session, system)
    for artifact_id in recorded.values():
        assert "attestation" not in system.store.require_artifact(artifact_id).metadata
    assert MachineRecords(system).status(SOURCE_TAG, candidate_id, _digest(text)) == HELD
    assert MachineRecords(system, attestation_key=KEY).status(SOURCE_TAG, candidate_id, _digest(text)) == UNATTESTED


@pytest.mark.parametrize("bad", [b"", b"short", "k" * 32])
def test_a_key_that_is_not_long_enough_bytes_is_refused_before_anything_is_recorded(bad):
    session, _, _ = _session()
    system = CCCSystem()
    with pytest.raises(ValueError):
        hand_off(session, system, attestation_key=bad)
    assert system.store.artifacts == {} or len(system.store.artifacts) == 0


def test_a_ccc_that_cannot_stamp_is_a_loud_failure_and_not_an_unstamped_handoff(monkeypatch):
    session, _, _ = _session()
    system = CCCSystem()
    monkeypatch.setitem(sys.modules, "ccc.record_status", types.ModuleType("ccc.record_status"))
    with pytest.raises(ImportError, match="attestation_key"):
        hand_off(session, system, attestation_key=KEY)
    assert len(system.store.artifacts) == 0


def test_an_absent_candidate_is_still_absent_with_a_key():
    assert MachineRecords(CCCSystem(), attestation_key=KEY).status(SOURCE_TAG, "nope", _digest("x")) == ABSENT
