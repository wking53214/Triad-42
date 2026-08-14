"""Triad+42: an advisory cognitive review harness.

This package structures and enforces a Triad+42 pass. It does not perform the
reasoning. Red, Gray, Green, and 42 are done by a human or a model. The
package enforces form: that stages ran in order, that verdicts rest on
findings that can carry them, that epistemic labels survive, and that mandate
clusters were examined rather than skipped.

The mechanism is advisory. It cannot create authority, authorize execution,
establish canonical status, promote drafts, or convert recommendations into
decisions.
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
from .epistemic import Authorization, Label, LabeledItem
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
    DistinctionKind,
    Disposition,
    Grounding,
    GroundingLedger,
    GroundingStatus,
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
from .provenance import (
    HUMAN_ROOTS,
    MACHINE_ORIGINS,
    ErasureEvent,
    Origin,
    ProvenanceGraph,
    RootTrace,
    SupportLink,
)
from .retrieval import CandidateKind, CandidateRecord, CandidateStore, SurfacingStatus
from .review import ReviewPass, Session, Stage, Verdict

__version__ = "2.1.0"

__all__ = [
    "Candidate",
    "CandidateKind",
    "CandidateStore",
    "DeepThoughtEngine",
    "ErasureEvent",
    "GrayLens",
    "GreenLens",
    "HUMAN_ROOTS",
    "IndependenceCheck",
    "MACHINE_ORIGINS",
    "NotYetSpecified",
    "Origin",
    "ProvenanceGraph",
    "RedLens",
    "RootTrace",
    "SupportLink",
    "SurfacingStatus",
    "normalize_key",
    "ANOMALY",
    "MANDATE",
    "PATTERN",
    "Authorization",
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
    "no_candidate",
    "run_gate",
]
