"""Amendment 1: epistemic persistence.

Every item entering or leaving a review pass carries exactly one label.
Labels do not decay, drift, or upgrade. A recommendation that survives ten
reviews is still a recommendation. The only thing that may change a label is
an explicit, recorded human authorization event.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import uuid

from .errors import EpistemicViolation, IncompleteSubmission


class Label(str, Enum):
    """The six governing epistemic categories."""

    FACT = "FACT"
    INFERENCE = "INFERENCE"
    ASSUMPTION = "ASSUMPTION"
    DECISION = "DECISION"
    RECOMMENDATION = "RECOMMENDATION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Authorization:
    """A recorded human authorization for a label change.

    The harness never creates one of these on its own. A caller must supply
    it, and the identity of the authorizing human is required.
    """

    authorized_by: str
    reason: str

    def __post_init__(self) -> None:
        if not self.authorized_by.strip():
            raise IncompleteSubmission("Authorization requires an authorizing human.")
        if not self.reason.strip():
            raise IncompleteSubmission("Authorization requires a stated reason.")

    def to_dict(self) -> dict[str, Any]:
        return {"authorized_by": self.authorized_by, "reason": self.reason}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Authorization":
        return cls(authorized_by=data["authorized_by"], reason=data["reason"])


@dataclass
class LabeledItem:
    """A statement carrying its epistemic label and its history.

    The label travels with the item across passes. `provenance` records where
    the item came from, including a prior pass, so a pass-2 input that was a
    pass-1 output cannot arrive looking like fresh ground truth.
    """

    text: str
    label: Label
    item_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    origin_pass: Optional[str] = None
    label_history: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise IncompleteSubmission("A labeled item requires text.")
        if not isinstance(self.label, Label):
            self.label = Label(self.label)

    def relabel(self, new_label: Label, authorization: Authorization) -> None:
        """Change the label. Requires an explicit human authorization event."""
        if not isinstance(authorization, Authorization):
            raise EpistemicViolation(
                f"Cannot change label {self.label.value} -> "
                f"{Label(new_label).value} without a recorded human "
                "authorization. Labels do not upgrade through review."
            )
        new_label = Label(new_label)
        self.label_history.append(
            {
                "from": self.label.value,
                "to": new_label.value,
                "authorization": authorization.to_dict(),
            }
        )
        self.label = new_label

    def carry_forward(self, into_pass: str) -> "LabeledItem":
        """Produce this item as an input to a later pass, label intact."""
        return LabeledItem(
            text=self.text,
            label=self.label,
            item_id=self.item_id,
            origin_pass=self.origin_pass or into_pass,
            label_history=list(self.label_history),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "text": self.text,
            "label": self.label.value,
            "origin_pass": self.origin_pass,
            "label_history": list(self.label_history),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LabeledItem":
        return cls(
            text=data["text"],
            label=Label(data["label"]),
            item_id=data["item_id"],
            origin_pass=data.get("origin_pass"),
            label_history=list(data.get("label_history", [])),
        )
