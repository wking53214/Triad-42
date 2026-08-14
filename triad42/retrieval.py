"""Retrieval: preserved but unfindable is not preserved.

Anything the mechanism detects is stored, whether or not it was shown to the
human. Not surfacing something is a presentation decision, never a deletion.
Every candidate stays queryable, and the reason it was or was not surfaced is
part of the record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional
import uuid

from .errors import IncompleteSubmission


class CandidateKind(str, Enum):
    FINDING = "FINDING"
    OBSERVATION = "OBSERVATION"
    GROUNDING = "GROUNDING"
    INSIGHT = "INSIGHT"
    REJECTED_INSIGHT = "REJECTED_INSIGHT"
    EXAMINATION = "EXAMINATION"
    CONFLICT = "CONFLICT"


class SurfacingStatus(str, Enum):
    SURFACED = "SURFACED"
    NOT_SURFACED = "NOT_SURFACED"


@dataclass
class CandidateRecord:
    """One detected item, with the reason it was or was not shown."""

    text: str
    kind: CandidateKind
    status: SurfacingStatus
    reason: str
    pass_id: Optional[str] = None
    scope: Optional[str] = None
    source_id: Optional[str] = None
    candidate_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise IncompleteSubmission("A candidate requires text.")
        if not self.reason.strip():
            raise IncompleteSubmission(
                "A candidate requires a stated reason for its surfacing status. "
                "Silent non-surfacing is indistinguishable from suppression."
            )
        self.kind = CandidateKind(self.kind)
        self.status = SurfacingStatus(self.status)

    @property
    def surfaced(self) -> bool:
        return self.status is SurfacingStatus.SURFACED

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "text": self.text,
            "kind": self.kind.value,
            "status": self.status.value,
            "reason": self.reason,
            "pass_id": self.pass_id,
            "scope": self.scope,
            "source_id": self.source_id,
        }


class CandidateStore:
    """Append-only. Nothing here is ever removed by the system."""

    def __init__(self) -> None:
        self._candidates: list[CandidateRecord] = []

    def record(self, candidate: CandidateRecord) -> CandidateRecord:
        self._candidates.append(candidate)
        return candidate

    def all(self) -> list[CandidateRecord]:
        return list(self._candidates)

    def query(
        self,
        kind: Optional[CandidateKind] = None,
        status: Optional[SurfacingStatus] = None,
        pass_id: Optional[str] = None,
        scope: Optional[str] = None,
        predicate: Optional[Callable[[CandidateRecord], bool]] = None,
    ) -> list[CandidateRecord]:
        out = self._candidates
        if kind is not None:
            kind = CandidateKind(kind)
            out = [c for c in out if c.kind is kind]
        if status is not None:
            status = SurfacingStatus(status)
            out = [c for c in out if c.status is status]
        if pass_id is not None:
            out = [c for c in out if c.pass_id == pass_id]
        if scope is not None:
            out = [c for c in out if c.scope == scope]
        if predicate is not None:
            out = [c for c in out if predicate(c)]
        return list(out)

    def not_surfaced(self) -> list[CandidateRecord]:
        """The question the human must always be able to ask."""
        return self.query(status=SurfacingStatus.NOT_SURFACED)

    def to_dict(self) -> dict[str, Any]:
        return {"candidates": [c.to_dict() for c in self._candidates]}
