"""Amendment 2: Red severity classification and cluster escalation.

Severity is supplied by the reviewer. The harness never infers it, never
computes it, and never overrides it. What the harness does is refuse to let a
verdict rest on findings that cannot carry it, and refuse to let a mandate
cluster go unexamined.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
import uuid

from .errors import EscalationError, IncompleteSubmission, UnexaminedMandate


class Severity(str, Enum):
    """The four severity tiers. Only CRITICAL and HIGH can support FAILS."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


#: Ascending order. Escalation moves exactly one step along this ladder.
TIER_ORDER: tuple[Severity, ...] = (
    Severity.LOW,
    Severity.MEDIUM,
    Severity.HIGH,
    Severity.CRITICAL,
)

#: Severities that may support a FAILS verdict.
BLOCKING = frozenset({Severity.CRITICAL, Severity.HIGH})

#: The 1 / 2 / 3 thresholds.
ANOMALY = 1
PATTERN = 2
MANDATE = 3


def next_tier(severity: Severity) -> Optional[Severity]:
    """The tier one step up, or None if already at the top."""
    idx = TIER_ORDER.index(severity)
    if idx + 1 >= len(TIER_ORDER):
        return None
    return TIER_ORDER[idx + 1]


class ClusterState(str, Enum):
    """What a group of same-scope, same-tier findings means.

    TERMINOLOGY, EXPLICITLY SCOPED
    ------------------------------
    "Mandate" here means a mandatory examination. It is a duty placed on the
    reviewer, not a conclusion granted authority.

    The word is also used elsewhere for an established requirement that only a
    human may authorize. These are different things and the harness never
    conflates them: reaching three findings compels someone to look, and
    nothing more. No cluster, at any count, can produce an authorized
    conclusion. That transition stays a human act.
    """

    ANOMALY = "ANOMALY"  # 1. Record only.
    PATTERN = "PATTERN"  # 2. Examination permitted, escalation optional.
    MANDATE = "MANDATE"  # 3+. Examination required, escalation presumed.


class ExaminationOutcome(str, Enum):
    """The three legitimate results of a cluster examination."""

    SHARED_CAUSE_NAMED = "SHARED_CAUSE_NAMED"
    INDEPENDENT_ORIGINS_DEMONSTRATED = "INDEPENDENT_ORIGINS_DEMONSTRATED"
    REQUIRES_HUMAN_DECISION = "REQUIRES_HUMAN_DECISION"


@dataclass
class Finding:
    """A single Red finding.

    `scope` is what makes clustering possible: findings cluster only when they
    attach to the same component, boundary, or authority relationship.
    `derived_from` is populated when the finding was produced by escalation
    rather than observed directly.
    """

    text: str
    severity: Severity
    scope: str
    finding_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    derived_from: list[str] = field(default_factory=list)
    escalation_cause: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise IncompleteSubmission("A finding requires text.")
        if not self.scope.strip():
            raise IncompleteSubmission(
                "A finding requires a scope. Without one, clustering cannot "
                "distinguish related findings from coincidence."
            )
        if not isinstance(self.severity, Severity):
            self.severity = Severity(self.severity)

    @property
    def is_derived(self) -> bool:
        return bool(self.derived_from)

    @property
    def is_blocking(self) -> bool:
        return self.severity in BLOCKING

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "text": self.text,
            "severity": self.severity.value,
            "scope": self.scope,
            "derived_from": list(self.derived_from),
            "escalation_cause": self.escalation_cause,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Finding":
        return cls(
            text=data["text"],
            severity=Severity(data["severity"]),
            scope=data["scope"],
            finding_id=data["finding_id"],
            derived_from=list(data.get("derived_from", [])),
            escalation_cause=data.get("escalation_cause"),
        )


@dataclass(frozen=True)
class Cluster:
    """A group of findings sharing scope and severity tier."""

    scope: str
    severity: Severity
    finding_ids: tuple[str, ...]

    @property
    def key(self) -> tuple[str, str]:
        return (self.scope, self.severity.value)

    @property
    def count(self) -> int:
        return len(self.finding_ids)

    @property
    def state(self) -> ClusterState:
        if self.count >= MANDATE:
            return ClusterState.MANDATE
        if self.count == PATTERN:
            return ClusterState.PATTERN
        return ClusterState.ANOMALY

    @property
    def examination_required(self) -> bool:
        return self.state is ClusterState.MANDATE

    @property
    def examination_permitted(self) -> bool:
        return self.state in (ClusterState.PATTERN, ClusterState.MANDATE)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "severity": self.severity.value,
            "finding_ids": list(self.finding_ids),
            "count": self.count,
            "state": self.state.value,
        }


