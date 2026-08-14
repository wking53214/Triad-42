import json

import pytest

from triad42 import (
    Authorization,
    CandidateRecord,
    CandidateKind,
    CandidateStore,
    EpistemicViolation,
    GrayLens,
    GreenLens,
    IncompleteSubmission,
    Label,
    LabeledItem,
    NotYetSpecified,
    Origin,
    ProvenanceGraph,
    RedLens,
    Session,
    Severity,
    SurfacingStatus,
    Verdict,
)
from triad42.engines import unavailable


def auth(reason="human said so"):
    return Authorization(authorized_by="William", reason=reason)


def item(text, label=Label.INFERENCE):
    return LabeledItem(text=text, label=label)


# --------------------------------------------------------------------------
# Chain A: origin
# --------------------------------------------------------------------------


def test_machine_material_cannot_become_user_established():
    g = ProvenanceGraph()
    m = g.register(item("Derived conclusion"), Origin.MACHINE_DERIVED)
    with pytest.raises(EpistemicViolation):
        g.reassign_origin(m.item_id, Origin.USER_ESTABLISHED, None)
    assert g.origin_of(m.item_id) is Origin.MACHINE_DERIVED


def test_human_can_accept_machine_material_explicitly():
    g = ProvenanceGraph()
    m = g.register(item("Assistant suggested this"), Origin.ASSISTANT_PROPOSED)
    g.reassign_origin(m.item_id, Origin.USER_ACCEPTED, auth("adopted in review"))
    assert g.origin_of(m.item_id) is Origin.USER_ACCEPTED


def test_origin_and_label_are_independent():
    """Who said it and what kind of claim it is are different questions."""
    g = ProvenanceGraph()
    a = g.register(item("A user guess", Label.ASSUMPTION), Origin.USER_ESTABLISHED)
    b = g.register(item("A machine inference", Label.INFERENCE), Origin.MACHINE_DERIVED)
    assert g.origin_of(a.item_id) is Origin.USER_ESTABLISHED
    assert a.label is Label.ASSUMPTION  # human origin is not an upgrade
    assert b.label is Label.INFERENCE


# --------------------------------------------------------------------------
# Chain B: support
# --------------------------------------------------------------------------


def test_support_link_requires_a_stated_reason():
    g = ProvenanceGraph()
    a = g.register(item("source"), Origin.USER_ESTABLISHED)
    b = g.register(item("target"), Origin.MACHINE_DERIVED)
    with pytest.raises(IncompleteSubmission):
        g.add_support(a.item_id, b.item_id, reason="   ")


def test_nothing_supports_itself():
    g = ProvenanceGraph()
    a = g.register(item("a"), Origin.USER_ESTABLISHED)
    with pytest.raises(IncompleteSubmission):
        g.add_support(a.item_id, a.item_id, reason="circular")


def test_support_cycles_are_rejected():
    g = ProvenanceGraph()
    a = g.register(item("a"), Origin.MACHINE_DERIVED)
    b = g.register(item("b"), Origin.MACHINE_DERIVED)
    g.add_support(a.item_id, b.item_id, "a backs b")
    with pytest.raises(IncompleteSubmission):
        g.add_support(b.item_id, a.item_id, "b backs a")


def test_human_origin_is_not_automatic_support():
    """Chain A and Chain B answer different questions."""
    g = ProvenanceGraph()
    src = g.register(item("I prefer mornings", Label.FACT), Origin.USER_ESTABLISHED)
    concl = g.register(item("Therefore the system is faster at dawn"),
                       Origin.MACHINE_DERIVED)
    # authentic human source, but no support link asserted
    assert g.supporters(concl.item_id) == []
    assert not g.trace(concl.item_id).reaches_human_root
    with pytest.raises(EpistemicViolation):
        g.promote_to_fact(concl.item_id, auth())


# --------------------------------------------------------------------------
# human root requirement
# --------------------------------------------------------------------------


def test_machine_chain_cannot_bootstrap_into_fact():
    g = ProvenanceGraph()
    a = g.register(item("machine step 1"), Origin.MACHINE_DERIVED)
    b = g.register(item("machine step 2"), Origin.MACHINE_DERIVED)
    c = g.register(item("machine step 3"), Origin.MACHINE_DERIVED)
    g.add_support(a.item_id, b.item_id, "step 1 backs step 2")
    g.add_support(b.item_id, c.item_id, "step 2 backs step 3")
    trace = g.trace(c.item_id)
    assert not trace.reaches_human_root
    assert trace.machine_steps >= 3
    with pytest.raises(EpistemicViolation):
        g.promote_to_fact(c.item_id, auth())


