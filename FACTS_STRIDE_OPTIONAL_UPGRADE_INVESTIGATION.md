# FACTS / STRIDE Optional Upgrade Investigation

**Target:** `/home/wking53214/Triad-42`, commit `af96bf9`  
**Method:** repository-first review of package code, tests, examples, README,
pending decisions, and the current operational-upgrade modules. FACTS and
STRIDE were treated as conceptual source families; no supplied implementation
was copied. This investigation made no production or test changes.

## Executive Verdict

**NO INTEGRATION RECOMMENDED.**

FACTS contributes no new core capability. Its safe subset—canonical
serialization and content identity—is already present in `integrity.py`.
Destructive or subjective text transformation is outside Triad-42's role.

STRIDE contributes no new core capability. Its lifecycle, structured results,
history, recurrence, and telemetry ideas are already implemented where they
fit. Its execution controls, retries, queues, async workers, anomaly scores,
confidence aggregation, and authenticated runtime envelopes presuppose an
autonomous service that Triad-42 intentionally does not contain.

The only plausible deltas are deployment-boundary concerns: durable
transformation manifests if a transformation service is introduced, or
authenticated audit storage if an external persistence service is introduced.
Neither is a demonstrated current repository gap.

## Repository Architecture Reviewed

Triad-42 is a dependency-free Python 3.11 advisory review harness. It stores
review records in memory and exports one-way JSON. There is no database,
reload path, queue, worker, retry loop, async execution path, external model
client, branch/merge state graph, or persistent audit service.

`ReviewPass` enforces `RED -> GRAY -> GREEN -> 42`, stage closure, Red/Green
sealing, Gray phase separation, verdict admissibility, disagreement handling,
timestamps, and write-once verdicts. `Session` owns pass history, provenance,
analogy history, and the append-only candidate store.

`epistemic.py` preserves labels and human authorizations. `provenance.py`
separates origin from support, rejects support cycles, enforces human-root
requirements for machine-derived FACT promotion, and cascades human erasure.
`findings.py` implements reviewer-supplied severity, same-scope clustering,
mandatory examination, and one-tier escalation. `lenses.py` records Gray
structure and Green grounding without assigning Gray severity or truth.
`deepthought.py` records the ordered 42 novelty gate. `engines.py` contains
protocols only; automated reasoning is deliberately absent.

Current donor-adjacent facilities:

- `integrity.py`: canonical sorted-key JSON UTF-8 bytes, SHA-256 digest, and
  optional previous-digest metadata.
- `observations.py`: exact-text-preserving linguistic surface signals,
  disconnected from epistemic decisions.
- `telemetry.py`: immutable read-only pass counters, disconnected from
  governance logic.

Existing tests total 105 passing tests. UUIDs and timestamps are intentionally
variable metadata; serialization ordering and integrity bytes are deterministic.

## FACTS Capability Mapping

| Source concept | Current equivalent / location | Tests | Novelty / overlap | Value and recommendation |
|---|---|---|---|---|
| deterministic canonicalization | `integrity.canonical_bytes()`; `ReviewPass.to_json()` sorts keys | `test_manifest_is_deterministic...`, serialization tests | A; export-only equivalent | Low new value — REUSE EXISTING |
| explicit transformation stages | Red/Gray/Green/42 stages in `review.py` | stage-order and sealing tests | Overlap, but semantics differ | High governance value already covered — REUSE EXISTING |
| transformation manifests | `IntegrityManifest` describes canonical export, not a transformation | manifest tests | C; no transform provenance | No current transformation to manifest — DEFER |
| input/output artifact identity | item/candidate/source IDs; digest only for supplied mapping | serialization/provenance tests | C; IDs identify records, not content | Adequate for current in-memory model — DEFER |
| SHA-256 content identity | `content_digest()` / `manifest_for()` | mutation verification test | A | Already sufficient for content identity — REUSE EXISTING |
| transformation metadata | `LabeledItem` history and provenance metadata, no transform record | label/provenance tests | C; no transform exists | Add only with a real transformation boundary — P1 DOCUMENT ONLY |
| version-bound processing | package version in `pyproject.toml`; no policy/version field in records | no version-binding test | D in abstract, E in current architecture | No processor exists to bind — P1 DOCUMENT ONLY |
| reproducible transformation | no transformation pipeline; canonical export is reproducible for same mapping | canonical digest test | E; not applicable | Do not manufacture a transform engine — REJECT |
| before/after artifact relationship | provenance support links relate claims, not transformed artifacts | support-chain tests | C but different semantics | Do not overload epistemic support links — REJECT |
| deterministic verification | `IntegrityManifest.verify()` checks representation digest | manifest mutation test | A for export | Sufficient at current boundary — REUSE EXISTING |

