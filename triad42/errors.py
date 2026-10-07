"""Rejection errors.

Nothing in this package fails silently. Every rejection carries a reason.
"""


class Triad42Error(Exception):
    """Base for every rejection raised by the harness."""


class StageOrderError(Triad42Error):
    """A stage was run out of sequence."""


class EpistemicViolation(Triad42Error):
    """An epistemic-label violation.

    Kept for compatibility. As of 3.0.0 Triad+42 has no relabel operation, so
    nothing in this package raises it; label and promotion rules live in CCC.
    """


class IncompleteSubmission(Triad42Error):
    """A submitted artifact is missing a field the framework requires."""


class InadmissibleVerdict(Triad42Error):
    """A declared verdict is not supported by the recorded findings."""


class UnexaminedMandate(Triad42Error):
    """A cluster reached the mandate threshold and was never examined."""


class EscalationError(Triad42Error):
    """An escalation was attempted that the framework does not permit."""


class GroundingError(Triad42Error):
    """A Green grounding violated the break-disclosure or reaffirmation rule."""
