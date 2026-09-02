# Triad-42 Current Architecture

This is a repository-derived model of Triad-42 2.2.0. It describes implemented
behavior, not the aspirations in the README.

## Repository surface

The project is a dependency-free Python 3.11 package (`pyproject.toml`) with
11 modules under `triad42/`, 100 pytest tests in `tests/`, three runnable
examples, a README, and `DECISIONS_PENDING.md`. There is no CI configuration,
database adapter, persistence loader, cryptographic module, external model
client, or implemented reasoning engine.

The public exports in `triad42/__init__.py` expose the records, enums,
exceptions, ledgers, `ReviewPass`, and `Session`. Serialization is one-way:
`to_dict()`/`to_json()` export records; no deserializer reconstructs a pass or
session.

## Constitutional role and control flow

Triad-42 is an advisory harness. Human or external model work supplies the
substantive Red, Gray, Green, and 42 material; the package validates
procedural admissibility. `ReviewPass` enforces the only legal order:

`RED -> GRAY -> GREEN -> DEEP_THOUGHT (42) -> verdict`

Each stage closes once. Red and Green ledgers seal at closure; Gray observations
are exposed as a tuple; a missing Gray assessment becomes explicit
`INSUFFICIENT_TO_ASSESS`; missing 42 input becomes `NO_42_IDENTIFIED`; and a
verdict is write-once with a timestamp and required reason.

## Records and stages

- `epistemic.py`: `Label`, `Authorization`, and mutable `LabeledItem`.
  Labels are FACT, INFERENCE, ASSUMPTION, DECISION, RECOMMENDATION, or UNKNOWN.
  Carry-forward preserves the label and history. Every relabel requires a
  recorded human authorization; registered items also have a provenance guard
  against unauthorized promotion to FACT.
- `provenance.py`: Chain A `Origin`, Chain B `SupportLink`, `RootTrace`, and
  `ProvenanceGraph`. Support links require reasons and cannot cycle. FACT status
  for machine-derived material requires a live path to human-originated
  material. Human erasure records an event and cascades downgrades or decision
  flags; `zombie_check()` detects fact records left without a human root.
- `findings.py`: Red `Finding` and `FindingLedger`. The reviewer supplies
  severity (LOW, MEDIUM, HIGH, CRITICAL). Same-scope/same-tier findings form
  anomaly/pattern/mandate clusters at 1/2/3. A mandate requires examination.
  Examination may name a shared cause (one-tier escalation), demonstrate
  distinct origins, or route to human decision. Escalated findings re-enter
  clustering. Only HIGH/CRITICAL findings can support `FAILS`.
- `lenses.py`: Gray `StructuralObservation`,
  `CrossCuttingObservation`, and explicit `StructuralAssessment`; Green
  `Grounding` and `GroundingLedger`. Gray can make an independent phase-1
  observation, then receive Red findings and record cross-cutting causes across
  at least two scopes. Gray has no severity. Green requires a break statement
  and tracks new grounding versus session reaffirmation using normalized
  analogy keys; repeated analogy is visible but not counted as new support.
- `deepthought.py`: 42 `Candidate`, `CheckAnswer`, and `GateRecord`. Five
  ordered checks reject already-stated, renamed, unrelated, or immaterial
  candidates; abstraction is retained with an abstraction result. A cleared
  candidate must name a consequence area. No candidate is a valid result.
- `retrieval.py`: append-only `CandidateStore` and `CandidateRecord`.
  Findings, examinations, Gray observations, Green groundings, and nonempty
  42 candidates can be harvested with kind, pass, scope, source, surfacing
  status, reason, and timestamp. Non-surfacing is presentation metadata, not
  deletion.
- `review.py`: `ReviewPass` composes the stage ledgers, checks component
  disagreement, exports the complete pass, and yields only labelled
  inference/recommendation outputs. `Session` supplies pass history, the
  provenance graph, analogy history, and candidate store.
- `engines.py`: protocols only (`RedLens`, `GrayLens`, `GreenLens`,
  `DeepThoughtEngine`, `IndependenceCheck`) plus `unavailable()`. No automated
  lens or model execution is implemented. Red's protocol deliberately omits
  severity.
- `integrity.py`: canonical JSON UTF-8 encoding, SHA-256 content digests, and
  optional previous-digest links for export/storage manifests. This attests
  representation identity only.
- `observations.py`: deterministic, non-destructive surface-language signals
  retaining the original text. These are not connected to review decisions.
- `telemetry.py`: read-only counters derived from a pass and optional session;
  counters are not inputs to any governance rule.
- `_clock.py` supplies UTC timestamps; `errors.py` supplies domain exceptions.

## Verdict and escalation authority

The harness does not calculate truth, novelty, severity, or confidence. It
checks that a declared `Verdict` is compatible with the record:
`NO_BLOCKING_FINDINGS`, `FAILS`, `INSUFFICIENT_EVIDENCE`, or
`REQUIRES_HUMAN_DECISION`. A Red blocking finding plus affirmative Gray
`STRUCTURE_HOLDS` and new Green grounding is an explicit disagreement; it
routes to human decision unless a written override is supplied.

## Existing protections relevant to this investigation

Already implemented: deterministic analogy-key normalization; recurrence
tracking for Green analogies; stage order and sealing; write-once verdicts;
timestamps on records; append-only candidate retention; explicit surfacing
reasons; one-way JSON export; label-history authorization; human-root and
support-chain checks; cycle prevention; erasure cascade; cross-cutting Gray
observations; explicit negative outcomes; export-boundary content manifests;
reviewer-only linguistic observations; and read-only operational counters.

Not implemented: text sanitization or rewriting; epistemic linguistic
classifiers; stage duration measurement; telemetry persistence/export;
anomaly or variance scores; fragility scores; confidence aggregation;
persistence/reload; or automatic reasoning.

## Architectural conclusion

The package is a procedural and provenance-preserving review boundary, not a
content-processing, scoring, or autonomous-evaluation system. Any addition
that turns wording into epistemic status, recurrence into invalidity, hashes
into truth, or telemetry into a decision would cross that boundary.
