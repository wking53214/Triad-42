"""The pass and the session.

Stage order is enforced: Red, then Gray, then Green, then 42. The order is
load-bearing. Green's job is to find correspondence with reality, which
produces confidence. Red's job is to break claims. If Green ran first, its
confidence would reach Red as a premise, and Red would inherit it.

Verdicts are declared by the reviewer, not computed by the harness. What the
harness does is refuse a verdict the record cannot carry. That preserves the
advisory rule: the mechanism analyses, the human decides.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import json
import uuid

from ._clock import utcnow
from .deepthought import GateRecord, DeepThoughtResult, no_candidate
from .epistemic import LabeledItem, Label
from .errors import (
    InadmissibleVerdict,
    IncompleteSubmission,
    StageOrderError,
)
from .findings import (
    Finding,
    FindingLedger,
    Severity,
    ExaminationOutcome,
)
from .lenses import (
    CrossCuttingObservation,
    Grounding,
    GroundingLedger,
    StructuralAssessment,
    StructuralObservation,
)
from .provenance import Origin, ProvenanceGraph
from .retrieval import CandidateKind, CandidateRecord, CandidateStore, SurfacingStatus


class Stage(str, Enum):
    RED = "RED"
    GRAY = "GRAY"
    GREEN = "GREEN"
    DEEP_THOUGHT = "42"


STAGE_ORDER: tuple[Stage, ...] = (Stage.RED, Stage.GRAY, Stage.GREEN, Stage.DEEP_THOUGHT)


class Verdict(str, Enum):
    """Terminal outputs. The negative ones are first-class results."""

    NO_BLOCKING_FINDINGS = "NO_BLOCKING_FINDINGS"
    FAILS = "FAILS"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    REQUIRES_HUMAN_DECISION = "REQUIRES_HUMAN_DECISION"


class ReviewPass:
    """One complete Triad+42 pass over one subject."""

    def __init__(
        self,
        subject: LabeledItem,
        inputs: Optional[list[LabeledItem]] = None,
        pass_id: Optional[str] = None,
    ) -> None:
        if not isinstance(subject, LabeledItem):
            raise IncompleteSubmission(
                "The subject of review must carry an epistemic label."
            )
        self.pass_id = pass_id or uuid.uuid4().hex[:12]
        self.subject = subject
        self.inputs: list[LabeledItem] = list(inputs or [])
        for item in self.inputs:
            if not isinstance(item, LabeledItem):
                raise IncompleteSubmission(
                    "Every input must carry an epistemic label. Unlabelled "
                    "input is how a recommendation becomes a premise."
                )

        self.red = FindingLedger()
        self._gray: list[StructuralObservation] = []
        self._cross_cutting: list[CrossCuttingObservation] = []
        self._gray_phase = 1
        self.structural_assessment: Optional[StructuralAssessment] = None
        self.assessment_reason: Optional[str] = None
        self.green = GroundingLedger()
        self.deep_thought: Optional[GateRecord] = None

        self.created_at = utcnow()
        self.declared_at: Optional[str] = None
        self._stage_index = 0
        self._closed_stages: list[Stage] = []
        self.verdict: Optional[Verdict] = None
        self.verdict_reason: Optional[str] = None
        self.disagreement_override: Optional[str] = None

    # -- stage sequencing ------------------------------------------------

    @property
    def gray(self) -> tuple[StructuralObservation, ...]:
        """Read-only. Observations go in through add_observation()."""
        return tuple(self._gray)

    @property
    def cross_cutting(self) -> tuple[CrossCuttingObservation, ...]:
        """Read-only. Cross-cutting observations go in through add_cross_cutting()."""
        return tuple(self._cross_cutting)

    @property
    def gray_phase(self) -> int:
        """1 while Gray works independently, 2 once it has seen Red's findings."""
        return self._gray_phase

    @property
    def current_stage(self) -> Optional[Stage]:
        if self._stage_index >= len(STAGE_ORDER):
            return None
        return STAGE_ORDER[self._stage_index]

    def _require(self, stage: Stage) -> None:
        if self.current_stage is not stage:
            done = ", ".join(s.value for s in self._closed_stages) or "none"
            expected = self.current_stage.value if self.current_stage else "none"
            raise StageOrderError(
                f"{stage.value} cannot run now. Completed: {done}. "
                f"Expected next: {expected}. The sequence is Red, Gray, Green, "
                "then 42, and it is not optional."
            )

    def close_stage(self) -> Stage:
        """Finish the current stage and advance."""
        stage = self.current_stage
        if stage is None:
            raise StageOrderError("All stages are already closed.")
        if stage is Stage.RED:
            self.red.assert_mandates_closed()
            self.red.seal()
        if stage is Stage.GRAY and self.structural_assessment is None:
            # Same shape as 42 defaulting to NO 42 IDENTIFIED: when nothing was
            # established, the honest record says so rather than staying blank.
            self.structural_assessment = StructuralAssessment.INSUFFICIENT_TO_ASSESS
            self.assessment_reason = "No assessment was recorded before Gray closed."
        if stage is Stage.GREEN:
            self.green.seal()
        if stage is Stage.DEEP_THOUGHT and self.deep_thought is None:
            self.deep_thought = no_candidate()
        self._closed_stages.append(stage)
        self._stage_index += 1
        return stage

    # -- stage entry points ----------------------------------------------

    def add_finding(self, text: str, severity: Severity, scope: str) -> Finding:
        self._require(Stage.RED)
        return self.red.add(Finding(text=text, severity=severity, scope=scope))

    def examine_cluster(self, scope: str, severity: Severity, outcome, **kwargs):
        self._require(Stage.RED)
        return self.red.examine(scope, severity, outcome, **kwargs)

    def add_observation(self, observation: StructuralObservation) -> StructuralObservation:
        """Phase 1. Gray's independent read of the architecture."""
        self._require(Stage.GRAY)
        if self._gray_phase != 1:
            raise StageOrderError(
                "Gray's independent phase closed when Red's findings were "
                "requested. An observation made after seeing the findings is "
                "not independent of them; record it as a cross-cutting "
                "observation instead."
            )
        self._gray.append(observation)
        return observation

    def red_findings_for_gray(self) -> tuple[Finding, ...]:
        """Hand Red's findings to Gray, sealing Gray's independent phase.

        Requesting the findings is what commits Gray's own work. Gray cannot
        see what Red found without first putting on the record what it found
        without them, which is what keeps Red's framing from shaping Gray's
        structural read.
        """
        self._require(Stage.GRAY)
        self._gray_phase = 2
        return tuple(self.red.findings)

    def add_cross_cutting(
        self, observation: CrossCuttingObservation
    ) -> CrossCuttingObservation:
        """Phase 2. One structural cause appearing across separate scopes."""
        self._require(Stage.GRAY)
        if self._gray_phase != 2:
            raise StageOrderError(
                "Cross-cutting observations belong to Gray's second phase. "
                "Call red_findings_for_gray() first, which seals the "
                "independent observations you have already made."
            )
        known = {f.finding_id: f for f in self.red.findings}
        missing = [fid for fid in observation.finding_ids if fid not in known]
        if missing:
            raise IncompleteSubmission(
                f"Cross-cutting observation cites findings not on the record: "
                f"{missing}."
            )
        actual = {known[fid].scope for fid in observation.finding_ids}
        if not set(observation.scopes) <= actual:
            raise IncompleteSubmission(
                f"Declared scopes {sorted(observation.scopes)} do not match "
                f"the scopes of the cited findings {sorted(actual)}."
            )
        self._cross_cutting.append(observation)
        return observation

    def assess_structure(
        self, assessment: StructuralAssessment, reason: str
    ) -> StructuralAssessment:
        """Gray's affirmative conclusion. Required before Gray closes."""
        self._require(Stage.GRAY)
        if not reason.strip():
            raise IncompleteSubmission("A structural assessment requires a reason.")
        self.structural_assessment = StructuralAssessment(assessment)
        self.assessment_reason = reason
        return self.structural_assessment

    def add_grounding(self, grounding: Grounding) -> Grounding:
        self._require(Stage.GREEN)
        return self.green.add(grounding)

    def record_42(self, record: GateRecord) -> GateRecord:
        self._require(Stage.DEEP_THOUGHT)
        self.deep_thought = record
        return record

    # -- verdict ---------------------------------------------------------

    @property
    def stages_complete(self) -> bool:
        return len(self._closed_stages) == len(STAGE_ORDER)

    @property
    def closed_stage_count(self) -> int:
        """Number of stages closed so far, for read-only observability."""
        return len(self._closed_stages)

    def _disagreement(self) -> bool:
        """Red says stop while Gray and Green say the thing holds.

        This used to read Gray's silence as agreement, which conflated "looked
        and found nothing wrong" with "did not look". Gray now says which one
        it is, so the check rests on a statement rather than an absence.
        """
        red_objects = bool(self.red.blocking_findings())
        gray_affirms = self.structural_assessment is StructuralAssessment.STRUCTURE_HOLDS
        green_grounded = self.green.new_grounding_count() > 0
        return red_objects and gray_affirms and green_grounded

    def declare(
        self,
        verdict: Verdict,
        reason: str,
        disagreement_override: Optional[str] = None,
    ) -> Verdict:
        """Declare the pass verdict. The harness checks admissibility only."""
        if not self.stages_complete:
            remaining = [
                s.value for s in STAGE_ORDER if s not in self._closed_stages
            ]
            raise StageOrderError(
                f"A verdict cannot be declared with stages open: {remaining}."
            )
        if self.verdict is not None:
            raise InadmissibleVerdict(
                f"A verdict was already declared for this pass "
                f"({self.verdict.value}). The record is write-once: a second "
                "declaration would overwrite it with no trace of the first."
            )
        verdict = Verdict(verdict)
        if not reason.strip():
            raise IncompleteSubmission("A verdict requires a stated reason.")

        blocking = self.red.blocking_findings()

        if verdict is Verdict.FAILS and not blocking:
            raise InadmissibleVerdict(
                "FAILS may rest only on CRITICAL or HIGH findings. The record "
                f"holds {len(self.red.findings)} finding(s), none blocking. "
                "Volume does not aggregate into failure."
            )

        if verdict is Verdict.NO_BLOCKING_FINDINGS and blocking:
            ids = [f.finding_id for f in blocking]
            raise InadmissibleVerdict(
                f"Blocking findings remain on the record: {ids}."
            )

        if self.red.routed_to_human() and verdict is not Verdict.REQUIRES_HUMAN_DECISION:
            raise InadmissibleVerdict(
                "A cluster examination returned REQUIRES HUMAN DECISION. That "
                "result cannot be absorbed into another verdict."
            )

        if self._disagreement() and verdict is not Verdict.REQUIRES_HUMAN_DECISION:
            if not (disagreement_override or "").strip():
                raise InadmissibleVerdict(
                    "Red raised blocking findings while Gray found no "
                    "structural problem and Green established grounding. "
                    "Component disagreement routes to human decision unless a "
                    "written override is supplied."
                )
            self.disagreement_override = disagreement_override

        self.verdict = verdict
        self.verdict_reason = reason
        self.declared_at = utcnow()
        return verdict

    # -- outputs ----------------------------------------------------------

    def outputs(self) -> list[LabeledItem]:
        """What this pass produces, labelled for carry-forward.

        Findings are inferences. A 42 that clears the gate is a
        recommendation. Nothing produced here is ever a fact or a decision.
        """
        out: list[LabeledItem] = []
        for f in self.red.findings:
            out.append(
                LabeledItem(
                    text=f.text, label=Label.INFERENCE, origin_pass=self.pass_id
                )
            )
        if self.deep_thought and self.deep_thought.result is not DeepThoughtResult.NO_42_IDENTIFIED:
            out.append(
                LabeledItem(
                    text=self.deep_thought.candidate,
                    label=Label.RECOMMENDATION,
                    origin_pass=self.pass_id,
                )
            )
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "pass_id": self.pass_id,
            "subject": self.subject.to_dict(),
            "inputs": [i.to_dict() for i in self.inputs],
            "stages_closed": [s.value for s in self._closed_stages],
            "red": self.red.to_dict(),
            "gray": [o.to_dict() for o in self._gray],
            "gray_phase": self._gray_phase,
            "cross_cutting": [o.to_dict() for o in self._cross_cutting],
            "structural_assessment": (
                self.structural_assessment.value
                if self.structural_assessment
                else None
            ),
            "assessment_reason": self.assessment_reason,
            "green": self.green.to_dict(),
            "deep_thought": self.deep_thought.to_dict() if self.deep_thought else None,
            "created_at": self.created_at,
            "declared_at": self.declared_at,
            "verdict": self.verdict.value if self.verdict else None,
            "verdict_reason": self.verdict_reason,
            "disagreement_override": self.disagreement_override,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