@dataclass
class Examination:
    """The record of one cluster examination.

    At the mandate threshold the burden is inverted: escalation is presumed,
    and declining to escalate requires a distinct named origin for every
    finding in the cluster. A bare assertion that the findings are unrelated
    is rejected.
    """

    scope: str
    severity: Severity
    finding_ids: tuple[str, ...]
    outcome: ExaminationOutcome
    shared_cause: Optional[str] = None
    independent_origins: dict[str, str] = field(default_factory=dict)
    reasoning: Optional[str] = None
    produced_finding_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "severity": self.severity.value,
            "finding_ids": list(self.finding_ids),
            "outcome": self.outcome.value,
            "shared_cause": self.shared_cause,
            "independent_origins": dict(self.independent_origins),
            "reasoning": self.reasoning,
            "produced_finding_id": self.produced_finding_id,
        }


class FindingLedger:
    """Holds Red's findings and enforces the escalation rules over them.

    Derived findings re-enter the pool, so a cluster examination can produce a
    finding that itself clusters. Recomputation runs until the picture is
    stable.
    """

    #: Guard against a pathological escalation loop.
    MAX_ROUNDS = 32

    def __init__(self) -> None:
        self._findings: dict[str, Finding] = {}
        self._examinations: list[Examination] = []
        self._examined_keys: set[tuple[str, str, tuple[str, ...]]] = set()

    # -- submission -----------------------------------------------------

    def add(self, finding: Finding) -> Finding:
        self._findings[finding.finding_id] = finding
        return finding

    @property
    def findings(self) -> list[Finding]:
        return list(self._findings.values())

    @property
    def examinations(self) -> list[Examination]:
        return list(self._examinations)

    def get(self, finding_id: str) -> Finding:
        if finding_id not in self._findings:
            raise EscalationError(f"No finding with id {finding_id}.")
        return self._findings[finding_id]

    # -- clustering -----------------------------------------------------

    def clusters(self) -> list[Cluster]:
        grouped: dict[tuple[str, Severity], list[str]] = {}
        for f in self._findings.values():
            grouped.setdefault((f.scope, f.severity), []).append(f.finding_id)
        return [
            Cluster(scope=scope, severity=sev, finding_ids=tuple(sorted(ids)))
            for (scope, sev), ids in grouped.items()
        ]

    def open_mandates(self) -> list[Cluster]:
        """Mandate clusters that have not yet been examined."""
        out = []
        for c in self.clusters():
            if not c.examination_required:
                continue
            if (c.scope, c.severity.value, c.finding_ids) in self._examined_keys:
                continue
            out.append(c)
        return out

    # -- examination ----------------------------------------------------

    def examine(
        self,
        scope: str,
        severity: Severity,
        outcome: ExaminationOutcome,
        shared_cause: Optional[str] = None,
        independent_origins: Optional[dict[str, str]] = None,
        reasoning: Optional[str] = None,
    ) -> Examination:
        """Record an examination of the cluster at (scope, severity)."""
        severity = Severity(severity)
        outcome = ExaminationOutcome(outcome)
        cluster = self._require_cluster(scope, severity)

        if not cluster.examination_permitted:
            raise EscalationError(
                f"Cluster {scope}/{severity.value} holds {cluster.count} "
                "finding(s). A single finding is an anomaly and is recorded "
                "only. Examination begins at two."
            )

        if outcome is ExaminationOutcome.SHARED_CAUSE_NAMED:
            exam = self._shared_cause(cluster, shared_cause)
        elif outcome is ExaminationOutcome.INDEPENDENT_ORIGINS_DEMONSTRATED:
            exam = self._independent_origins(cluster, independent_origins)
        else:
            exam = self._human_decision(cluster, reasoning)

        self._examinations.append(exam)
        self._examined_keys.add(
            (cluster.scope, cluster.severity.value, cluster.finding_ids)
        )
        return exam

    def _require_cluster(self, scope: str, severity: Severity) -> Cluster:
        for c in self.clusters():
            if c.scope == scope and c.severity is severity:
                return c
        raise EscalationError(f"No cluster at scope {scope!r} tier {severity.value}.")

    def _shared_cause(self, cluster: Cluster, cause: Optional[str]) -> Examination:
        if not (cause or "").strip():
            raise IncompleteSubmission(
                "Escalation requires the shared cause to be named. Count alone "
                "cannot produce a higher-severity finding."
            )
        target = next_tier(cluster.severity)
        if target is None:
            # Nothing sits above CRITICAL. The examination is still recorded so
            # the mandate is closed, but no new finding is produced.
            return Examination(
                scope=cluster.scope,
                severity=cluster.severity,
                finding_ids=cluster.finding_ids,
                outcome=ExaminationOutcome.SHARED_CAUSE_NAMED,
                shared_cause=cause,
                produced_finding_id=None,
            )
        derived = Finding(
            text=f"[escalated from {cluster.severity.value}] {cause}",
            severity=target,
            scope=cluster.scope,
            derived_from=list(cluster.finding_ids),
            escalation_cause=cause,
        )
        self.add(derived)
        return Examination(
            scope=cluster.scope,
            severity=cluster.severity,
            finding_ids=cluster.finding_ids,
            outcome=ExaminationOutcome.SHARED_CAUSE_NAMED,
            shared_cause=cause,
            produced_finding_id=derived.finding_id,
        )

    def _independent_origins(
        self, cluster: Cluster, origins: Optional[dict[str, str]]
    ) -> Examination:
        origins = origins or {}
        missing = [fid for fid in cluster.finding_ids if not origins.get(fid, "").strip()]
        if missing:
            raise IncompleteSubmission(
                "Declining to escalate requires a distinct named origin for "
                f"every finding in the cluster. Missing for: {missing}. "
                "An assertion that the findings are unrelated is not enough."
            )
        extra = set(origins) - set(cluster.finding_ids)
        if extra:
            raise IncompleteSubmission(
                f"Origins supplied for findings outside this cluster: {sorted(extra)}."
            )
        distinct = {v.strip().casefold() for v in origins.values()}
        if len(distinct) < len(origins):
            raise IncompleteSubmission(
                "The origin accounts are not distinct. Repeating one account "
                "across findings describes a shared cause, which is an "
                "escalation, not an exemption from one."
            )
        return Examination(
            scope=cluster.scope,
            severity=cluster.severity,
            finding_ids=cluster.finding_ids,
            outcome=ExaminationOutcome.INDEPENDENT_ORIGINS_DEMONSTRATED,
            independent_origins=dict(origins),
        )

    def _human_decision(
        self, cluster: Cluster, reasoning: Optional[str]
    ) -> Examination:
        if not (reasoning or "").strip():
            raise IncompleteSubmission(
                "Routing a cluster to human decision requires stating what the "
                "accumulation suggests and why no single finding carries it."
            )
        return Examination(
            scope=cluster.scope,
            severity=cluster.severity,
            finding_ids=cluster.finding_ids,
            outcome=ExaminationOutcome.REQUIRES_HUMAN_DECISION,
            reasoning=reasoning,
        )

    # -- closure --------------------------------------------------------

    def assert_mandates_closed(self) -> None:
        """Refuse to finalize while any mandate cluster is unexamined."""
        open_now = self.open_mandates()
        if not open_now:
            return
        described = ", ".join(
            f"{c.scope}/{c.severity.value} ({c.count} findings)" for c in open_now
        )
        raise UnexaminedMandate(
            "Examination is required at three findings in the same scope. "
            f"Unexamined: {described}."
        )

    def routed_to_human(self) -> bool:
        return any(
            e.outcome is ExaminationOutcome.REQUIRES_HUMAN_DECISION
            for e in self._examinations
        )

    def blocking_findings(self) -> list[Finding]:
        return [f for f in self._findings.values() if f.is_blocking]

    def to_dict(self) -> dict[str, Any]:
        return {
            "findings": [f.to_dict() for f in self._findings.values()],
            "clusters": [c.to_dict() for c in self.clusters()],
            "examinations": [e.to_dict() for e in self._examinations],
        }