FACTS' first-person, hedging, qualitative, and prohibited-language rules are
domain-specific policy examples. `observations.py` may report such surface
signals, but no signal filters input, rewrites text, changes labels, or
supports a verdict.

## STRIDE Capability Mapping

| Source concept | Current equivalent / location | Tests | Novelty / overlap | Value and recommendation |
|---|---|---|---|---|
| centralized policy patterns | dataclass validation and enum constraints distributed by domain module | broad malformed-input tests | C; no policy engine | No shared policy vocabulary is required — E / NO VALUE |
| policy validation interceptors | `ReviewPass._require()`, ledger guards, provenance guard | bypass/regression tests | A structurally, not as middleware | Existing boundary checks are stronger for this model — REUSE EXISTING |
| input normalization | `normalize_key()` only for analogy identity | normalization tests | A narrow equivalent | Do not normalize claim text — REUSE EXISTING |
| bounded gateway behavior | stage order and admissibility checks | stage/verdict tests | A for records; no runtime traffic | No request gateway exists — H / NOT APPLICABLE |
| pipeline lifecycle state | `Stage`, `_closed_stages`, sealing | stage closure tests | A | Already load-bearing — REUSE EXISTING |
| ACCEPTED/RETRY/BLOCKED/ERROR states | domain exceptions and explicit verdict enum | verdict/error tests | E; action states do not map cleanly | Adding runtime states would misstate authority — REJECT |
| bounded retry behavior | none | none | E; no retryable execution | No loop to bound — NOT APPLICABLE |
| duplicate output detection | Green analogy keys and reaffirmation status; append-only candidates | repeated-analogy tests | A for declared analogy identity; intentionally not text identity | Sufficient without suppression — REUSE EXISTING |
| loop detection | support-cycle prevention; `FindingLedger.MAX_ROUNDS` guard | support-cycle/escalation tests | A for relevant graph and escalation loops | Existing controls cover actual loops — REUSE EXISTING |
| historical execution state | `Session.passes`, provenance histories, candidate records | session/export tests | C; no execution history | Current review history is sufficient — DEFER |
| deterministic output hashing | `content_digest()` over canonical export | digest tests | A at export boundary | No state-transition hash needed — REUSE EXISTING |
| async job/worker architecture | none | none | E; no jobs | Outside kernel — NOT APPLICABLE |
| queue boundaries | none | none | E; no queue | Outside kernel — NOT APPLICABLE |
| telemetry attached to execution | `PassTelemetry` from pass/session | telemetry tests | A for review process, no executor | Sufficient current observability — REUSE EXISTING |
| structured execution results | `ReviewPass`, `Session`, `GateRecord`, `CandidateRecord` exports | serialization tests | A domain-native result envelope | Do not add generic envelope — REUSE EXISTING |
| cryptographic attestation | SHA-256 content identity only | manifest tests | E; no authenticating authority | Hash is not attestation — REJECT |
| HMAC authenticity/integrity | none | none | D only for durable trusted audit | Requires external key/persistence boundary — P1 DOCUMENT ONLY |
| policy interceptors | object-level guards and stage checks | bypass tests | A at actual mutation boundaries | Middleware would duplicate them — REUSE EXISTING |
| centralized policy definitions | enums/constants and per-object invariants | domain tests | B only in an execution system | No consolidation needed — E / NO VALUE |
| operational confidence assessment | deliberately absent | tests enforce no automatic severity/novelty | G | Would create forbidden authority — REJECT |
| anomaly detection | Red anomaly/pattern/mandate states; Gray cross-cutting observations | clustering/Gray tests | A procedural equivalent | Do not add numeric anomaly scoring — REUSE EXISTING |
| stability assessment | Gray structural assessment is reviewer-authored | Gray assessment tests | Partial but intentional | No automatic stable/unstable regime — REJECT |
| fragility assessment | no numeric fragility model; reviewer findings can expose weakness | finding tests | E/G | Domain judgment belongs to reviewers — REJECT |
| consolidated risk/confidence output | declared verdict checked against findings; no score | verdict tests | G | Preserve separate signals and human declaration — REJECT |

