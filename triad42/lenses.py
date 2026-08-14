"""Gray and Green.

Gray records structural observations. It carries no severity scheme by
default (see DECISIONS_PENDING.md, item 5).

Green is governed by Amendment 3: every grounding must state where the
analogy breaks, and must declare whether it is new grounding or a
reaffirmation of grounding already established in this session. Analogy is
grounding, never proof.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import uuid

from .errors import GroundingError, IncompleteSubmission


class DistinctionKind(str, Enum):
    """The distinctions Gray is charged with preserving."""

    AUTHORITY_CAPABILITY_EXECUTION = "AUTHORITY != CAPABILITY != EXECUTION"
    EPISTEMIC_CATEGORY = "FACT != INFERENCE != RECOMMENDATION != DECISION"
    WORKFLOW_GOVERNANCE = "WORKFLOW != GOVERNANCE"
    OTHER = "OTHER"


class Disposition(str, Enum):
    """What Gray decides when two rules overlap."""

    CONSOLIDATE = "CONSOLIDATE"
    EXPLICITLY_SCOPE = "EXPLICITLY_SCOPE"
    INHERIT = "INHERIT"
    RETAIN_SEPARATELY = "RETAIN_SEPARATELY"


@dataclass
class StructuralObservation:
    """One Gray observation about relationships rather than statements."""

    text: str
    scope: str
    distinction: DistinctionKind = DistinctionKind.OTHER
    disposition: Optional[Disposition] = None
    disposition_reason: Optional[str] = None
    observation_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise IncompleteSubmission("A structural observation requires text.")
        if not self.scope.strip():
            raise IncompleteSubmission("A structural observation requires a scope.")
        if not isinstance(self.distinction, DistinctionKind):
            self.distinction = DistinctionKind(self.distinction)
        if self.disposition is not None:
            self.disposition = Disposition(self.disposition)
            if self.disposition is Disposition.RETAIN_SEPARATELY and not (
                self.disposition_reason or ""
            ).strip():
                raise IncompleteSubmission(
                    "Retaining overlapping rules separately requires a "
                    "demonstrable reason."
                )

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "text": self.text,
            "scope": self.scope,
            "distinction": self.distinction.value,
            "disposition": self.disposition.value if self.disposition else None,
            "disposition_reason": self.disposition_reason,
        }


class GroundingStatus(str, Enum):
    NEW_GROUNDING = "NEW_GROUNDING"
    REAFFIRMATION = "REAFFIRMATION_OF_PRIOR_GROUNDING"


@dataclass
class Grounding:
    """One Green grounding.

    `analogy_key` is a stable identifier for the analogy itself, so the same
    comparison used twice in a session is detected as reaffirmation rather
    than counted as a second discovery.
    """

    analogy_key: str
    real_system: str
    where_it_holds: str
    where_it_breaks: str
    status: GroundingStatus = GroundingStatus.NEW_GROUNDING
    exposes: Optional[str] = None
    grounding_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])

    def __post_init__(self) -> None:
        for name in ("analogy_key", "real_system", "where_it_holds"):
            if not getattr(self, name).strip():
                raise IncompleteSubmission(f"A grounding requires {name}.")
        if not self.where_it_breaks.strip():
            raise GroundingError(
                "A grounding must state where the analogy fails, not only "
                "where it holds. A grounding without a break statement is "
                "incomplete and is rejected."
            )
        if not isinstance(self.status, GroundingStatus):
            self.status = GroundingStatus(self.status)

    def to_dict(self) -> dict[str, Any]:
        return {
            "grounding_id": self.grounding_id,
            "analogy_key": self.analogy_key,
            "real_system": self.real_system,
            "where_it_holds": self.where_it_holds,
            "where_it_breaks": self.where_it_breaks,
            "status": self.status.value,
            "exposes": self.exposes,
        }


class GroundingLedger:
    """Tracks analogies used across a session so repetition is visible."""

    def __init__(self) -> None:
        self._groundings: list[Grounding] = []
        self._seen_keys: set[str] = set()

    def seed_prior_keys(self, keys: set[str]) -> None:
        """Load analogy keys established by earlier passes in this session."""
        self._seen_keys |= {k.casefold() for k in keys}

    def add(self, grounding: Grounding) -> Grounding:
        key = grounding.analogy_key.casefold()
        already = key in self._seen_keys
        if already and grounding.status is GroundingStatus.NEW_GROUNDING:
            raise GroundingError(
                f"Analogy {grounding.analogy_key!r} already established "
                "grounding in this session. Repeating it is reaffirmation, "
                "not new grounding. Familiarity is not validation."
            )
        if not already and grounding.status is GroundingStatus.REAFFIRMATION:
            raise GroundingError(
                f"Analogy {grounding.analogy_key!r} has not been used in this "
                "session, so it cannot reaffirm prior grounding."
            )
        self._seen_keys.add(key)
        self._groundings.append(grounding)
        return grounding

    @property
    def groundings(self) -> list[Grounding]:
        return list(self._groundings)

    @property
    def keys(self) -> set[str]:
        return set(self._seen_keys)

    def new_grounding_count(self) -> int:
        return sum(
            1 for g in self._groundings if g.status is GroundingStatus.NEW_GROUNDING
        )

    def to_dict(self) -> dict[str, Any]:
        return {"groundings": [g.to_dict() for g in self._groundings]}
