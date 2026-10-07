"""The handoff to CCC: machine-only, nothing dropped, never twice, never silent.

These tests run against the real CCC package. CI installs it and sets
TRIAD42_REQUIRE_CCC=1, so there a missing CCC fails the build instead of
quietly skipping. Locally they skip only when CCC is not installed.
"""

import os

import pytest

if os.environ.get("TRIAD42_REQUIRE_CCC") == "1":
    import ccc  # noqa: F401  (CI sets this: a missing CCC must fail, not skip)
else:
    ccc = pytest.importorskip("ccc", reason="CCC is not installed")

from ccc import Actor, ActorType, CCCSystem, EpistemicStatus, ProvenanceStatus  # noqa: E402

from triad42 import (  # noqa: E402
    Label,
    LabeledItem,
    Session,
    Severity,
    SurfacingStatus,
)
from triad42 import ccc_handoff  # noqa: E402
from triad42.ccc_handoff import HANDOFF_REASON, SOURCE_TAG, hand_off  # noqa: E402


def _session_with_output() -> tuple[Session, str, str]:
    session = Session()
    rp = session.start_pass(LabeledItem("The plan as written.", Label.ASSUMPTION))
    shown = rp.add_finding("Step 3 has no rollback.", Severity.HIGH, scope="plan")
    hidden = rp.add_finding("Naming is inconsistent.", Severity.LOW, scope="docs")
    session.harvest(rp, surfaced_ids={shown.finding_id})
    return session, shown.finding_id, hidden.finding_id


def test_every_candidate_is_recorded_as_machine_originated():
    session, _, _ = _session_with_output()
    system = CCCSystem()
    recorded = hand_off(session, system)

    assert len(recorded) == len(session.candidates.all()) == 2
    for artifact_id in recorded.values():
        artifact = system.store.require_artifact(artifact_id)
        assert artifact.origin.kind is ActorType.MODEL
        assert artifact.machine_origin
        assert artifact.provenance_status is ProvenanceStatus.ASSISTANT_PROPOSED
        assert artifact.epistemic_status is EpistemicStatus.INFERENCE
        assert SOURCE_TAG in artifact.topics


def test_not_surfaced_candidates_go_across_with_their_reason():
    session, shown_id, hidden_id = _session_with_output()
    system = CCCSystem()
    hand_off(session, system)

    by_source = {}
    for cand_id, art_id in session.handed_off.items():
        meta = system.store.require_artifact(art_id).metadata
        by_source[meta["source_id"]] = meta
    assert by_source[shown_id]["surfacing_status"] == SurfacingStatus.SURFACED.value
    hidden = by_source[hidden_id]
    assert hidden["surfacing_status"] == SurfacingStatus.NOT_SURFACED.value
    assert hidden["surfacing_reason"].strip()


def test_handoff_never_records_the_same_candidate_twice():
    session, _, _ = _session_with_output()
    system = CCCSystem()
    first = hand_off(session, system)
    second = hand_off(session, system)
    assert len(first) == 2
    assert second == {}
    assert len(session.handed_off) == 2


def test_later_output_is_handed_off_incrementally():
    session, _, _ = _session_with_output()
    system = CCCSystem()
    hand_off(session, system)
    rp = session.start_pass(LabeledItem("The revised plan.", Label.ASSUMPTION))
    rp.add_finding("Revision still lacks rollback.", Severity.HIGH, scope="plan")
    session.harvest(rp)
    assert len(hand_off(session, system)) == 1
    assert len(session.handed_off) == 3


def test_there_is_no_way_to_choose_the_actor():
    import inspect

    assert set(inspect.signature(hand_off).parameters) == {"session", "system"}
    session, _, _ = _session_with_output()
    system = CCCSystem()
    for art_id in hand_off(session, system).values():
        origin = system.store.require_artifact(art_id).origin
        assert origin.kind is ActorType.MODEL
        assert origin.actor_id == SOURCE_TAG


def test_ccc_refuses_to_promote_handed_off_output_on_a_model_s_say_so():
    """The point of the handoff: CCC, not Triad+42, guards promotion."""
    from ccc.errors import ConstitutionViolation

    session, _, _ = _session_with_output()
    system = CCCSystem()
    art_id = next(iter(hand_off(session, system).values()))
    with pytest.raises(ConstitutionViolation):
        system.accept(art_id, actor=Actor.model("triad42"), reason="looks right",
                      authorization_basis="model consensus")


def test_human_erasure_in_ccc_reaches_handed_off_output():
    session, _, _ = _session_with_output()
    system = CCCSystem()
    art_id = next(iter(hand_off(session, system).values()))
    system.erase(art_id, actor=Actor.human("william"), reason="not mine to keep",
                 authorization_basis="owner request")
    assert system.store.require_artifact(art_id).state.value == "ERASED"


def test_handoff_records_its_reason_in_the_audit_trail():
    session, _, _ = _session_with_output()
    system = CCCSystem()
    recorded = hand_off(session, system)
    reasons = {
        e.reason for e in system.audit_trail.all()
        if e.object_id in set(recorded.values())
    }
    assert reasons == {HANDOFF_REASON}


def test_missing_ccc_raises_instead_of_skipping(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "ccc":
            raise ImportError("simulated: CCC not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    session, _, _ = _session_with_output()
    with pytest.raises(ImportError, match="never skips"):
        ccc_handoff.hand_off(session, CCCSystem())
    assert session.handed_off == {}


def test_a_stand_in_target_is_refused_and_does_not_count_as_delivered():
    session, _, _ = _session_with_output()

    class StandIn:
        def ingest(self, *a, **k):
            raise AssertionError("should never be called")

    with pytest.raises(TypeError):
        hand_off(session, StandIn())
    assert session.handed_off == {}
    system = CCCSystem()
    assert len(hand_off(session, system)) == 2


def test_a_second_ccc_system_receives_everything():
    session, _, _ = _session_with_output()
    first, second = CCCSystem(), CCCSystem()
    assert len(hand_off(session, first)) == 2
    assert len(hand_off(session, second)) == 2
    assert hand_off(session, first) == {}
    assert len(first.store.artifacts) == len(second.store.artifacts) == 2


def test_harvesting_a_pass_twice_does_not_double_record():
    session = Session()
    rp = session.start_pass(LabeledItem("The plan.", Label.ASSUMPTION))
    rp.add_finding("Step 3 has no rollback.", Severity.HIGH, scope="plan")
    session.harvest(rp)
    session.harvest(rp)
    assert len(session.candidates.all()) == 2
    system = CCCSystem()
    assert len(hand_off(session, system)) == 1
    assert len(system.store.artifacts) == 1


def test_an_unharvested_pass_blocks_the_handoff():
    session, _, _ = _session_with_output()
    session.start_pass(LabeledItem("Started, never harvested.", Label.ASSUMPTION))
    system = CCCSystem()
    with pytest.raises(ValueError, match="never harvested"):
        hand_off(session, system)
    assert len(system.store.artifacts) == 0


def test_handing_off_again_never_resurrects_erased_material():
    session, _, _ = _session_with_output()
    system = CCCSystem()
    art_id = next(iter(hand_off(session, system).values()))
    system.erase(art_id, actor=Actor.human("william"), reason="remove it",
                 authorization_basis="owner request")
    assert hand_off(session, system) == {}
    assert len(system.store.artifacts) == 2
    assert system.store.require_artifact(art_id).content is None
