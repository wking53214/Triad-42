import json

import pytest

from triad42 import (
    Authorization,
    Candidate,
    Check,
    CheckAnswer,
    ClusterState,
    DeepThoughtResult,
    EpistemicViolation,
    EscalationError,
    ExaminationOutcome,
    Finding,
    FindingLedger,
    Grounding,
    GroundingError,
    GroundingStatus,
    InadmissibleVerdict,
    IncompleteSubmission,
    Label,
    LabeledItem,
    ReviewPass,
    Session,
    Severity,
    Stage,
    StageOrderError,
    StructuralObservation,
    UnexaminedMandate,
    Verdict,
    no_candidate,
    run_gate,
)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def subject(text="A proposal under review"):
    return LabeledItem(text=text, label=Label.ASSUMPTION)


def finish_red(rp):
    rp.close_stage()


def walk_to(rp, stage):
    while rp.current_stage is not stage:
        rp.close_stage()


def gate_answers(**overrides):
    base = {
        Check.NOT_ALREADY_STATED: True,
        Check.NOT_MERELY_RENAMING: True,
        Check.ABSTRACTION_LABELLED: True,
        Check.NEW_RELATIONSHIP: True,
        Check.MATERIALLY_CONSEQUENTIAL: True,
    }
    base.update(overrides)
    return [
        CheckAnswer(check=c, passed=v, reasoning="reviewer reasoning")
        for c, v in base.items()
    ]


# --------------------------------------------------------------------------
# Amendment 1: epistemic persistence
# --------------------------------------------------------------------------


def test_label_cannot_change_without_authorization():
    item = LabeledItem(text="X improves throughput", label=Label.RECOMMENDATION)
    with pytest.raises(EpistemicViolation):
        item.relabel(Label.FACT, None)
    assert item.label is Label.RECOMMENDATION


def test_label_changes_only_with_recorded_authorization():
    item = LabeledItem(text="X improves throughput", label=Label.RECOMMENDATION)
    item.relabel(Label.DECISION, Authorization(authorized_by="William", reason="Adopted"))
    assert item.label is Label.DECISION
    assert item.label_history[0]["from"] == "RECOMMENDATION"
    assert item.label_history[0]["authorization"]["authorized_by"] == "William"


def test_authorization_requires_identity_and_reason():
    with pytest.raises(IncompleteSubmission):
        Authorization(authorized_by="", reason="because")
    with pytest.raises(IncompleteSubmission):
        Authorization(authorized_by="William", reason="  ")


def test_recommendation_survives_carry_forward_as_recommendation():
    session = Session()
    rec = LabeledItem(text="Consolidate the stores", label=Label.RECOMMENDATION)
    rp = session.start_pass(subject(), inputs=[rec])
    assert rp.inputs[0].label is Label.RECOMMENDATION


def test_unlabelled_input_is_rejected():
    with pytest.raises(IncompleteSubmission):
        ReviewPass(subject=subject(), inputs=["a bare string"])


def test_pass_outputs_are_never_facts():
    rp = ReviewPass(subject=subject())
    rp.add_finding("Undocumented dependency", Severity.MEDIUM, "auth")
    walk_to(rp, Stage.DEEP_THOUGHT)
    rp.record_42(
        run_gate(Candidate("A new relationship", consequence_area="architecture"),
                 gate_answers())
    )
    rp.close_stage()
    labels = {o.label for o in rp.outputs()}
    assert Label.FACT not in labels
    assert Label.DECISION not in labels


# --------------------------------------------------------------------------
# Amendment 2: severity and the FAILS floor
# --------------------------------------------------------------------------


def test_finding_requires_scope():
    with pytest.raises(IncompleteSubmission):
        Finding(text="something wrong", severity=Severity.LOW, scope="  ")


def test_volume_of_medium_cannot_produce_fails():
    rp = ReviewPass(subject=subject())
    for i in range(2):
        rp.add_finding(f"minor issue {i}", Severity.MEDIUM, f"scope-{i}")
    for _ in range(4):
        rp.close_stage()
    with pytest.raises(InadmissibleVerdict):
        rp.declare(Verdict.FAILS, "lots of small problems")


