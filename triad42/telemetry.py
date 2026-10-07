"""Read-only operational telemetry.

Telemetry describes what a pass recorded. It is intentionally not consulted
by verdict, severity, epistemic, provenance, or novelty logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from .review import ReviewPass, Session
from .deepthought import DeepThoughtResult


@dataclass(frozen=True)
class PassTelemetry:
    pass_id: str
    stages_closed: int
    findings: int
    examinations: int
    escalations: int
    rejected_candidates: int
    gate_failures: int
    human_decision_routes: int
    human_overrides: int
    retrieval_records: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "pass_id": self.pass_id,
            "stages_closed": self.stages_closed,
            "findings": self.findings,
            "examinations": self.examinations,
            "escalations": self.escalations,
            "rejected_candidates": self.rejected_candidates,
            "gate_failures": self.gate_failures,
            "human_decision_routes": self.human_decision_routes,
            "human_overrides": self.human_overrides,
            "retrieval_records": self.retrieval_records,
        }


def collect_pass_telemetry(
    review_pass: ReviewPass, session: Optional[Session] = None
) -> PassTelemetry:
    """Collect counters without mutating or evaluating the pass."""
    rejected = 0
    gate_failures = 0
    if review_pass.deep_thought is not None:
        if review_pass.deep_thought.result is DeepThoughtResult.NO_42_IDENTIFIED:
            rejected = int(bool(review_pass.deep_thought.candidate))
            gate_failures = int(review_pass.deep_thought.failed_at is not None)

    retrieved = (
        len(session.candidates.query(pass_id=review_pass.pass_id))
        if session is not None
        else 0
    )
    return PassTelemetry(
        pass_id=review_pass.pass_id,
        stages_closed=review_pass.closed_stage_count,
        findings=len(review_pass.red.findings),
        examinations=len(review_pass.red.examinations),
        escalations=sum(
            1 for e in review_pass.red.examinations if e.produced_finding_id
        ),
        rejected_candidates=rejected,
        gate_failures=gate_failures,
        human_decision_routes=int(review_pass.red.routed_to_human()),
        human_overrides=int(review_pass.disagreement_override is not None),
        retrieval_records=retrieved,
    )
