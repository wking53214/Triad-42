# Triad-42 Bounded Operational Upgrades

> **Historical document.** Written against Triad-42 2.2.0. As of 3.0.0 the
> provenance graph, relabel, `Authorization` and fact promotion described here
> were removed; CCC owns those rules. See README, "Origin, promotion, and
> erasure belong to CCC".

These additive APIs are operational and observational. They do not make
Triad-42 decide truth, severity, novelty, grounding, or authority.

## Export-boundary content manifest

`triad42.integrity.manifest_for()` hashes canonical sorted-key JSON with
SHA-256 and optionally records a previous digest. `verify()` checks content
identity only. The caller owns durable manifest storage and algorithm
lifecycle. Tests cover deterministic encoding and changed content.

## Read-only operational telemetry

`triad42.telemetry.collect_pass_telemetry()` returns immutable counters for
closed stages, findings, examinations, escalations, gate failures, human
routing/overrides, provenance depth, and harvested retrieval records. It does
not mutate a pass and no governance rule consumes it. Tests cover counters and
read-only behavior.

## Reviewer-only linguistic observations

`triad42.observations.observe_language()` returns the exact original text and
surface signals for first-person, uncertainty, causal, absolute, modal,
quantitative, and evaluative wording. It is not wired into any decision path.
False positives and false negatives are expected; vocabulary is not evidence.
Tests cover preservation, representative signals, and empty input.

## Compatibility and rationale

All three APIs preserve stage boundaries, human-root enforcement,
write-once/sealing semantics, and epistemic-status preservation. They belong at
Triad-42's export and reviewer boundaries. Autonomous classifiers, scoring
engines, persistence services, and automated lenses remain out of scope.