def test_machine_inference_with_human_root_can_be_promoted():
    g = ProvenanceGraph()
    root = g.register(item("I ran the test myself", Label.FACT), Origin.USER_ESTABLISHED)
    inf = g.register(item("The build is reproducible"), Origin.MACHINE_DERIVED)
    g.add_support(root.item_id, inf.item_id, "the observed run is the evidence")
    assert g.trace(inf.item_id).reaches_human_root
    g.promote_to_fact(inf.item_id, auth("verified independently"))
    assert inf.label is Label.FACT


def test_registering_a_rootless_machine_fact_is_rejected():
    g = ProvenanceGraph()
    with pytest.raises(EpistemicViolation):
        g.register(item("Established truth", Label.FACT), Origin.MACHINE_DERIVED)


def test_trace_answers_why_this_exists():
    g = ProvenanceGraph()
    root = g.register(item("user statement"), Origin.USER_ESTABLISHED)
    mid = g.register(item("machine inference"), Origin.MACHINE_DERIVED)
    g.add_support(root.item_id, mid.item_id, "the statement names the constraint")
    t = g.trace(mid.item_id)
    assert t.human_roots == [root.item_id]
    assert t.paths and t.paths[0][-1] == root.item_id


# --------------------------------------------------------------------------
# erasure cascade
# --------------------------------------------------------------------------


def test_erasure_downgrades_dependent_fact():
    g = ProvenanceGraph()
    root = g.register(item("I measured it", Label.FACT), Origin.USER_ESTABLISHED)
    dep = g.register(item("Latency is under 50ms"), Origin.MACHINE_DERIVED)
    g.add_support(root.item_id, dep.item_id, "the measurement is the basis")
    g.promote_to_fact(dep.item_id, auth())
    assert dep.label is Label.FACT

    event = g.erase(root.item_id, erased_by="William", reason="measurement was wrong")
    assert dep.label is Label.UNKNOWN
    assert event.downgrades[0]["from"] == "FACT"


def test_no_zombie_evidence_survives_erasure():
    g = ProvenanceGraph()
    root = g.register(item("source", Label.FACT), Origin.USER_ESTABLISHED)
    a = g.register(item("a"), Origin.MACHINE_DERIVED)
    b = g.register(item("b"), Origin.MACHINE_DERIVED)
    g.add_support(root.item_id, a.item_id, "root backs a")
    g.add_support(a.item_id, b.item_id, "a backs b")
    g.promote_to_fact(a.item_id, auth())
    g.promote_to_fact(b.item_id, auth())

    g.erase(root.item_id, "William", "retracted")
    assert g.zombie_check() == []
    assert a.label is not Label.FACT
    assert b.label is not Label.FACT


def test_cascade_only_ever_moves_downward():
    """Erasure is a human act, so downgrade is authorized. Upgrade never is."""
    g = ProvenanceGraph()
    root = g.register(item("source", Label.FACT), Origin.USER_ESTABLISHED)
    dep = g.register(item("weak claim", Label.ASSUMPTION), Origin.MACHINE_DERIVED)
    g.add_support(root.item_id, dep.item_id, "root informs the assumption")
    g.erase(root.item_id, "William", "changed my mind")
    assert dep.label is Label.ASSUMPTION  # untouched, never raised


def test_human_decision_is_flagged_not_downgraded():
    """Erasing what informed a decision does not unmake the decision."""
    g = ProvenanceGraph()
    root = g.register(item("the analysis", Label.FACT), Origin.USER_ESTABLISHED)
    dec = g.register(item("We are going with option B", Label.DECISION),
                     Origin.USER_ESTABLISHED)
    g.add_support(root.item_id, dec.item_id, "the analysis informed the choice")
    event = g.erase(root.item_id, "William", "analysis was flawed")
    assert dec.label is Label.DECISION
    assert dec.item_id in event.flagged


def test_erased_material_cannot_support_anything_new():
    g = ProvenanceGraph()
    a = g.register(item("gone"), Origin.USER_ESTABLISHED)
    b = g.register(item("still here"), Origin.MACHINE_DERIVED)
    g.erase(a.item_id, "William", "removed")
    with pytest.raises(IncompleteSubmission):
        g.add_support(a.item_id, b.item_id, "trying to use erased material")


def test_erasure_requires_actor_and_reason():
    g = ProvenanceGraph()
    a = g.register(item("x"), Origin.USER_ESTABLISHED)
    with pytest.raises(IncompleteSubmission):
        g.erase(a.item_id, erased_by="", reason="because")


# --------------------------------------------------------------------------
# retrieval right
# --------------------------------------------------------------------------


def test_candidate_requires_a_surfacing_reason():
    with pytest.raises(IncompleteSubmission):
        CandidateRecord(text="something", kind=CandidateKind.FINDING,
                  status=SurfacingStatus.NOT_SURFACED, reason="")


