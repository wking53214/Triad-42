"""42 / Deep Thought.

42 is not the fourth member of the Triad. It is a separate mechanism that
searches for high-leverage synthesis emerging from Red, Gray, and Green.

Every candidate passes five checks in order. Failing any check ends the gate.
NO 42 IDENTIFIED is a legitimate and complete result. The gate must never
manufacture novelty because the format expects a 42.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .errors import IncompleteSubmission


class Check(str, Enum):
    """The five novelty checks, in the order they must be applied."""

    NOT_ALREADY_STATED = "NOT_ALREADY_STATED"
    NOT_MERELY_RENAMING = "NOT_MERELY_RENAMING"
    ABSTRACTION_LABELLED = "ABSTRACTION_LABELLED"
    NEW_RELATIONSHIP = "NEW_RELATIONSHIP"
    MATERIALLY_CONSEQUENTIAL = "MATERIALLY_CONSEQUENTIAL"


CHECK_ORDER: tuple[Check, ...] = (
    Check.NOT_ALREADY_STATED,
    Check.NOT_MERELY_RENAMING,
    Check.ABSTRACTION_LABELLED,
    Check.NEW_RELATIONSHIP,
    Check.MATERIALLY_CONSEQUENTIAL,
)


class DeepThoughtResult(str, Enum):
    NOVEL_INSIGHT = "NOVEL_INSIGHT"
    MEANINGFUL_ABSTRACTION = "MEANINGFUL_ABSTRACTION"
    NO_42_IDENTIFIED = "NO_42_IDENTIFIED"


#: Areas an insight must plausibly affect to count as materially consequential.
CONSEQUENCE_AREAS = (
    "architecture",
    "governance",
    "reasoning",
    "workflow",
    "boundaries",
    "reliability",
    "safety",
    "capability",
    "integration",
    "future design decisions",
)


@dataclass
class CheckAnswer:
    """One reviewer answer to one check, with reasoning."""

    check: Check
    passed: bool
    reasoning: str

    def __post_init__(self) -> None:
        if not isinstance(self.check, Check):
            self.check = Check(self.check)
        if not self.reasoning.strip():
            raise IncompleteSubmission(
                f"Check {self.check.value} requires stated reasoning. A bare "
                "yes or no does not establish the answer."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "check": self.check.value,
            "passed": self.passed,
            "reasoning": self.reasoning,
        }


@dataclass
class Candidate:
    """A candidate 42 submitted to the gate."""

    text: str
    consequence_area: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise IncompleteSubmission("A candidate insight requires text.")


#: Marks a record as produced by run_gate() or no_candidate(). A record built by
#: hand does not carry it, and ReviewPass.record_42() refuses it. This stops a
#: caller who is not trying to cheat from skipping the five checks by accident;
#: it cannot stop one who imports this private name.
_ISSUED = object()


@dataclass(frozen=True)
class GateRecord:
    """The full record of one candidate's trip through the gate.

    Frozen: the result and the answers cannot be edited after the gate issues it.
    """

    candidate: str
    result: DeepThoughtResult
    answers: tuple[CheckAnswer, ...] = ()
    failed_at: Optional[Check] = None
    consequence_area: Optional[str] = None
    _issued: object = field(default=None, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "answers", tuple(self.answers))

    @property
    def issued_by_gate(self) -> bool:
        """True only for a record that run_gate() or no_candidate() produced."""
        return self._issued is _ISSUED

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate,
            "result": self.result.value,
            "answers": [a.to_dict() for a in self.answers],
            "failed_at": self.failed_at.value if self.failed_at else None,
            "consequence_area": self.consequence_area,
        }


def run_gate(candidate: Candidate, answers: list[CheckAnswer]) -> GateRecord:
    """Run the five checks in order and return the result.

    Check 3 is not a pass/fail in the same sense as the others. Answering it
    "this abstracts existing structure" does not end the gate; it fixes the
    label the result may carry. An abstraction can still be valuable, but it
    must be presented as an abstraction rather than as a discovery.
    """
    supplied = {a.check: a for a in answers}
    ordered: list[CheckAnswer] = []
    is_abstraction = False

    for check in CHECK_ORDER:
        if check not in supplied:
            raise IncompleteSubmission(
                f"The gate requires an answer for {check.value}. Checks are "
                "applied in order and none may be skipped."
            )
        answer = supplied[check]
        ordered.append(answer)

        if check is Check.ABSTRACTION_LABELLED:
            # passed=False here means "yes, this is an abstraction".
            is_abstraction = not answer.passed
            continue

        if not answer.passed:
            return GateRecord(
                candidate=candidate.text,
                result=DeepThoughtResult.NO_42_IDENTIFIED,
                answers=tuple(ordered),
                failed_at=check,
                _issued=_ISSUED,
            )

    if is_abstraction:
        result = DeepThoughtResult.MEANINGFUL_ABSTRACTION
    else:
        result = DeepThoughtResult.NOVEL_INSIGHT

    if not (candidate.consequence_area or "").strip():
        raise IncompleteSubmission(
            "An insight that clears the gate must name what it affects. "
            f"Expected one of: {', '.join(CONSEQUENCE_AREAS)}."
        )

    return GateRecord(
        candidate=candidate.text,
        result=result,
        answers=tuple(ordered),
        consequence_area=candidate.consequence_area,
        _issued=_ISSUED,
    )


def no_candidate() -> GateRecord:
    """The correct result when no candidate insight exists at all."""
    return GateRecord(
        candidate="",
        result=DeepThoughtResult.NO_42_IDENTIFIED,
        answers=(),
        failed_at=None,
        _issued=_ISSUED,
    )
