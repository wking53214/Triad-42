# Triad-42 Conceptual Enhancement Review

## Determination

Three bounded operational upgrades are justified; no epistemic automation is
justified. The upgrades are export-boundary content integrity, read-only
process telemetry, and reviewer-only linguistic observations. They do not
alter decisions, labels, severity, provenance, or verdicts.

## Translation and scoring matrix

Scores are A-H on a 0-5 scale: fit, gap, constitutional compatibility,
incremental value, auditability, complexity burden (5 = low burden),
attack-surface impact, and testability. Totals are advisory only.

| Concept | Abstract capability | Existing equivalent / gap | Score | Classification |
|---|---|---|---:|---|
| normalization | deterministic representation normalization | `normalize_key()` protects analogy identity; claim text is untouched | 20 | REJECT |
| SHA-256 manifest | representation integrity | one-way export had no content commitment | 29 | INTEGRATE |
| first-person framing | linguistic signal detection | no reviewer-only surface metadata | 27 | INTEGRATE |
| hedging / qualifiers | uncertainty-language detection | labels do not infer wording | 27 | INTEGRATE |
| causal language | causal-claim signal detection | named causes remain reviewer-authored | 27 | INTEGRATE |
| absolute/modal/quantitative/evaluative language | linguistic metadata | no surface signal facility | 27 | INTEGRATE |
| repeated output | recurrence detection | Green analogy history and reaffirmation already exist | 22 | ALREADY COVERED |
| lifecycle state | process-state tracking | ordered stages, sealing, write-once verdict | 31 | ALREADY COVERED |
| telemetry | process observability | records expose data but had no stable counter view | 30 | INTEGRATE |
| anomaly/variance/fragility | structural deviation analysis | Red clusters and Gray cross-cutting observations | 20 | REJECT |
| multi-signal confidence | evidence synthesis | separate ledgers and declared verdicts | 20 | REJECT |
| execution envelope | structured boundary object | `ReviewPass`/`Session` and JSON export | 32 | ALREADY COVERED |

No candidate is `INVESTIGATE FURTHER`, `DOCUMENT ONLY`, or `NOT APPLICABLE`.
The integrated items are deliberately narrow facilities, not automated
evaluation.

## Safety boundaries

`observe_language()` preserves exact original text and emits only reviewer
metadata. Hedging is not error, assertion is not evidence, causal vocabulary
is not causation, and first-person framing is not provenance. The signals are
not consumed by Red, Gray, Green, 42, provenance, labels, severity, or verdicts.

`collect_pass_telemetry()` is read-only. Counts cannot raise severity,
establish evidence, suppress candidates, or override a verdict. It does not
invent confidence, stability, fragility, or duration scores.

`integrity.py` hashes canonical exported bytes only. A valid digest cannot
establish epistemic integrity, provenance correctness, support quality, or
truth. Durable manifest storage and algorithm lifecycle remain caller duties.

## Rejected concepts and adversarial results

Text rewriting risks confusing a sanitized representation with the original.
Generic duplicate blocking confuses repeated text with repeated epistemic
content and can suppress independent findings. Anomaly, variance, fragility,
and multi-signal scores can become hidden severity or confidence engines.
Hash-as-truth, automated lens precedence, machine novelty ratification, and
stage collapse all violate the advisory boundary.

The upgrades cannot make machine material human-rooted through transformation,
cannot modify an earlier sealed stage, and cannot change a 42 input before
novelty review. False positives and false negatives in linguistic metadata are
expected and remain visible to the reviewer.

## Recommendation

Implement the three bounded operational upgrades and reject all
decision-making variants. The highest-value donor idea is lifecycle and
structured-record discipline, extended only with safe observability
boundaries. The highest-risk idea is multi-signal linguistic/telemetry scoring.

## Validation

- Baseline: 100 passed, 0 failed, 0 skipped.
- Final: 105 passed, 0 failed, 0 skipped.
- No external implementation was copied or ported.