def test_non_surfaced_candidates_remain_queryable():
    store = CandidateStore()
    store.record(CandidateRecord(text="shown", kind=CandidateKind.FINDING,
                           status=SurfacingStatus.SURFACED, reason="presented"))
    store.record(CandidateRecord(text="hidden", kind=CandidateKind.FINDING,
                           status=SurfacingStatus.NOT_SURFACED,
                           reason="below the presentation threshold"))
    hidden = store.not_surfaced()
    assert len(hidden) == 1
    assert hidden[0].text == "hidden"
    assert len(store.all()) == 2


def test_rejected_insight_is_retained_not_discarded():
    session = Session()
    rp = session.start_pass(item("A proposal", Label.ASSUMPTION))
    for _ in range(4):
        rp.close_stage()
    session.harvest(rp)
    # the default 42 result has no candidate text, so nothing is stored for it
    assert session.candidates.query(kind=CandidateKind.REJECTED_INSIGHT) == []


def test_harvest_records_everything_a_pass_produced():
    session = Session()
    rp = session.start_pass(item("A proposal", Label.ASSUMPTION))
    f = rp.add_finding("A real problem", Severity.MEDIUM, "auth")
    for _ in range(4):
        rp.close_stage()
    n = session.harvest(rp, surfaced_ids={f.finding_id})
    assert n >= 1
    surfaced = session.candidates.query(status=SurfacingStatus.SURFACED)
    assert any(c.source_id == f.finding_id for c in surfaced)


def test_candidate_store_is_append_only():
    store = CandidateStore()
    assert not hasattr(store, "delete")
    assert not hasattr(store, "remove")


# --------------------------------------------------------------------------
# the empty seam
# --------------------------------------------------------------------------


def test_reasoning_layer_is_not_implemented():
    with pytest.raises(NotYetSpecified):
        unavailable()


def test_red_lens_protocol_omits_severity():
    """An automated Red must not assign severity: severity gates FAILS."""
    import inspect

    sig = inspect.signature(RedLens.analyze)
    assert "severity" not in sig.parameters
    hints = RedLens.analyze.__annotations__
    assert "Severity" not in str(hints.get("return", ""))


def test_lens_protocols_are_distinct():
    assert RedLens is not GrayLens
    assert GrayLens is not GreenLens


# --------------------------------------------------------------------------
# serialization
# --------------------------------------------------------------------------


def test_session_serializes_provenance_and_candidates():
    session = Session()
    rp = session.start_pass(item("Subject", Label.ASSUMPTION),
                            subject_origin=Origin.USER_ESTABLISHED)
    rp.add_finding("A finding", Severity.LOW, "scope-a")
    for _ in range(4):
        rp.close_stage()
    rp.declare(Verdict.NO_BLOCKING_FINDINGS, "nothing blocking")
    session.harvest(rp)

    data = json.loads(session.to_json())
    assert "provenance" in data
    assert "candidates" in data
    assert data["provenance"]["items"][0]["origin"] == "USER_ESTABLISHED"
    assert len(data["candidates"]["candidates"]) >= 1


def test_provenance_export_marks_erased_and_root_erased():
    g = ProvenanceGraph()
    root = g.register(item("root", Label.FACT), Origin.USER_ESTABLISHED)
    dep = g.register(item("dep"), Origin.MACHINE_DERIVED)
    g.add_support(root.item_id, dep.item_id, "root backs dep")
    g.erase(root.item_id, "William", "retracted")
    data = g.to_dict()
    by_id = {i["item_id"]: i for i in data["items"]}
    assert by_id[root.item_id]["erased"] is True
    assert by_id[dep.item_id]["root_erased"] is True


# --------------------------------------------------------------------------
# regressions: the six defects found by adversarial review of v2.0.0
# --------------------------------------------------------------------------


def test_relabel_cannot_bypass_the_human_root_requirement():
    """v2.0.0 defect: promote_to_fact was guarded, relabel() was not."""
    g = ProvenanceGraph()
    a = g.register(item("machine 1"), Origin.MACHINE_DERIVED)
    b = g.register(item("machine 2"), Origin.MACHINE_DERIVED)
    g.add_support(a.item_id, b.item_id, "a backs b")
    with pytest.raises(EpistemicViolation):
        b.relabel(Label.FACT, auth("bypass attempt"))
    assert b.label is Label.INFERENCE
    assert g.zombie_check() == []


def test_guard_permits_relabel_when_a_human_root_exists():
    g = ProvenanceGraph()
    root = g.register(item("I observed it", Label.FACT), Origin.USER_ESTABLISHED)
    inf = g.register(item("therefore X"), Origin.MACHINE_DERIVED)
    g.add_support(root.item_id, inf.item_id, "the observation is the basis")
    inf.relabel(Label.FACT, auth("confirmed"))
    assert inf.label is Label.FACT


