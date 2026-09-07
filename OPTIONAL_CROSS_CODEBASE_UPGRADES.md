# Optional Cross-Codebase Upgrade Investigation

**Target:** `/home/wking53214/Triad-42` (Triad-42 2.2.0 plus commit
`af96bf9`)

**Scope:** Repository-first comparison against the FACTS, STRIDE, and
FORTRESS/GSA concepts in the investigation prompt. The local FACTS and STRIDE
repositories were not present under the workspace names searched; their
described capabilities were assessed conceptually. Local
`/home/wking53214/FORTRESS` and `/home/wking53214/GSA-815` implementations were
sampled as supplied-family evidence. No production code or tests were modified.

## 1. Executive verdict

**NO MATERIAL BENEFIT.**

Triad-42 is an advisory cognitive review harness, not an autonomous execution,
control, or statistical-analysis runtime. Its strongest boundaries are already
implemented: ordered Red/Gray/Green/42 stages, sealed ledgers, write-once
verdicts, human authorization, human-root provenance, support-chain checks,
erasure cascade, candidate retention, Gray cross-cutting observations, Green
reaffirmation tracking, and explicit negative outcomes.

The recently added digest, telemetry, and linguistic-observation APIs are
already the maximum defensible interpretation of the donor ideas for this
repository. Stronger versions—HMAC audit authority, regime engines,
confidence/fragility scoring, autonomous invariants, bounded action execution,
deep immutable envelopes, or cryptographic state interlocks—would introduce a
different system and weaken Triad-42's constitutional boundary.

## 2. Repository architecture summary

`triad42/` is a dependency-free Python package with records and ledgers rather
than an execution service. `ReviewPass` enforces
`RED -> GRAY -> GREEN -> 42`, closes and seals stage ledgers, validates declared
verdicts, and exports JSON. `Session` owns pass history, provenance, analogy
history, and the append-only candidate store.

`epistemic.py` carries FACT, INFERENCE, ASSUMPTION, DECISION, RECOMMENDATION,
and UNKNOWN labels with authorization history. `provenance.py` separates origin
from support, requires a human-root path for machine-derived FACT promotion,
prevents support cycles, and cascades human erasure. `findings.py` keeps
reviewer-supplied severity, same-scope clustering, examination, and one-tier
escalation. `lenses.py` records Gray structure and Green grounding without
giving Gray severity or Green truth authority. `deepthought.py` records the
five-check 42 gate, including `NO_42_IDENTIFIED`. `engines.py` contains
protocols only; no automated reasoning lens is implemented.

The current package also has:

- `integrity.py`: deterministic canonical JSON bytes, SHA-256 content digest,
  and optional previous-digest metadata.
- `telemetry.py`: read-only pass counters; no duration, score, or decision
  path.
- `observations.py`: exact-text-preserving surface language signals; no claim
  rewrite or epistemic interpretation.

State is in-memory. Export is one-way (`to_dict()`/`to_json()`), with no reload,
database, worker queue, retry loop, async boundary, branch/merge model, HMAC
audit log, or cryptographic signature key lifecycle. UUIDs and UTC timestamps
are intentionally nondeterministic record metadata; JSON key ordering and
integrity canonicalization are deterministic.

## 3. FACTS findings