def test_fails_admissible_with_one_high():
    rp = ReviewPass(subject=subject())
    rp.add_finding("Unsupported verification claim", Severity.HIGH, "provenance")
    for _ in range(4):
        rp.close_stage()
    assert rp.declare(Verdict.FAILS, "blocking finding stands") is Verdict.FAILS


def test_no_blocking_findings_rejected_when_blocking_exists():
    rp = ReviewPass(subject=subject())
    rp.add_finding("Authority overreach", Severity.CRITICAL, "governance")
    for _ in range(4):
        rp.close_stage()
    with pytest.raises(InadmissibleVerdict):
        rp.declare(Verdict.NO_BLOCKING_FINDINGS, "looks fine")


# --------------------------------------------------------------------------
# 1 / 2 / 3 clustering
# --------------------------------------------------------------------------


def test_one_finding_is_an_anomaly():
    led = FindingLedger()
    led.add(Finding("a", Severity.LOW, "mod"))
    (c,) = led.clusters()
    assert c.state is ClusterState.ANOMALY
    assert not c.examination_permitted


def test_two_findings_are_a_pattern():
    led = FindingLedger()
    led.add(Finding("a", Severity.LOW, "mod"))
    led.add(Finding("b", Severity.LOW, "mod"))
    (c,) = led.clusters()
    assert c.state is ClusterState.PATTERN
    assert c.examination_permitted
    assert not c.examination_required


def test_three_findings_are_a_mandate():
    led = FindingLedger()
    for t in "abc":
        led.add(Finding(t, Severity.LOW, "mod"))
    (c,) = led.clusters()
    assert c.state is ClusterState.MANDATE
    assert c.examination_required


def test_anomaly_cannot_be_examined():
    led = FindingLedger()
    led.add(Finding("a", Severity.LOW, "mod"))
    with pytest.raises(EscalationError):
        led.examine("mod", Severity.LOW, ExaminationOutcome.SHARED_CAUSE_NAMED,
                    shared_cause="x")


def test_findings_in_different_scopes_do_not_cluster():
    led = FindingLedger()
    for i in range(3):
        led.add(Finding(f"f{i}", Severity.MEDIUM, f"scope-{i}"))
    assert all(c.state is ClusterState.ANOMALY for c in led.clusters())
    assert led.open_mandates() == []


def test_unexamined_mandate_blocks_stage_close():
    rp = ReviewPass(subject=subject())
    for i in range(3):
        rp.add_finding(f"f{i}", Severity.MEDIUM, "auth")
    with pytest.raises(UnexaminedMandate):
        rp.close_stage()


# --------------------------------------------------------------------------
# escalation and the inverted burden
# --------------------------------------------------------------------------


def test_escalation_moves_exactly_one_tier():
    led = FindingLedger()
    for i in range(3):
        led.add(Finding(f"f{i}", Severity.LOW, "auth"))
    exam = led.examine("auth", Severity.LOW, ExaminationOutcome.SHARED_CAUSE_NAMED,
                       shared_cause="all three trace to the missing owner rule")
    produced = led.get(exam.produced_finding_id)
    assert produced.severity is Severity.MEDIUM
    assert produced.severity is not Severity.HIGH
    assert produced.is_derived


def test_escalation_requires_a_named_cause():
    led = FindingLedger()
    for i in range(3):
        led.add(Finding(f"f{i}", Severity.LOW, "auth"))
    with pytest.raises(IncompleteSubmission):
        led.examine("auth", Severity.LOW, ExaminationOutcome.SHARED_CAUSE_NAMED,
                    shared_cause="   ")


def test_declining_to_escalate_requires_origin_per_finding():
    led = FindingLedger()
    ids = [led.add(Finding(f"f{i}", Severity.MEDIUM, "auth")).finding_id
           for i in range(3)]
    with pytest.raises(IncompleteSubmission):
        led.examine(
            "auth", Severity.MEDIUM,
            ExaminationOutcome.INDEPENDENT_ORIGINS_DEMONSTRATED,
            independent_origins={ids[0]: "typo in the spec"},
        )


def test_repeated_origin_account_is_rejected_as_shared_cause():
    led = FindingLedger()
    ids = [led.add(Finding(f"f{i}", Severity.MEDIUM, "auth")).finding_id
           for i in range(3)]
    with pytest.raises(IncompleteSubmission):
        led.examine(
            "auth", Severity.MEDIUM,
            ExaminationOutcome.INDEPENDENT_ORIGINS_DEMONSTRATED,
            independent_origins={i: "insufficient design rigor" for i in ids},
        )


