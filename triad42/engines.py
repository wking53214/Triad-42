"""Reasoning engines: the seam, deliberately empty.

Nothing in this module is implemented. It exists to state precisely what an
automated Red, Gray, or Green would have to produce, and to record the reason
nothing fills those slots yet.

THE OPEN PROBLEM
----------------
If Red, Gray, and Green are the same underlying model wearing three sets of
instructions, there is currently no way to demonstrate that they stayed
distinct. Three prompts that collapse into one reviewer in three costumes
would produce output that looks like a Triad and is not one, and nothing here
or in the specification says how to detect that.

That is not an engineering gap. It is an unanswered design question, and it
is the reason these are protocols rather than classes.

THE SECOND PROBLEM
------------------
Severity is what gates a FAILS verdict. Any component that assigns severity
therefore holds veto power. An automated Red that assigned its own severity
would acquire authority the framework denies it. Whatever eventually fills
the Red slot must either leave severity to a human or be granted that
authority explicitly and knowingly.

WHAT WOULD HAVE TO BE TRUE BEFORE ANYTHING IS BUILT HERE
--------------------------------------------------------
1. A stated test that distinguishes three working lenses from one lens run
   three times, with a defined failure threshold.
2. A decision on whether an automated lens may assign severity.
3. A decision on whether lens output enters the record as
   ASSISTANT_PROPOSED or MACHINE_DERIVED, and whether it may ever support a
   FACT.
4. A replaceable model boundary, so no provider-specific call reaches the
   rest of the package.

Until all four are answered, this module stays empty by design.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from .deepthought import GateRecord
from .epistemic import LabeledItem
from .lenses import Grounding, StructuralObservation


class NotYetSpecified(NotImplementedError):
    """Raised if anything tries to use the unbuilt reasoning layer."""


@runtime_checkable
class RedLens(Protocol):
    """Would return findings WITHOUT severity. Severity stays with the human.

    The return shape is (text, scope) pairs. Severity is deliberately absent:
    see THE SECOND PROBLEM above.
    """

    def analyze(self, subject: LabeledItem, context: Any) -> list[tuple[str, str]]:
        ...


@runtime_checkable
class GrayLens(Protocol):
    """Would return structural observations."""

    def analyze(
        self, subject: LabeledItem, context: Any
    ) -> list[StructuralObservation]:
        ...


@runtime_checkable
class GreenLens(Protocol):
    """Would return groundings, each including where the analogy breaks."""

    def analyze(self, subject: LabeledItem, context: Any) -> list[Grounding]:
        ...


@runtime_checkable
class DeepThoughtEngine(Protocol):
    """Would propose candidate insights and run them through the gate.

    It proposes. It never ratifies. NO 42 IDENTIFIED must remain reachable.
    """

    def synthesize(self, subject: LabeledItem, context: Any) -> GateRecord:
        ...


@runtime_checkable
class IndependenceCheck(Protocol):
    """Would demonstrate that the three lenses did not collapse into one.

    No implementation exists because no test has been specified. See THE OPEN
    PROBLEM above.
    """

    def verify(self, red: Any, gray: Any, green: Any) -> bool:
        ...


def unavailable(*_args: Any, **_kwargs: Any) -> None:
    raise NotYetSpecified(
        "The reasoning layer is not implemented. Red, Gray, Green, and 42 are "
        "performed by a human or a model outside this package, and their "
        "output is submitted to the harness for governance. See the module "
        "docstring for the four questions that must be answered first."
    )