| Capability | Existing equivalent | Gap | Value | Recommendation |
|---|---|---|---|---|
| deterministic input normalization | `normalize_key()` normalizes analogy identity only | Claim text must remain exact | Low | E / REJECT |
| strict regex structural filtering | no structural text filter; explicit record validation exists | Filtering would be semantic authority | None | G / REJECT |
| first-person/reference normalization | `observe_language()` reports first-person framing without rewrite | No safe normalization gap | Low | A / ALREADY PRESENT |
| qualitative-token filtering | no token removal | Removal can erase context and provenance | None | G / REJECT |
| whitespace canonicalization | JSON digest canonicalizes serialized structure | No need to canonicalize reviewed text | Low | A / ALREADY PRESENT at export boundary |
| deterministic transformation pipeline | no transformation pipeline; original claims are preserved | Transformation is outside harness role | None | F / CONFLICTING |
| SHA-256 transformed-payload hash | `integrity.manifest_for()` hashes canonical export | No missing core mechanism | Low | A / ALREADY PRESENT |
| structured integrity manifest | `IntegrityManifest` includes algorithm, canonicalization, digest, prior digest | Durable manifest storage is caller-owned | Low | A / ALREADY PRESENT |
| explicit transformation stages | Red/Gray/Green/42 are explicit governance stages | Donor transform stages are not review stages | None | A / ALREADY PRESENT, do not merge |
| separation normalize/transform/attest | integrity is isolated from review; no transform | No additional boundary needed | Low | A / ALREADY PRESENT |
| deterministic output generation | sorted JSON export and stable digest bytes | UUID/time fields remain intentionally variable | Low | E / NO VALUE |
| transformation-before-hashing | digest is over final export mapping | No transformed semantic payload exists | None | E / UNNECESSARY |
| audit-oriented metadata | timestamps, reasons, provenance, surfacing, telemetry | No durable audit service | Low | A / ALREADY PRESENT for package scope |
| stable machine-readable manifest | `to_dict()` plus `IntegrityManifest.to_dict()` | No external manifest registry | Low | A / ALREADY PRESENT |

FACTS' subjective language rules are not suitable as Triad-42 filters:
assertion, hedging, first-person wording, and qualitative terms cannot establish
truth, origin, severity, or support.

## 4. STRIDE findings

| Capability | Existing equivalent | Gap | Value | Recommendation |
|---|---|---|---|---|
| centralized compiled validation patterns | dataclass `__post_init__` checks and domain exceptions | No universal validator need | Low | E / NO VALUE |
| input normalization | analogy-key normalization only | Text mutation would be unsafe | None | G / REJECT |
| validator/orchestrator separation | records/ledgers are separated from `ReviewPass` orchestration | Already native | Low | A / ALREADY PRESENT |
| traffic/governor / budgets | no traffic runtime | No autonomous work to bound | None | E / NOT APPLICABLE |
| queue limits / retries / loop detection | no queue or retry execution | No execution path to protect | None | E / NOT APPLICABLE |
| lifecycle states | `Stage`, closure, sealing, write-once verdict | Stronger equivalent exists | High | A / ALREADY PRESENT |
| historical output tracking | Session outputs and Green analogy history; append-only candidates | Text identity is deliberately not conflated | High | A / ALREADY PRESENT |
| ACCEPTED/RETRY/BLOCKED/ERROR states | domain exceptions and explicit verdicts | Runtime action statuses do not fit | None | F / CONFLICTING |
| anomaly/variance/fragility engines | Red clusters and Gray cross-cutting observations | No safe automatic scoring gap | None | G / REJECT |
| consolidated confidence score | no score by design | A score would acquire authority | Harmful | G / REJECT |
| immutable/frozen result structures | frozen `Authorization`, `SupportLink`; sealed ledgers and read-only views | Some records remain intentionally mutable | Low | E / NO VALUE |
| explicit telemetry structures | `PassTelemetry` | No external metrics transport | Low | A / ALREADY PRESENT |
| policy/execution/intelligence reports | structured `ReviewPass`/`Session` exports | Existing envelope is domain-native | Low | A / ALREADY PRESENT |
| async job wrappers/workers | none | No jobs or workers | None | E / NOT APPLICABLE |
| controlled computation/orchestration | `ReviewPass` controls accepted record transitions | No computation engine to govern | Low | A / ALREADY PRESENT |

The STRIDE execution patterns are valuable for a system that autonomously
processes requests. Triad-42 deliberately stops before that boundary.

## 5. FORTRESS/GSA findings

