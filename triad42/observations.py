"""Non-destructive linguistic observations.

These signals describe surface wording for reviewer attention. They never
rewrite text and never determine labels, severity, truth, causality, or
verdicts.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any


SIGNALS = (
    "first-person-framing-present",
    "uncertainty-language-present",
    "causal-language-present",
    "absolute-claim-present",
    "modal-language-present",
    "quantitative-claim-present",
    "evaluative-language-present",
)

_PATTERNS = {
    "first-person-framing-present": r"\b(?:i|we|my|our|me|us)\b",
    "uncertainty-language-present": (
        r"\b(?:maybe|perhaps|possibly|likely|unlikely|appears?|seems?|might|"
        r"may|could|uncertain|unclear|approximately)\b"
    ),
    "causal-language-present": (
        r"\b(?:because|therefore|causes?|caused|causing|leads?|result(?:s|ed|"
        r"ing)?|due to|as a result)\b"
    ),
    "absolute-claim-present": (
        r"\b(?:always|never|all|none|every|certainly)\b"
    ),
    "modal-language-present": r"\b(?:must|shall|should|will|can|cannot|may|might)\b",
    "quantitative-claim-present": r"(?<!\w)(?:\d+(?:[.,]\d+)?%?|\$[\d.,]+)(?!\w)",
    "evaluative-language-present": (
        r"\b(?:good|bad|safe|unsafe|better|worse|effective|ineffective|"
        r"important|unacceptable|successful|failure)\b"
    ),
}


@dataclass(frozen=True)
class LinguisticObservation:
    """Signals observed in the exact original text."""

    original_text: str
    signals: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.original_text.strip():
            raise ValueError("Linguistic observation requires original text.")
        unknown = set(self.signals) - set(SIGNALS)
        if unknown:
            raise ValueError(f"Unknown linguistic signals: {sorted(unknown)}.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "original_text": self.original_text,
            "signals": list(self.signals),
        }


def observe_language(text: str) -> LinguisticObservation:
    """Detect surface patterns without changing or classifying the text."""
    if not text.strip():
        raise ValueError("Linguistic observation requires original text.")
    found = tuple(
        signal
        for signal in SIGNALS
        if re.search(_PATTERNS[signal], text, flags=re.IGNORECASE)
    )
    return LinguisticObservation(original_text=text, signals=found)
