"""Triad+42: an advisory cognitive review harness.

This package structures and enforces a Triad+42 pass. It does not perform the
reasoning. Red, Gray, Green, and 42 are done by a human or a model. The
package enforces form: that stages ran in order, that verdicts rest on
findings that can carry them, that epistemic labels survive, and that mandate
clusters were examined rather than skipped.

The mechanism is advisory. It cannot create authority, authorize execution,
establish canonical status, promote drafts, or convert recommendations into
decisions. It holds no origin rules and no durable memory: CCC (the Cognitive
Continuity Constitution) is the single owner of both. Output that must persist
is handed to CCC through `triad42.ccc_handoff`, always as machine-originated.
"""

from .deepthought import (
    Candidate,
    Check,
    CheckAnswer,
    DeepThoughtResult,
    GateRecord,
    no_candidate,
    run_gate,
)
from .epistemic import Label, LabeledItem
from .errors import (
    EpistemicViolation,
    EscalationError,
    GroundingError,
    InadmissibleVerdict,
    IncompleteSubmission,
    StageOrderError,
    Triad42Error,
    UnexaminedMandate,
)
from .findings import (
    ANOMALY,
    MANDATE,
    PATTERN,
    Cluster,
    ClusterState,
    Examination,
    ExaminationOutcome,
    Finding,
    FindingLedger,
    Severity,
)
from .lenses import (
    CrossCuttingObservation,
    DistinctionKind,
    Disposition,
    Grounding,
    GroundingLedger,
    GroundingStatus,
    StructuralAssessment,
    StructuralObservation,
    normalize_key,
)
from .engines import (
    DeepThoughtEngine,
    GrayLens,
    GreenLens,
    IndependenceCheck,
    NotYetSpecified,
    RedLens,
)
from .retrieval import CandidateKind, CandidateRecord, CandidateStore, SurfacingStatus
from .review import ReviewPass, Session, Stage, Verdict
from .integrity import (
    IntegrityManifest,
    canonical_bytes,
    content_digest,
    manifest_for,
)
from .observations import LinguisticObservation, SIGNALS, observe_language
from .telemetry import PassTelemetry, collect_pass_telemetry

__version__ = "3.0.0"

__all__ = [
    "Candidate",
    "CandidateKind",
    "CandidateStore",
    "DeepThoughtEngine",
    "GrayLens",
    "GreenLens",
    "IndependenceCheck",
    "NotYetSpecified",
    "RedLens",
    "SurfacingStatus",
    "CrossCuttingObservation",
    "StructuralAssessment",
    "normalize_key",
    "ANOMALY",
    "MANDATE",
    "PATTERN",
    "Candidate",
    "Check",
    "CheckAnswer",
    "Cluster",
    "ClusterState",
    "DeepThoughtResult",
    "Disposition",
    "DistinctionKind",
    "EpistemicViolation",
    "EscalationError",
    "Examination",
    "ExaminationOutcome",
    "Finding",
    "FindingLedger",
    "GateRecord",
    "Grounding",
    "GroundingError",
    "GroundingLedger",
    "GroundingStatus",
    "InadmissibleVerdict",
    "IncompleteSubmission",
    "Label",
    "LabeledItem",
    "ReviewPass",
    "Session",
    "Severity",
    "Stage",
    "StageOrderError",
    "StructuralObservation",
    "Triad42Error",
    "UnexaminedMandate",
    "Verdict",
    "IntegrityManifest",
    "LinguisticObservation",
    "PassTelemetry",
    "SIGNALS",
    "canonical_bytes",
    "collect_pass_telemetry",
    "content_digest",
    "no_candidate",
    "manifest_for",
    "observe_language",
    "run_gate",
]