def test_distinct_origins_close_the_mandate_without_escalating():
    led = FindingLedger()
    ids = [led.add(Finding(f"f{i}", Severity.MEDIUM, "auth")).finding_id
           for i in range(3)]
    led.examine(
        "auth", Severity.MEDIUM,
        ExaminationOutcome.INDEPENDENT_ORIGINS_DEMONSTRATED,
        independent_origins={
            ids[0]: "copied from a superseded draft",
            ids[1]: "terminology drift from the Gem prompt",
            ids[2]: "edge case nobody enumerated",
        },
    )
    assert led.open_mandates() == []
    assert len(led.findings) == 3


def test_human_decision_outcome_requires_reasoning():
    led = FindingLedger()
    for i in range(3):
        led.add(Finding(f"f{i}", Severity.MEDIUM, "auth"))
    with pytest.raises(IncompleteSubmission):
        led.examine("auth", Severity.MEDIUM,
                    ExaminationOutcome.REQUIRES_HUMAN_DECISION, reasoning="")


def test_critical_cluster_examined_but_produces_nothing_higher():
    led = FindingLedger()
    for i in range(3):
        led.add(Finding(f"f{i}", Severity.CRITICAL, "gov"))
    exam = led.examine("gov", Severity.CRITICAL,
                       ExaminationOutcome.SHARED_CAUSE_NAMED,
                       shared_cause="single broken authority boundary")
    assert exam.produced_finding_id is None
    assert led.open_mandates() == []


def test_escalated_finding_can_complete_a_higher_cluster():
    """Two observed MEDIUMs plus one escalated from LOW makes a MEDIUM mandate."""
    led = FindingLedger()
    led.add(Finding("observed medium one", Severity.MEDIUM, "auth"))
    led.add(Finding("observed medium two", Severity.MEDIUM, "auth"))
    for i in range(3):
        led.add(Finding(f"low {i}", Severity.LOW, "auth"))

    medium_cluster = [c for c in led.clusters() if c.severity is Severity.MEDIUM][0]
    assert medium_cluster.state is ClusterState.PATTERN

    led.examine("auth", Severity.LOW, ExaminationOutcome.SHARED_CAUSE_NAMED,
                shared_cause="all three trace to the missing owner rule")

    medium_cluster = [c for c in led.clusters() if c.severity is Severity.MEDIUM][0]
    assert medium_cluster.count == 3
    assert medium_cluster.state is ClusterState.MANDATE
    assert led.open_mandates()  # the cascade reopened an examination duty


def test_human_decision_cannot_be_absorbed_into_another_verdict():
    rp = ReviewPass(subject=subject())
    for i in range(3):
        rp.add_finding(f"f{i}", Severity.MEDIUM, "auth")
    rp.examine_cluster("auth", Severity.MEDIUM,
                       ExaminationOutcome.REQUIRES_HUMAN_DECISION,
                       reasoning="something is wrong here but I cannot name it")
    for _ in range(4):
        rp.close_stage()
    with pytest.raises(InadmissibleVerdict):
        rp.declare(Verdict.NO_BLOCKING_FINDINGS, "nothing blocking")
    assert rp.declare(Verdict.REQUIRES_HUMAN_DECISION, "routed") is Verdict.REQUIRES_HUMAN_DECISION


# --------------------------------------------------------------------------
# Amendment 3: Green
# --------------------------------------------------------------------------


def test_grounding_without_break_is_rejected():
    with pytest.raises(GroundingError):
        Grounding(
            analogy_key="immune-system",
            real_system="mammalian immune response",
            where_it_holds="both discriminate self from non-self",
            where_it_breaks="",
        )


def test_reused_analogy_cannot_claim_new_grounding():
    session = Session()
    rp1 = session.start_pass(subject())
    walk_to(rp1, Stage.GREEN)
    rp1.add_grounding(Grounding(
        analogy_key="immune-system",
        real_system="mammalian immune response",
        where_it_holds="self versus non-self discrimination",
        where_it_breaks="no equivalent of memory cells here",
    ))
    rp1.close_stage()
    rp1.close_stage()
    rp2 = session.start_pass(subject())
    walk_to(rp2, Stage.GREEN)
    with pytest.raises(GroundingError):
        rp2.add_grounding(Grounding(
            analogy_key="immune-system",
            real_system="mammalian immune response",
            where_it_holds="same point again",
            where_it_breaks="same break again",
            status=GroundingStatus.NEW_GROUNDING,
        ))