## Existing-Functionality / Redundancy Findings

### Stronger or equivalent existing mechanisms

Triad-42 already has stronger domain-specific enforcement for lifecycle,
provenance, human authorization, support-chain structure, erasure effects,
write-once behavior, candidate retention, and stage separation than a generic
runtime wrapper would provide. Existing tests include direct bypass attempts:
late ledger writes, direct relabel bypass, duplicate verdict declaration,
analogy normalization failure, support cycles, and unexamined mandates.

### Present but intentionally limited

Content digests do not authenticate an actor. IDs and timestamps do not make
execution deterministic. `PassTelemetry` has no persistence or duration
measurement. `LinguisticObservation` has expected false positives/negatives.
Support links record asserted reasons but do not verify reasoning quality.
These limits are explicit and appropriate to the current boundary.

### Wrong layer

HMAC audit logs, worker queues, retry budgets, async wrappers, state-signature
chains, fork/merge anchors, regime controllers, action bounds, and drift
monitors belong in a persistence, execution, or operations service with a
defined trust owner. They should not be added to the review kernel.

### Conflicting or unsafe

Destructive sanitization, qualitative-token rejection, automatic policy
classification, confidence aggregation, automatic severity, and
regime-based verdict gating could make wording or volume function as evidence.
They would weaken epistemic-status preservation or give software authority
over Red, Gray, Green, or 42.

## Novel Capability Candidates

No candidate meets the repository's threshold for a new implementation.

The nearest candidate is **policy-version binding for a future transformation
service**. It is currently only a documentation lead because Triad-42 has no
transformation service, policy registry, or before/after artifact model.
Implementing it now would create speculative infrastructure rather than close
a measured gap.

## Optional Upgrade Ledger

| ID | Source | Capability | Current state | Novelty | Value | Risk | Integration location | Dependencies | Test requirements | Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|
| R1 | FACTS | Canonical export identity | Present in `integrity.py` | None | High for export consumers | Low | Attestation layer | None | Canonical ordering, mutation, malformed mapping | REUSE EXISTING |
| R2 | FACTS | Transformation manifest | No transformation path | Potential | Low now / medium later | Medium | Transformation layer, not kernel | Transform service and policy registry | Before/after binding, version, replay, tamper | P1 — DOCUMENT ONLY |
| R3 | STRIDE | Lifecycle/gateway state | Present in `review.py` and ledgers | None | High | Low | Core governance boundary | None | Stage order, bypass, closure, regression | REUSE EXISTING |
| R4 | STRIDE | Duplicate/loop protection | Green recurrence and graph-cycle checks present | None | High | Low | Existing ledgers/graph | None | Independent duplicate, cycle, legitimate repeat | REUSE EXISTING |
| R5 | STRIDE | Execution telemetry | `PassTelemetry` present and read-only | None | Medium | Low | Observability | None | Partial pass, harvest, no decision influence | REUSE EXISTING |
| R6 | STRIDE | HMAC audit authenticity | No durable audit service | Potential only | Low in current package | High | External attestation/persistence layer | Key management and trusted storage | Key rotation, replay, tamper, failure semantics | P1 — DOCUMENT ONLY |
| R7 | STRIDE | Async workers/retries/queues | Absent by design | Novel but misaligned | None | High | Separate execution repository | Runtime workload | Concurrency, timeout, duplicate execution, retry limits | P0 — REJECT |
| R8 | STRIDE | anomaly/stability/fragility/confidence | Procedural review already handles observations | None / harmful | Negative | High | Nowhere in kernel | None | Would require proving non-authority | P0 — REJECT |
| R9 | BOTH | Unified normalize-transform-attest pipeline | No safe transformation boundary | Novel but misaligned | Low | High | Separate transformation service | Original preservation, policy registry | Reproduction, lineage, tamper, rollback | P0 — REJECT |

