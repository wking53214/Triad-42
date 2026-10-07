"""Amendment 1: epistemic persistence.

Every item entering or leaving a review pass carries exactly one label, and
that label never changes inside Triad+42. Labels do not decay, drift, or
upgrade here, and there is no relabel operation at all: a labeled item is
immutable. A recommendation that survives ten reviews is still a
recommendation.

Changing what a claim is, or recording that a human adopted it, is not this
package's job. That authority belongs to CCC (the Cognitive Continuity
Constitution), which is the single owner of origin and promotion rules. See
`triad42.ccc_handoff`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import uuid

from ._clock import utcnow
from .errors import IncompleteSubmission


class Label(str, Enum):
    """The six governing epistemic categories."""

    FACT = "FACT"
    INFERENCE = "INFERENCE"
    ASSUMPTION = "ASSUMPTION"
    DECISION = "DECISION"
    RECOMMENDATION = "RECOMMENDATION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class LabeledItem:
    """A statement carrying its epistemic label.

    Immutable. The label travels with the item across passes unchanged.
    `origin_pass` records where the item came from, including a prior pass,
    so a pass-2 input that was a pass-1 output cannot arrive looking like
    fresh ground truth.

    A label supplied by the caller (for example FACT on a subject) is carried,
    not certified. Triad+42 does not vouch for it; CCC decides what a claim is.
    """

    text: str
    label: Label
    item_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    origin_pass: Optional[str] = None
    created_at: str = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise IncompleteSubmission("A labeled item requires text.")
        if not isinstance(self.label, Label):
            object.__setattr__(self, "label", Label(self.label))

    def carry_forward(self, into_pass: str) -> "LabeledItem":
        """Produce this item as an input to a later pass, label intact."""
        return LabeledItem(
            text=self.text,
            label=self.label,
            item_id=self.item_id,
            origin_pass=self.origin_pass or into_pass,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "text": self.text,
            "label": self.label.value,
            "origin_pass": self.origin_pass,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LabeledItem":
        return cls(
            text=data["text"],
            label=Label(data["label"]),
            item_id=data["item_id"],
            origin_pass=data.get("origin_pass"),
            created_at=data.get("created_at", utcnow()),
        )