def test_reaffirmation_is_accepted_when_marked():
    session = Session()
    rp1 = session.start_pass(subject())
    walk_to(rp1, Stage.GREEN)
    rp1.add_grounding(Grounding(
        analogy_key="aviation-checklist",
        real_system="preflight checklist",
        where_it_holds="forced sequence prevents skipped steps",
        where_it_breaks="checklists assume a known failure set",
    ))
    rp1.close_stage()
    rp1.close_stage()
    rp2 = session.start_pass(subject())
    walk_to(rp2, Stage.GREEN)
    g = rp2.add_grounding(Grounding(
        analogy_key="aviation-checklist",
        real_system="preflight checklist",
        where_it_holds="same structural point",
        where_it_breaks="same limit",
        status=GroundingStatus.REAFFIRMATION,
    ))
    assert g.status is GroundingStatus.REAFFIRMATION
    assert rp2.green.new_grounding_count() == 0


def test_unseen_analogy_cannot_claim_reaffirmation():
    rp = ReviewPass(subject=subject())
    walk_to(rp, Stage.GREEN)
    with pytest.raises(GroundingError):
        rp.add_grounding(Grounding(
            analogy_key="never-used",
            real_system="something",
            where_it_holds="holds",
            where_it_breaks="breaks",
            status=GroundingStatus.REAFFIRMATION,
        ))


# --------------------------------------------------------------------------
# Gray
# --------------------------------------------------------------------------


def test_retaining_overlapping_rules_requires_a_reason():
    from triad42 import Disposition
    with pytest.raises(IncompleteSubmission):
        StructuralObservation(
            text="Two rules overlap on advisory consensus",
            scope="governance",
            disposition=Disposition.RETAIN_SEPARATELY,
        )


# --------------------------------------------------------------------------
# 42 gate
# --------------------------------------------------------------------------


def test_already_stated_ends_the_gate():
    rec = run_gate(
        Candidate("The mechanism is advisory", consequence_area="governance"),
        gate_answers(**{Check.NOT_ALREADY_STATED: False}),
    )
    assert rec.result is DeepThoughtResult.NO_42_IDENTIFIED
    assert rec.failed_at is Check.NOT_ALREADY_STATED


def test_renaming_ends_the_gate():
    rec = run_gate(
        Candidate("Call Red the Adversary", consequence_area="architecture"),
        gate_answers(**{Check.NOT_MERELY_RENAMING: False}),
    )
    assert rec.result is DeepThoughtResult.NO_42_IDENTIFIED
    assert rec.failed_at is Check.NOT_MERELY_RENAMING


def test_abstraction_is_labelled_not_failed():
    rec = run_gate(
        Candidate("All three lenses guard one boundary", consequence_area="architecture"),
        gate_answers(**{Check.ABSTRACTION_LABELLED: False}),
    )
    assert rec.result is DeepThoughtResult.MEANINGFUL_ABSTRACTION
    assert rec.failed_at is None


def test_immaterial_insight_ends_the_gate():
    rec = run_gate(
        Candidate("Red and Green rhyme", consequence_area="architecture"),
        gate_answers(**{Check.MATERIALLY_CONSEQUENTIAL: False}),
    )
    assert rec.result is DeepThoughtResult.NO_42_IDENTIFIED


def test_gate_requires_every_check():
    answers = gate_answers()[:3]
    with pytest.raises(IncompleteSubmission):
        run_gate(Candidate("x", consequence_area="safety"), answers)


def test_check_requires_reasoning():
    with pytest.raises(IncompleteSubmission):
        CheckAnswer(check=Check.NOT_ALREADY_STATED, passed=True, reasoning="")


def test_clearing_gate_requires_named_consequence_area():
    with pytest.raises(IncompleteSubmission):
        run_gate(Candidate("A genuinely new relationship"), gate_answers())


def test_no_candidate_is_a_legitimate_result():
    assert no_candidate().result is DeepThoughtResult.NO_42_IDENTIFIED


