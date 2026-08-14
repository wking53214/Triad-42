"""Two-phase Gray, run against the real defects found in v2.0.0.

The three findings below are the actual bugs an adversarial pass turned up.
Each sat in a different subsystem, so Red's clustering could not connect them:
clustering measures accumulation inside one scope, on purpose.

Gray connects them, and only after committing what it saw on its own.

Run with: python3 example_cross_cutting.py
"""

from triad42 import (
    CrossCuttingObservation,
    DistinctionKind,
    Label,
    LabeledItem,
    Session,
    Severity,
    StructuralAssessment,
    StructuralObservation,
    Verdict,
)


def main() -> None:
    session = Session()
    rp = session.start_pass(
        LabeledItem("The v2.0.0 governance boundaries as implemented.",
                    Label.ASSUMPTION)
    )

    # ---- RED: three findings, three different subsystems ----------------
    a = rp.add_finding(
        "relabel() reaches FACT without consulting the provenance graph.",
        Severity.CRITICAL, scope="provenance")
    b = rp.add_finding(
        "The Red ledger accepts findings after the stage has closed.",
        Severity.HIGH, scope="findings")
    c = rp.add_finding(
        "A verdict can be declared twice, overwriting the first.",
        Severity.HIGH, scope="review")

    for cluster in rp.red.clusters():
        print(f"  Red cluster {cluster.scope}/{cluster.severity.value}: "
              f"{cluster.count} finding, state {cluster.state.value}")
    print("  Red sees three anomalies. No cluster forms. That is correct.\n")
    rp.close_stage()

    # ---- GRAY phase 1: independent read ----------------------------------
    rp.add_observation(StructuralObservation(
        text="Authority to change a label is held in two places at once.",
        scope="governance",
        distinction=DistinctionKind.AUTHORITY_CAPABILITY_EXECUTION,
    ))
    print(f"  Gray phase {rp.gray_phase}: independent observation recorded.")

    # ---- GRAY phase 2: findings handed over, phase 1 sealed --------------
    findings = rp.red_findings_for_gray()
    print(f"  Gray phase {rp.gray_phase}: received {len(findings)} findings.\n")

    cc = rp.add_cross_cutting(CrossCuttingObservation(
        shared_cause=(
            "Every guard is implemented at the convenience method while the "
            "object it guards stays publicly mutable. Three subsystems, one "
            "defect."
        ),
        finding_ids=(a.finding_id, b.finding_id, c.finding_id),
        scopes=("provenance", "findings", "review"),
        distinction=DistinctionKind.AUTHORITY_CAPABILITY_EXECUTION,
    ))
    print(f"  Cross-cutting cause found across {len(cc.scopes)} scopes:")
    print(f"    {cc.shared_cause}\n")

    severities = [f.severity.value for f in rp.red.findings]
    rp.assess_structure(
        StructuralAssessment.STRUCTURE_COMPROMISED,
        "One architectural defect appears in three subsystems.",
    )
    print(f"  Severities unchanged by Gray: {severities}")
    print(f"  Gray's assessment: {rp.structural_assessment.value}\n")
    rp.close_stage()
    rp.close_stage()  # green
    rp.close_stage()  # 42

    rp.declare(Verdict.FAILS,
               "A CRITICAL finding stands, and Gray reports the structure "
               "compromised across three subsystems.")
    print(f"  Verdict: {rp.verdict.value}")


if __name__ == "__main__":
    main()
