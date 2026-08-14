"""Provenance: Chain A, Chain B, human roots, and erasure.

Two different questions get asked about every claim, and conflating them is
how machine output becomes evidence.

Chain A asks who originated the material.
Chain B asks whether that material actually supports the conclusion drawn
from it.

A statement can be authentically human-originated and still be insufficient
support for a particular inference. Human origin is not an evidentiary
upgrade.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Optional
import uuid

from ._clock import utcnow
from .epistemic import Authorization, Label, LabeledItem
from .errors import EpistemicViolation, IncompleteSubmission


class Origin(str, Enum):
    """Chain A. Who originated this material."""

    USER_ESTABLISHED = "USER_ESTABLISHED"
    USER_ACCEPTED = "USER_ACCEPTED"
    ASSISTANT_PROPOSED = "ASSISTANT_PROPOSED"
    MACHINE_DERIVED = "MACHINE_DERIVED"
    EXTERNAL_SOURCE = "EXTERNAL_SOURCE"
    PROVENANCE_UNCERTAIN = "PROVENANCE_UNCERTAIN"


#: Origins that can terminate a support chain as a legitimate human root.
HUMAN_ROOTS = frozenset({Origin.USER_ESTABLISHED, Origin.USER_ACCEPTED})

#: Origins that cannot, on their own, root an evidentiary claim.
MACHINE_ORIGINS = frozenset({Origin.ASSISTANT_PROPOSED, Origin.MACHINE_DERIVED})


@dataclass(frozen=True)
class SupportLink:
    """Chain B. One claim offered as support for another.

    `reason` must state how the source bears on the target. "It is related"
    is not a support relationship.
    """

    source_id: str
    target_id: str
    reason: str
    link_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    created_at: str = field(default_factory=utcnow)

    def __post_init__(self) -> None:
        if self.source_id == self.target_id:
            raise IncompleteSubmission("A claim cannot support itself.")
        if not self.reason.strip():
            raise IncompleteSubmission(
                "A support link requires a stated reason. Adjacency is not "
                "support."
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "link_id": self.link_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "reason": self.reason,
            "created_at": self.created_at,
        }


@dataclass
class RootTrace:
    """The answer to: why does this claim exist, and what backs it."""

    item_id: str
    reaches_human_root: bool
    human_roots: list[str] = field(default_factory=list)
    machine_steps: int = 0
    paths: list[list[str]] = field(default_factory=list)
    erased_roots: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "reaches_human_root": self.reaches_human_root,
            "human_roots": list(self.human_roots),
            "machine_steps": self.machine_steps,
            "paths": [list(p) for p in self.paths],
            "erased_roots": list(self.erased_roots),
        }


@dataclass
class ErasureEvent:
    """A human removing material from their own record.

    The system has no veto. Its job is to record the erasure and disclose the
    consequences.
    """

    item_id: str
    erased_by: str
    reason: str
    downgrades: list[dict[str, str]] = field(default_factory=list)
    flagged: list[str] = field(default_factory=list)
    erased_at: str = field(default_factory=utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "erased_by": self.erased_by,
            "reason": self.reason,
            "downgrades": list(self.downgrades),
            "flagged": list(self.flagged),
            "erased_at": self.erased_at,
        }


class ProvenanceGraph:
    """Holds claims, their origins, and the support relationships between them.

    Enforces three rules:

    1. Machine-originated material cannot acquire human origin except by a
       recorded human authorization.
    2. A claim cannot hold FACT status unless its support chain terminates in
       human-originated material that actually supports it.
    3. When a human erases a root, everything resting on it downgrades. No
       claim keeps evidentiary status on erased ground.
    """

    def __init__(self) -> None:
        self._items: dict[str, LabeledItem] = {}
        self._origins: dict[str, Origin] = {}
        self._links: list[SupportLink] = []
        self._erased: dict[str, ErasureEvent] = {}
        self._root_erased: set[str] = set()

    # -- registration ----------------------------------------------------

    def register(self, item: LabeledItem, origin: Origin) -> LabeledItem:
        origin = Origin(origin)
        if item.item_id in self._items:
            raise IncompleteSubmission(f"Item {item.item_id} is already registered.")
        self._items[item.item_id] = item
        self._origins[item.item_id] = origin
        if item.label is Label.FACT:
            self._assert_fact_admissible(item.item_id)
        item.promotion_guard = self._guard
        return item

    def has(self, item_id: str) -> bool:
        return item_id in self._items

    def _guard(self, item: LabeledItem, new_label: Label) -> None:
        """Consulted on every relabel of a registered item.

        Without this, the human-root requirement could be sidestepped simply
        by calling relabel() instead of promote_to_fact().
        """
        if new_label is not Label.FACT:
            return
        origin = self._origins.get(item.item_id)
        if origin in HUMAN_ROOTS or origin is Origin.EXTERNAL_SOURCE:
            return
        if not self.trace(item.item_id).reaches_human_root:
            raise EpistemicViolation(
                f"{origin.value if origin else 'Unregistered'} material cannot "
                "be relabelled to FACT without a support chain terminating in "
                "human-originated material. Machine reasoning does not "
                "bootstrap itself into evidence by any route."
            )

    def origin_of(self, item_id: str) -> Origin:
        self._require(item_id)
        return self._origins[item_id]

    def item(self, item_id: str) -> LabeledItem:
        self._require(item_id)
        return self._items[item_id]

    @property
    def items(self) -> list[LabeledItem]:
        return [i for k, i in self._items.items() if k not in self._erased]

    def _require(self, item_id: str) -> None:
        if item_id not in self._items:
            raise IncompleteSubmission(f"No registered item {item_id}.")

    # -- Chain A ---------------------------------------------------------

    def reassign_origin(
        self, item_id: str, new_origin: Origin, authorization: Optional[Authorization]
    ) -> Origin:
        """Change who a claim is attributed to. Guarded, not free."""
        self._require(item_id)
        new_origin = Origin(new_origin)
        current = self._origins[item_id]
        if new_origin in HUMAN_ROOTS and current in MACHINE_ORIGINS:
            if not isinstance(authorization, Authorization):
                raise EpistemicViolation(
                    f"{current.value} material cannot become {new_origin.value} "
                    "without a recorded human authorization. Machine output "
                    "does not acquire human origin by being useful."
                )
        self._origins[item_id] = new_origin
        return new_origin

    # -- Chain B ---------------------------------------------------------

    def add_support(self, source_id: str, target_id: str, reason: str) -> SupportLink:
        self._require(source_id)
        self._require(target_id)
        if source_id in self._erased:
            raise IncompleteSubmission(
                f"Item {source_id} has been erased and cannot support anything."
            )
        link = SupportLink(source_id=source_id, target_id=target_id, reason=reason)
        if self._would_cycle(link):
            raise IncompleteSubmission(
                "That support link creates a cycle. A claim cannot support "
                "itself through intermediaries."
            )
        self._links.append(link)
        return link

    def _would_cycle(self, link: SupportLink) -> bool:
        seen = set()
        stack = [link.source_id]
        while stack:
            node = stack.pop()
            if node == link.target_id:
                return True
            if node in seen:
                continue
            seen.add(node)
            stack.extend(l.source_id for l in self._links if l.target_id == node)
        return False

    def supporters(self, item_id: str) -> list[str]:
        return [
            l.source_id
            for l in self._links
            if l.target_id == item_id and l.source_id not in self._erased
        ]

    def dependents(self, item_id: str) -> list[str]:
        return [l.target_id for l in self._links if l.source_id == item_id]

    # -- human root ------------------------------------------------------

    def trace(self, item_id: str) -> RootTrace:
        """Walk the support chain back and report what it terminates in."""
        self._require(item_id)
        paths: list[list[str]] = []
        roots: list[str] = []
        erased_roots: list[str] = []
        max_machine = 0

        def walk(node: str, path: list[str], machine_steps: int) -> None:
            nonlocal max_machine
            origin = self._origins[node]
            sources = [l.source_id for l in self._links if l.target_id == node]
            live = [s for s in sources if s not in self._erased]
            dead = [s for s in sources if s in self._erased]
            erased_roots.extend(dead)

            if origin in HUMAN_ROOTS:
                roots.append(node)
                paths.append(path + [node])
                max_machine = max(max_machine, machine_steps)
                return
            if not live:
                paths.append(path + [node])
                max_machine = max(max_machine, machine_steps + 1)
                return
            for s in live:
                if s in path:
                    continue
                walk(s, path + [node], machine_steps + 1)

        walk(item_id, [], 0)
        return RootTrace(
            item_id=item_id,
            reaches_human_root=bool(roots),
            human_roots=sorted(set(roots)),
            machine_steps=max_machine,
            paths=paths,
            erased_roots=sorted(set(erased_roots)),
        )

    def _assert_fact_admissible(self, item_id: str) -> None:
        origin = self._origins[item_id]
        if origin in HUMAN_ROOTS or origin is Origin.EXTERNAL_SOURCE:
            return
        trace = self.trace(item_id)
        if not trace.reaches_human_root:
            raise EpistemicViolation(
                f"{origin.value} material cannot hold FACT status without a "
                "support chain terminating in human-originated material. "
                "Machine reasoning does not bootstrap itself into evidence, "
                "however many steps it takes."
            )

    def promote_to_fact(self, item_id: str, authorization: Authorization) -> Label:
        """Raise a claim to FACT. Requires both a human root and authorization."""
        self._require(item_id)
        item = self._items[item_id]
        trace = self.trace(item_id)
        origin = self._origins[item_id]
        if origin not in HUMAN_ROOTS and origin is not Origin.EXTERNAL_SOURCE:
            if not trace.reaches_human_root:
                raise EpistemicViolation(
                    "Promotion to FACT requires a support chain terminating in "
                    "human-originated material that supports the claim."
                )
        item.relabel(Label.FACT, authorization)
        return item.label

    # -- erasure ---------------------------------------------------------

    def erase(self, item_id: str, erased_by: str, reason: str) -> ErasureEvent:
        """Remove human material at the human's instruction, then cascade.

        The downgrade that follows is not the system overruling Amendment 1.
        The human's erasure is the authorizing act, and the cascade only ever
        moves status downward. Nothing is ever raised automatically.
        """
        self._require(item_id)
        if not erased_by.strip() or not reason.strip():
            raise IncompleteSubmission("An erasure requires an actor and a reason.")

        event = ErasureEvent(item_id=item_id, erased_by=erased_by, reason=reason)
        self._erased[item_id] = event

        for dependent_id in self._reachable_dependents(item_id):
            dep = self._items[dependent_id]
            if dependent_id in self._erased:
                continue
            self._root_erased.add(dependent_id)
            if dep.label is Label.DECISION:
                # A human decision stays a human decision. Erasing what informed
                # it does not unmake it. It is flagged, not downgraded.
                event.flagged.append(dependent_id)
                continue
            if dep.label is not Label.FACT:
                continue
            trace = self.trace(dependent_id)
            origin = self._origins[dependent_id]
            if origin in HUMAN_ROOTS or origin is Origin.EXTERNAL_SOURCE:
                continue
            if trace.reaches_human_root:
                continue
            new_label = Label.INFERENCE if self.supporters(dependent_id) else Label.UNKNOWN
            dep.label_history.append(
                {
                    "from": dep.label.value,
                    "to": new_label.value,
                    "authorization": {
                        "authorized_by": erased_by,
                        "reason": f"Automatic downgrade: root {item_id} erased.",
                    },
                }
            )
            dep.label = new_label  # direct: the guard only blocks upward moves
            event.downgrades.append(
                {"item_id": dependent_id, "from": "FACT", "to": new_label.value}
            )
        return event

    def _reachable_dependents(self, item_id: str) -> list[str]:
        seen: set[str] = set()
        stack = list(self.dependents(item_id))
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            stack.extend(self.dependents(node))
        return sorted(seen)

    def is_erased(self, item_id: str) -> bool:
        return item_id in self._erased

    def zombie_check(self) -> list[str]:
        """Any FACT still standing on ground that no longer reaches a human root."""
        bad = []
        for item_id, item in self._items.items():
            if item_id in self._erased or item.label is not Label.FACT:
                continue
            origin = self._origins[item_id]
            if origin in HUMAN_ROOTS or origin is Origin.EXTERNAL_SOURCE:
                continue
            if not self.trace(item_id).reaches_human_root:
                bad.append(item_id)
        return bad

    def to_dict(self) -> dict[str, Any]:
        return {
            "items": [
                {
                    **self._items[i].to_dict(),
                    "origin": self._origins[i].value,
                    "erased": i in self._erased,
                    "root_erased": i in self._root_erased,
                }
                for i in sorted(self._items)
            ],
            "support_links": [l.to_dict() for l in self._links],
            "erasures": [e.to_dict() for e in self._erased.values()],
        }