def test_closing_42_without_a_candidate_records_no_42():
    rp = ReviewPass(subject=subject())
    for _ in range(4):
        rp.close_stage()
    assert rp.deep_thought.result is DeepThoughtResult.NO_42_IDENTIFIED


# --------------------------------------------------------------------------
# stage order
# --------------------------------------------------------------------------


def test_green_cannot_run_before_red():
    rp = ReviewPass(subject=subject())
    with pytest.raises(StageOrderError):
        rp.add_grounding(Grounding(
            analogy_key="k", real_system="s",
            where_it_holds="h", where_it_breaks="b",
        ))


def test_red_cannot_reopen_after_closing():
    rp = ReviewPass(subject=subject())
    rp.close_stage()
    with pytest.raises(StageOrderError):
        rp.add_finding("late finding", Severity.LOW, "mod")


def test_verdict_requires_all_stages_closed():
    rp = ReviewPass(subject=subject())
    rp.close_stage()
    with pytest.raises(StageOrderError):
        rp.declare(Verdict.NO_BLOCKING_FINDINGS, "premature")


def test_verdict_requires_a_reason():
    rp = ReviewPass(subject=subject())
    for _ in range(4):
        rp.close_stage()
    with pytest.raises(IncompleteSubmission):
        rp.declare(Verdict.NO_BLOCKING_FINDINGS, "   ")


# --------------------------------------------------------------------------
# disagreement
# --------------------------------------------------------------------------


def test_component_disagreement_routes_to_human_by_default():
    rp = ReviewPass(subject=subject())
    rp.add_finding("Unsupported claim", Severity.HIGH, "evidence")
    rp.close_stage()  # red
    rp.close_stage()  # gray, no observations
    rp.add_grounding(Grounding(
        analogy_key="bridge-load-test",
        real_system="structural load testing",
        where_it_holds="both test to failure deliberately",
        where_it_breaks="bridges have known material limits",
    ))
    rp.close_stage()  # green
    rp.close_stage()  # 42
    with pytest.raises(InadmissibleVerdict):
        rp.declare(Verdict.FAILS, "red wins")
    v = rp.declare(Verdict.FAILS, "red wins", disagreement_override="Legal overrode")
    assert v is Verdict.FAILS
    assert rp.disagreement_override == "Legal overrode"


# --------------------------------------------------------------------------
# serialization
# --------------------------------------------------------------------------


def test_pass_record_exports_the_full_record():
    rp = ReviewPass(subject=subject())
    for i in range(3):
        rp.add_finding(f"f{i}", Severity.LOW, "auth")
    rp.examine_cluster("auth", Severity.LOW,
                       ExaminationOutcome.SHARED_CAUSE_NAMED,
                       shared_cause="one missing rule")
    rp.close_stage()
    rp.add_observation(StructuralObservation(
        text="Authority and capability are conflated",
        scope="governance",
    ))
    rp.close_stage()
    rp.add_grounding(Grounding(
        analogy_key="air-traffic-control",
        real_system="ATC handoff protocol",
        where_it_holds="explicit custody transfer at every boundary",
        where_it_breaks="ATC has a single legal authority, this has several",
    ))
    rp.close_stage()
    rp.record_42(run_gate(
        Candidate("Handoff and label persistence are the same rule",
                  consequence_area="architecture"),
        gate_answers(),
    ))
    rp.close_stage()
    rp.declare(Verdict.NO_BLOCKING_FINDINGS, "no blocking findings remain")

    data = json.loads(rp.to_json())
    assert data["verdict"] == "NO_BLOCKING_FINDINGS"
    assert len(data["red"]["findings"]) == 4  # 3 originals plus 1 derived
    assert data["red"]["examinations"][0]["outcome"] == "SHARED_CAUSE_NAMED"
    assert data["green"]["groundings"][0]["where_it_breaks"]
    assert data["deep_thought"]["result"] == "NOVEL_INSIGHT"


def test_session_serializes_all_passes():
    session = Session()
    for _ in range(2):
        rp = session.start_pass(subject())
        for _ in range(4):
            rp.close_stage()
        rp.declare(Verdict.NO_BLOCKING_FINDINGS, "clean")
    data = json.loads(session.to_json())
    assert len(data["passes"]) == 2