@dataclass
class Session:
    """A sequence of passes sharing history, provenance, and a candidate store.

    History is what makes two rules enforceable: repetition is not
    verification, and an analogy used twice is reaffirmation rather than a
    second discovery.

    The provenance graph and the candidate store sit here rather than inside a
    pass, because both outlive any single review.
    """

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=utcnow)
    passes: list[ReviewPass] = field(default_factory=list)
    graph: ProvenanceGraph = field(default_factory=ProvenanceGraph)
    candidates: CandidateStore = field(default_factory=CandidateStore)

    def start_pass(
        self,
        subject: LabeledItem,
        inputs: Optional[list[LabeledItem]] = None,
        subject_origin: Origin = Origin.PROVENANCE_UNCERTAIN,
    ) -> ReviewPass:
        carried: list[LabeledItem] = []
        for item in inputs or []:
            carried.append(item.carry_forward(self.session_id))
        rp = ReviewPass(subject=subject, inputs=carried)
        rp.green.seed_prior_keys(self.analogy_keys())
        if not self.graph.has(subject.item_id):
            self.graph.register(subject, subject_origin)
        self.passes.append(rp)
        return rp

    def harvest(self, rp: ReviewPass, surfaced_ids: Optional[set[str]] = None) -> int:
        """Move everything a pass produced into the candidate store.

        `surfaced_ids` names what was actually shown to the human. Everything
        else is recorded as not surfaced, with a reason. Nothing is dropped.
        """
        surfaced_ids = surfaced_ids or set()
        n = 0

        def status_for(item_id: str) -> tuple[SurfacingStatus, str]:
            if item_id in surfaced_ids:
                return SurfacingStatus.SURFACED, "Presented to the human."
            return (
                SurfacingStatus.NOT_SURFACED,
                "Recorded but not presented. Retrievable on request.",
            )

        for f in rp.red.findings:
            st, why = status_for(f.finding_id)
            self.candidates.record(CandidateRecord(
                text=f.text, kind=CandidateKind.FINDING, status=st, reason=why,
                pass_id=rp.pass_id, scope=f.scope, source_id=f.finding_id,
            ))
            n += 1
        for e in rp.red.examinations:
            st, why = status_for(e.scope)
            self.candidates.record(CandidateRecord(
                text=f"{e.outcome.value} on {e.scope}/{e.severity.value}",
                kind=CandidateKind.EXAMINATION, status=st, reason=why,
                pass_id=rp.pass_id, scope=e.scope,
            ))
            n += 1
        for o in rp.gray:
            st, why = status_for(o.observation_id)
            self.candidates.record(CandidateRecord(
                text=o.text, kind=CandidateKind.OBSERVATION, status=st, reason=why,
                pass_id=rp.pass_id, scope=o.scope, source_id=o.observation_id,
            ))
            n += 1
        for g in rp.green.groundings:
            st, why = status_for(g.grounding_id)
            self.candidates.record(CandidateRecord(
                text=f"{g.real_system}: {g.where_it_holds}",
                kind=CandidateKind.GROUNDING, status=st, reason=why,
                pass_id=rp.pass_id, source_id=g.grounding_id,
            ))
            n += 1
        dt = rp.deep_thought
        if dt is not None and dt.candidate:
            rejected = dt.result is DeepThoughtResult.NO_42_IDENTIFIED
            kind = CandidateKind.REJECTED_INSIGHT if rejected else CandidateKind.INSIGHT
            reason = (
                f"Failed the novelty gate at {dt.failed_at.value}. Retained "
                "because a rejected insight is still a detected one."
                if rejected and dt.failed_at
                else "Cleared the novelty gate."
            )
            self.candidates.record(CandidateRecord(
                text=dt.candidate, kind=kind,
                status=SurfacingStatus.NOT_SURFACED if rejected else SurfacingStatus.SURFACED,
                reason=reason, pass_id=rp.pass_id,
            ))
            n += 1
        return n

    def analogy_keys(self) -> set[str]:
        keys: set[str] = set()
        for p in self.passes:
            keys |= p.green.keys
        return keys

    def prior_outputs(self) -> list[LabeledItem]:
        out: list[LabeledItem] = []
        for p in self.passes:
            out.extend(p.outputs())
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "passes": [p.to_dict() for p in self.passes],
            "provenance": self.graph.to_dict(),
            "candidates": self.candidates.to_dict(),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)