## Highest-Value Candidate

There is no new highest-value candidate. The highest-value existing boundary is
the current `ReviewPass`/ledger/provenance architecture; the highest-value
donor-derived capability already implemented is canonical export content
identity in `integrity.py`.

## Rejected Concepts

- **Destructive normalization/transformation:** can replace or obscure the
  original claim and weaken provenance.
- **Linguistic policy enforcement:** wording is not evidence, truth, causality,
  severity, or epistemic status.
- **Generic duplicate blocking:** repeated text is not repeated epistemic
  content and may suppress independent observations.
- **Retry, queue, async, and bounded action controls:** no autonomous action
  path exists to constrain.
- **HMAC as a kernel feature:** authenticity requires a key owner and durable
  audit boundary; SHA-256 content identity is not authenticity.
- **State signatures, anchors, forks, and merges:** no execution lineage graph
  exists; semantic provenance is not interchangeable with runtime lineage.
- **Regime, anomaly, volatility, fragility, and confidence scoring:** creates
  hidden authority and risks automatic verdict/severity decisions.
- **Generic execution envelopes:** `ReviewPass` and `Session` already are the
  domain-native structured boundary objects.

## Security and Governance Assessment

The real enforcement points are:

1. `ReviewPass._require()` and stage closure prevent out-of-order writes.
2. Red/Green sealing prevents mutation after stage closure.
3. `ProvenanceGraph.register()` installs a promotion guard on every registered
   item; support links reject cycles.
4. Finding closure rejects unexamined mandates.
5. Verdict declaration is human-authored, checked, and write-once.
6. Candidate storage is append-only and records non-surfacing reasons.
7. Integrity verification detects representation changes only.
8. Linguistic observations and telemetry are intentionally outside governance.

No donor mechanism strengthens these boundaries without introducing a new
trusted executor or persistence operator. Cryptographic hashes protect content
identity; they do not provide provenance, authorization, attestation, or
epistemic integrity.

## Test/Assurance Requirements

Because no new implementation is recommended, no new tests are required.
Existing tests cover normal and malformed records, stage and mutation bypasses,
support cycles, erasure cascades, repetition/reaffirmation, serialization,
integrity mutation, linguistic metadata preservation, and telemetry isolation.

If a future external transformation or persistence service is proposed, its
minimum assurance suite must cover:

- deterministic same-input/same-policy reproduction;
- original and transformed artifact preservation;
- policy/version binding and before/after lineage;
- manifest tampering and malformed serialization;
- HMAC key rotation, replay, truncation, and unauthorized writer behavior;
- duplicate execution, queue/retry bounds, concurrency, timeout, and rollback;
- proof that all observations remain unable to mutate labels, severity,
  provenance, grounding, 42 results, or verdicts.

## Recommended Next Step

**A. No change.**

Keep Triad-42 as a review/governance harness. If a future system adds an actual
transformation or autonomous execution service, perform a separate
boundary-specific investigation there and bind its artifacts to Triad-42 only
through explicit, human-labelled provenance.

## Final Decision

**NO INTEGRATION RECOMMENDED.**

FACTS offers reusable export-boundary terminology, but no missing capability.
STRIDE offers reusable runtime-service patterns, but no compatible current
target. There is no common abstraction worth extracting now, no reason to
merge the source families, and no demonstrated transformation, lifecycle,
retry, attestation, or telemetry gap requiring additional code.