def test_guard_does_not_block_downward_relabel():
    g = ProvenanceGraph()
    a = g.register(item("claim"), Origin.MACHINE_DERIVED)
    a.relabel(Label.UNKNOWN, auth("withdrawing confidence"))
    assert a.label is Label.UNKNOWN


def test_unregistered_items_are_unaffected_by_the_guard():
    loose = item("not in any graph")
    loose.relabel(Label.FACT, auth("standalone use"))
    assert loose.label is Label.FACT


def test_red_ledger_seals_when_the_stage_closes():
    """v2.0.0 defect: rp.red.add() bypassed the stage-order check."""
    from triad42.findings import Finding
    from triad42.errors import StageOrderError

    rp = Session().start_pass(item("subject", Label.ASSUMPTION))
    rp.close_stage()
    with pytest.raises(StageOrderError):
        rp.red.add(Finding("injected", Severity.HIGH, "scope"))
    assert rp.red.blocking_findings() == []


def test_gray_is_read_only_from_outside():
    """v2.0.0 defect: rp.gray was a mutable public list."""
    rp = Session().start_pass(item("subject", Label.ASSUMPTION))
    assert isinstance(rp.gray, tuple)
    with pytest.raises(AttributeError):
        rp.gray.append("smuggled in")


def test_green_ledger_seals_when_the_stage_closes():
    from triad42 import Grounding, Stage
    from triad42.errors import StageOrderError

    rp = Session().start_pass(item("subject", Label.ASSUMPTION))
    while rp.current_stage is not Stage.GREEN:
        rp.close_stage()
    rp.close_stage()
    with pytest.raises(StageOrderError):
        rp.green.add(Grounding("k", "sys", "holds", "breaks"))


def test_verdicts_are_write_once():
    """v2.0.0 defect: a second declare() silently overwrote the first."""
    from triad42.errors import InadmissibleVerdict

    rp = Session().start_pass(item("subject", Label.ASSUMPTION))
    for _ in range(4):
        rp.close_stage()
    rp.declare(Verdict.NO_BLOCKING_FINDINGS, "clean")
    with pytest.raises(InadmissibleVerdict):
        rp.declare(Verdict.REQUIRES_HUMAN_DECISION, "changed my mind")
    assert rp.verdict is Verdict.NO_BLOCKING_FINDINGS


def test_analogy_keys_are_normalized():
    """v2.0.0 defect: a hyphen defeated reaffirmation detection."""
    from triad42 import Grounding, GroundingError, Stage

    session = Session()
    p1 = session.start_pass(item("s1", Label.ASSUMPTION))
    while p1.current_stage is not Stage.GREEN:
        p1.close_stage()
    p1.add_grounding(Grounding("immune-system", "immune response", "holds", "breaks"))
    p1.close_stage()
    p1.close_stage()

    p2 = session.start_pass(item("s2", Label.ASSUMPTION))
    while p2.current_stage is not Stage.GREEN:
        p2.close_stage()
    with pytest.raises(GroundingError):
        p2.add_grounding(Grounding("Immune  System", "immune response", "a", "b"))


def test_normalize_key_folds_common_variants():
    from triad42 import normalize_key

    forms = ["immune-system", "immune system", "Immune_System", "  IMMUNE   SYSTEM "]
    assert len({normalize_key(f) for f in forms}) == 1


def test_start_pass_does_not_swallow_errors():
    """v2.0.0 defect: a bare except hid genuine registration failures."""
    import inspect

    assert "except Exception:" not in inspect.getsource(Session.start_pass)


def test_repeated_subject_registers_once_without_error():
    session = Session()
    subj = item("shared subject", Label.ASSUMPTION)
    session.start_pass(subj, subject_origin=Origin.USER_ESTABLISHED)
    session.start_pass(subj, subject_origin=Origin.USER_ESTABLISHED)
    assert session.graph.origin_of(subj.item_id) is Origin.USER_ESTABLISHED


def test_records_carry_timestamps():
    """v2.0.0 defect: nothing recorded when anything happened."""
    session = Session()
    rp = session.start_pass(item("subject", Label.ASSUMPTION))
    f = rp.add_finding("a finding", Severity.LOW, "scope")
    for _ in range(4):
        rp.close_stage()
    rp.declare(Verdict.NO_BLOCKING_FINDINGS, "clean")
    session.harvest(rp)

    d = rp.to_dict()
    assert d["created_at"] and d["declared_at"]
    assert d["red"]["findings"][0]["created_at"]
    assert f.created_at
    assert session.to_dict()["created_at"]
    assert session.candidates.all()[0].recorded_at


def test_erasure_event_is_timestamped():
    g = ProvenanceGraph()
    a = g.register(item("root", Label.FACT), Origin.USER_ESTABLISHED)
    event = g.erase(a.item_id, "William", "retracted")
    assert event.erased_at