| Capability | Existing equivalent | Gap | Value | Recommendation |
|---|---|---|---|---|
| global random seeding | no randomness in Triad-42 core | No stochastic execution to reproduce | None | E / NO VALUE |
| reproducible execution IDs | UUID pass/item IDs and timestamps are intentionally variable | Deterministic IDs would change record semantics | Low | F / CONFLICTING |
| safe statistical primitives | no statistical engine | No metrics requiring statistics | None | E / NO VALUE |
| HMAC append-only audit log | append-only candidate store and one-way export; no authenticated log | Only relevant with a trusted persistence operator/key lifecycle | Low | E / SEPARATE SYSTEM |
| event/data separation | records distinguish fields and reasons | No event stream | Low | E / NO VALUE |
| rolling error history / volatility | none | No operational signal stream | None | E / NOT APPLICABLE |
| contradiction/distortion scoring | human-authored reasoning and explicit assessments | Automated scoring would judge content | Harmful | G / REJECT |
| STABLE/UNSTABLE/CRITICAL regimes | explicit verdicts and Gray assessment | Regime would imply automatic gating | Harmful | G / REJECT |
| centralized invariant monitor | checks are located at object boundaries and stage closure | No scattered runtime invariant family | Low | A / ALREADY PRESENT |
| drift monitor | Green analogy recurrence and session history | No model/configuration stream | None | E / NO VALUE |
| bounded action MandateLayer | Triad-42 authorizes no downstream action | No action delta to constrain | None | E / NOT APPLICABLE |
| deep recursive freezing | tuples/read-only views/sealed ledgers at key boundaries | Mutable records are intentional before closure | Low | E / NO VALUE |
| cryptographic state signature | content digest covers exported representation; no state-transition graph | No branch/fork/replay state model | Low | E / SEPARATE SYSTEM |
| parent hashes / anchors / forks / merges | provenance IDs and support links, but no branch graph | Provenance is semantic support, not execution lineage | None | C / WRONG LAYER |
| immutable outbound envelopes | one-way JSON and structured records | No inter-module async envelope | None | E / NOT APPLICABLE |
| actor identity / chain-break checks | authorization identity, origins, support-cycle prevention | No execution chain to authenticate | Low | A / ALREADY PRESENT for governance |

The local FORTRESS/GSA code demonstrates useful patterns for autonomous,
numeric, asynchronous pipelines, but its own implementations include mutable
envelopes, default development keys, silent I/O failure paths, and
domain-specific thresholds. Those are not safe drop-in foundations for
Triad-42.

## 6. Cross-architecture opportunities

The proposed chains do not fit as one Triad-42 pipeline:

`NORMALIZE -> TRANSFORM -> HASH -> MANIFEST` would make content processing
precede review and risks replacing the original claim. Triad-42 safely supports
only export-boundary canonicalization and hashing.

`VALIDATE -> GOVERN -> EXECUTE -> OBSERVE -> CLASSIFY` assumes an execution and
classification authority. Triad-42 governs record admissibility, not actions or
truth.

`PRESERVE -> SIGN -> BOUND -> MONITOR -> ATTEST -> CONTINUE` assumes signed
state transitions and controlled continuation. Triad-42 has preservation and
procedural checks, but no trusted executor or state machine.

The safe composite is already present:

`PRESERVE -> STRUCTURE -> CHECK BOUNDARIES -> EXPORT/OBSERVE`

Adding `EXECUTE`, automatic `CLASSIFY`, or cryptographic interlocks would make
the package a different system.

## 7. Enforcement-boundary analysis

| Boundary | Enters | Invariant | Trust before/after | Bypass prevention | Failure |
|---|---|---|---|---|---|
| stage ledger | reviewer record | legal stage order and closure | caller supplies content; ledger accepts only current stage | `_require`, sealed Red/Green ledgers, Gray tuple | domain exception |
| provenance registration/relabel | labelled item + origin | human-root requirement for FACT | caller asserts origin; graph guards registered promotion | `promotion_guard`, support-cycle check | `EpistemicViolation` |
| support graph | source/target/reason | explicit acyclic support | caller asserts support; graph records relationship | registration and cycle checks | `IncompleteSubmission` |
| Red examination | findings in one scope/tier | 1/2/3 examination and one-tier escalation | reviewer supplies severity/cause; ledger enforces form | open-mandate check and sealing | escalation/unexamined errors |
| verdict | closed pass + declaration | declared result is carried by record | reviewer decides; harness checks admissibility | write-once verdict and disagreement rule | `InadmissibleVerdict` |
| candidate retrieval | produced record + surfacing decision | non-surfaced material remains queryable | caller chooses presentation; append-only store retains | no delete operation | incomplete candidate rejected |
| integrity export | mapping | canonical bytes match digest | caller supplies export and stores manifest | `verify()` detects content changes | boolean mismatch |
| linguistic observation | original text | metadata cannot replace source | detector is untrusted; reviewer interprets | no connection to decision APIs | invalid empty input |
| telemetry | completed/current pass | counters describe only recorded process | observer is untrusted; governance ignores it | read-only dataclass/function | absent optional data is explicit |

