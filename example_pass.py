"""A complete worked pass, runnable with: python3 example_pass.py

The subject under review is a fictional proposal. What matters is the shape:
Red finds things and hits a mandate, the mandate forces an examination, the
examination escalates, Gray records structure, Green grounds with a stated
break, 42 runs the gate, and the verdict is checked for admissibility.
"""

from triad42 import (
    Candidate,
    Check,
    CheckAnswer,
    DistinctionKind,
    ExaminationOutcome,
    Grounding,
    InadmissibleVerdict,
    Label,
    LabeledItem,
    Session,
    Severity,
    StructuralObservation,
    Verdict,
    run_gate,
)


def main() -> None:
    session = Session()

    subject = LabeledItem(
        text="Proposal: let the review harness auto-assign severity from finding text.",
        label=Label.RECOMMENDATION,
    )
    rp = session.start_pass(subject)

    # ---- RED -----------------------------------------------------------
    rp.add_finding(
        "Auto-assignment is inference presented as classification.",
        Severity.MEDIUM,
        scope="severity-engine",
    )
    rp.add_finding(
        "No stated threshold separates HIGH from MEDIUM.",
        Severity.MEDIUM,
        scope="severity-engine",
    )
    rp.add_finding(
        "Reviewer cannot correct a machine-assigned severity.",
        Severity.MEDIUM,
        scope="severity-engine",
    )

    print("Open mandates before examination:",
          [c.scope for c in rp.red.open_mandates()])

    exam = rp.examine_cluster(
        "severity-engine",
        Severity.MEDIUM,
        ExaminationOutcome.SHARED_CAUSE_NAMED,
        shared_cause=(
            "All three follow from the harness making judgements the framework "
            "reserves for humans."
        ),
    )
    escalated = rp.red.get(exam.produced_finding_id)
    print(f"Escalated to: {escalated.severity.value}")
    rp.close_stage()

    # ---- GRAY ----------------------------------------------------------
    rp.add_observation(
        StructuralObservation(
            text=(
                "The proposal moves severity from reviewer capability into "
                "harness authority without a corresponding authority grant."
            ),
            scope="severity-engine",
            distinction=DistinctionKind.AUTHORITY_CAPABILITY_EXECUTION,
        )
    )
    rp.close_stage()

    # ---- GREEN ---------------------------------------------------------
    rp.add_grounding(
        Grounding(
            analogy_key="clinical-triage",
            real_system="emergency department triage",
            where_it_holds=(
                "Triage uses fixed categories so different clinicians sort "
                "patients the same way."
            ),
            where_it_breaks=(
                "Triage categories are assigned by a trained clinician at the "
                "bedside, never by the intake form itself."
            ),
            exposes="The break is the whole objection: the form does not triage.",
        )
    )
    rp.close_stage()

    # ---- 42 ------------------------------------------------------------
    rp.record_42(
        run_gate(
            Candidate(
                text=(
                    "Any component that assigns severity thereby acquires veto "
                    "power, because severity is what gates FAILS."
                ),
                consequence_area="governance",
            ),
            [
                CheckAnswer(Check.NOT_ALREADY_STATED, True,
                            "The framework states the FAILS floor but never "
                            "names assignment as an authority act."),
                CheckAnswer(Check.NOT_MERELY_RENAMING, True,
                            "This is not the advisory rule restated."),
                CheckAnswer(Check.ABSTRACTION_LABELLED, True,
                            "Not an abstraction of existing structure."),
                CheckAnswer(Check.NEW_RELATIONSHIP, True,
                            "Connects severity assignment to veto authority, "
                            "which was not previously explicit."),
                CheckAnswer(Check.MATERIALLY_CONSEQUENTIAL, True,
                            "Determines whether any future automation may "
                            "touch severity."),
            ],
        )
    )
    rp.close_stage()

    print(f"42 result: {rp.deep_thought.result.value}")

    # ---- VERDICT -------------------------------------------------------
    try:
        rp.declare(Verdict.NO_BLOCKING_FINDINGS, "Nothing serious found.")
    except InadmissibleVerdict as exc:
        print(f"\nRejected verdict: {exc}\n")

    rp.declare(
        Verdict.FAILS,
        "The escalated HIGH finding stands: the proposal grants the harness "
        "authority the framework denies it.",
    )
    print(f"Verdict: {rp.verdict.value}")

    print("\nCarried forward to the next pass:")
    for item in rp.outputs():
        print(f"  [{item.label.value}] {item.text[:60]}")


if __name__ == "__main__":
    main()