The first seven are actual enforcement boundaries. The final three are
observability/boundary conveniences and intentionally do not enforce
epistemic conclusions.

## 8. Duplication and conflict analysis

Already stronger or equivalent: lifecycle control, stage separation, explicit
negative outcomes, human authorization, human-root provenance, support-chain
recording, erasure cascade, recurrence of Green analogies, candidate retention,
write-once behavior, and structured result envelopes.

Present but intentionally partial: mutable records before stage closure,
non-deterministic UUID/timestamps, one-way export, asserted rather than
verified support quality, and no durable audit service. These are design
choices or deployment boundaries, not demonstrated donor-driven gaps.

Wrong layer: HMAC audit persistence, worker queues, retry accounting, branch
hashes, state signatures, action bounds, regime control, and drift monitoring.
They belong to a storage, execution, or operational repository with an actual
trusted runtime.

Conflicting/harmful: text scrubbing, qualitative-token rejection, causal or
contradiction scoring, confidence aggregation, automatic severity, automatic
novelty, and regime-based verdict gating. They can turn observations into
authority, erase uncertainty, or collapse Red/Gray/Green/42.

## 9. Ranked upgrade candidates

No candidates qualify as genuinely useful new upgrades. The existing bounded
integrity, telemetry, and linguistic-observation facilities are retained as
already-present low-risk capabilities, not recommended new work.

For completeness, tests that would be mandatory before any future candidate
could be reconsidered are:

- integrity: canonical ordering, malformed serialization, mutation/tampering,
  replay, algorithm/version handling, and manifest-chain divergence;
- telemetry: normal/partial/closed passes, absent provenance, duplicate
  harvests, and proof that counters cannot affect verdicts;
- linguistic metadata: exact-text preservation, representative false
  positives/negatives, malformed input, provenance attachment, and proof that
  labels/severity/42 remain unchanged;
- state signatures or HMAC: key rotation, replay, fork/merge divergence,
  branch mismatch, mutation, invalid state, and bypass attempts;
- workers/retries: queue limits, duplicate execution, concurrency, timeout,
  retry budget, cancellation, and lifecycle recovery.

The latter categories have no meaningful target behavior in this repository,
so implementation complexity and regression risk outweigh value.

## 10. Do-nothing assessment

**Yes. The best engineering decision for this investigation is to integrate
nothing further.**

The target has no autonomous execution path, stochastic model, mutable
inter-module envelope, branch graph, durable audit stream, or operational
control loop for the FORTRESS/GSA mechanisms to protect. The current package
already uses the safe subset of donor concepts without allowing them to
decide epistemic status. More code would mostly create duplicate concepts or
new authority surfaces.

## 11. Recommended next step

**A. No change.**

Keep the current implementation and treat any future persistence, worker, or
service integration as a separate architectural investigation with a concrete
trust boundary. Do not add regimes, confidence scores, state interlocks, or
automatic linguistic judgments to Triad-42.

## Artifact and validation record

- Created: `OPTIONAL_CROSS_CODEBASE_UPGRADES.md`
- No production code or tests changed.
- Existing committed baseline remains `af96bf9`.
- Repository test suite was not rerun because this pass made no code changes;
  the last validated result is 105 passed, 0 failed, 0 skipped.
