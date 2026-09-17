# ORIGIN.md — Triad-42: A Historical White Paper

**Status:** Substantial primary-source recovery. Several questions this
investigation opened as `UNKNOWN: NOT YET RECOVERED` are resolved below with
dated, quoted, sourced artifacts. Others remain genuinely open and are
labeled as such. Nothing here is asserted on the strength of retained
summary alone where a primary artifact was reachable and checked.

**Evidence standard used throughout:**

- **RECOVERED** — a primary artifact was directly read in this investigation
  (a git commit, a file at a specific commit SHA, a dated conversation
  record with its exact ID) and is quoted or cited by that identifier.
- **REPORTED** — a claim rests on a summary, README, or prior investigation's
  restatement, and the underlying primary artifact was not independently
  re-inspected here.
- **UNKNOWN** — no artifact establishing the claim was found in the sources
  available to this investigation (the six in-scope repositories:
  `Triad-42`, `ChatGPT_History`, `Claude_History`, `CoPilot_History`,
  `Gemini_History`, `Gemini_Extraction`).

Where this document corrects an earlier claim, the correction is stated
explicitly rather than silently overwritten.

---

## Executive Summary

Triad-42's own git history, read directly, is a complete and unambiguous
record of the repository's life from its first commit forward. That record
answers most of what a prior recovery attempt had marked unresolved: the
harness's real creation date, the true sequence of hardening passes, and
the origin of an episode that a previous report had misread as evidence of
the harness's creation.

The chat archives in scope go further back than the repository. A
ChatGPT conversation titled **"Triad+42 Governance Model"**, opened
**2026-08-12T18:25:58Z**, is the earliest directly recovered artifact using
the exact terms Red, Gray, Green, and 42 as this project defines them, and
it opens by telling the assistant this is "the cognitive review mechanism
**you've been developing**" — language that presupposes prior development
this investigation did not separately recover. Tracing backward from
there, a second, older, differently-named lineage is visible in the Gemini
activity archive: a governance/authority architecture called **Submission
Protocol → Citadel → Vassal-State Architecture (VSA)**, first recovered
**2026-03-25 through 2026-03-28**, months before "Triad," "Red," "Gray,"
"Green," or "42" appear anywhere in the corpora searched. Whether VSA is a
true ancestor of Triad-42 or a separate, thematically related project is
**not established** — the vocabulary does not overlap, but the underlying
concern (bounding an AI system's authority, keeping a ledger, requiring a
human root) plainly does.

Triad-42 is not a standalone invention. Dated evidence places it inside a
much larger, named ecosystem of governance repositories the account holder
was actively mapping as of **2026-08-21**, and shows at least one sibling
project (`Governance_Gateway`) that was deliberately built with **no
knowledge of Triad-42**, confirming the two are parallel efforts rather than
one descending from the other.

---

## 1. Recovered Chronology

This chronology is built from two directly-inspected sources: the
`Triad-42` repository's own commit log (`git log`, read via the GitHub API,
every commit on `main` from `519d491` to `19cf383`), and the ChatGPT export
in `ChatGPT_History` (`index/manifest.json`, 863 conversations, cross-checked
against individual `summaries/<id>.md` files). Every row below is
**RECOVERED** unless marked otherwise.

| Date (UTC) | Event | Source |
|---|---|---|
| 2026-03-25 | "Submission Protocol" named as replacement for a prior **"SOONG"** protocol; Alpha-Omega Pillar described as system Root Node. Conceptual/textual evidence only — no code recovered. | `Gemini_Extraction/chronology/master_timeline.md` |
| 2026-03-26 | Central defensive/governance hub renamed "Citadel" (from "The Asylum"). | `Gemini_Extraction/chronology/master_timeline.md` |
| 2026-03-28T16:07:28Z | Exact phrase **"PROPOSAL: VASSAL-STATE ARCHITECTURE (VSA)"** appears in a Gemini activity record. Earliest recovered artifact in this project's governance/authority lineage under **any** name. | `Gemini_Extraction/reports/EXECUTIVE_VERDICT.md`, `investigations/VSA/evidence.jsonl` |
| 2026-04-07T07:26:36Z | "THE CITADEL: BETA VASSAL-STATE ARCHITECTURE (VSA)" schema: Core Keep, Gatekeeper Node, Master Ledger, Vassal States Alpha/Beta/Gamma, Verification Layer. | same |
| 2026-04-11T12:18:54Z | VSA evaluated explicitly as a governance/legal instrument: "the AI as a 'vassal' and the user as the 'sovereign.'" | same |
| 2026-07-18T21:07Z | ChatGPT conversation **"AI Governance Integration"**: a "GOVERNANCE-INTEGRATION-V1.0" prompt requesting a hardened module registry, an **immutable context envelope**, prompt-injection defense, and **audit lineage** — conceptually close to what Triad-42 later formalizes as provenance chains, under none of Triad-42's names. | `ChatGPT_History` conv `6a5beb0f-34c4-83ea-86e8-72c2531fa894` |
| 2026-07-18T23:18Z | **"Governance Pipeline Comparison"**: assistant evaluates candidate architectures explicitly against a "hardened AI governance stack (**GSA**/Sentinel-style architecture)." First recovered link between the "GSA" name and this governance work. | conv `6a5c09ae-59ac-83ea-8c02-a732d17b211b` |
| 2026-07-26T03:03Z | **"GSA Governance Core"**: a supplied file header reads "Architecture Family: **GSA / Citadel / AEGIS** Unified Governance Runtime." Bridges the Gemini-side "Citadel" name (April) into the ChatGPT-side work (July) under a shared label. | conv `6a657914-d35c-83ea-bff2-e26b8cf0bd2f` |
| **2026-08-12T18:25:58Z** | **"Triad+42 Governance Model."** Opening user message: *"Triad+42 — The Triad + 42 is the cognitive review mechanism you've been developing for the CCC / Global Gem Governance architecture. It consists of Red, Gray, Green, and 42..."* followed by the 🔴 Red = Assumption Breaker definition verbatim. **This is the earliest directly recovered artifact naming Red/Gray/Green/42 as Triad-42 defines them.** The assistant's reply confirms, point for point, the current constitution: Red/Gray/Green as parallel functions rather than sequential authorities, 42 as separate from the Triad, novelty as a requirement, analogy as grounding-not-proof, and the whole mechanism as advisory. Conversation continues to update_time 2026-08-13T19:11:05Z. | conv `6a7cbaad-c488-83ea-94de-ac333f9a3029` |
| 2026-08-13T05:23:00Z | `Triad-42` repository created on GitHub ("Initial commit," `519d491`). | `Triad-42` commit log |
| 2026-08-14T03:34:46Z | **First code commit**, `c155ee1`, message: *"Initial Triad-42 harness (v2)... Enforces the structure of a Triad+42 pass without performing the Red/Gray/Green/42 reasoning."* 73 tests. Note the commit's own label is **"v2,"** not v1 — see §6. | `Triad-42` commit log |
| 2026-08-14T03:43:36Z | `bc31ea8`, **v2.1.0**, "Harden governance boundaries": six defects found by adversarial review of v2.0.0 (human-root bypass via `relabel()`, post-closure finding injection, mutable Gray list, re-declarable verdicts, hyphen-defeated analogy dedup, missing timestamps), each with a working attack before the fix and a regression test after. 87 tests. | `Triad-42` commit log, `DECISIONS_PENDING.md` |
| 2026-08-14T03:56:50Z | `909c6bd`, README design-question count corrected 5→8. | `Triad-42` commit log |
| 2026-08-14T03:58:33Z | `ef3b196`, **v2.2.0**, "Two-phase Gray and cross-cutting observations": three of the six 2.1.0 defects shared one architectural cause invisible to Red's clustering; Gray gains an independent first phase, then a cross-cutting-observation phase that requires ≥2 scopes and a named cause. Author field: `claude <claude@local>`. 100 tests. | `Triad-42` commit log |
| 2026-08-16T19:06Z, 19:11Z | ChatGPT: two **"Hostile Epistemic Conservation Test"** conversations, five minutes apart — a hostile-reviewer prompt targeting "eight specified repositories" for silent epistemic-status transfer across system boundaries. **Whether `Triad-42` was one of the eight is not established** by the summary text recovered. | convs `6a820a2a…` , `6a820b44…` |
| 2026-08-21T22:20Z | **"Governance Architecture Blueprint."** User names 21 repositories/modules and asks how they connect: `sentinel_os, GSA-815, resume_os, GSA-Gateway, triad-42, ccc, GEMS, ecology, TIE, Fortress, Anvil, conservation_kernel, synapsis, innovation_os, Observe, EDDP, ATS, Citadel, archive, code, graph, herald`. Assistant's answer: core spine is **CCC + Conservation_Kernel + Sentinel_OS + SYNAPSIS**, with GSA-815 as the consolidation/governance-adapter layer, and **"Triad-42, innovation_os, TIE, GEMS, Resume_OS, Ecology as major surrounding systems."** **This directly establishes that Triad-42 is a satellite of a larger, separately-developed governance ecosystem, not its root.** | conv `6a88ce45-78a0-83ea-8f58-f7d720a6cc38` |
| 2026-08-23T22:42Z | **"Build Governance Gateway Baseline"**: a sibling repo, `wking53214/Governance_Gateway`, built explicitly with **"No knowledge of Sentinel, CCC, Triad-42, GEMS, TIE, HERALD, etc."** — a deliberate, stated isolation boundary. **Rules out `Governance_Gateway` as either an ancestor or a component of Triad-42.** | conv `6a8b7737-77b8-83ea-a410-8f8b662794de` |
| 2026-08-23T23:36Z – 2026-08-26T15:58Z | "Pull Governance Gateway" / "Governance_Gateway_whitepaper" (377 messages): a Colab-driven "Round 2" adversarial test campaign (Passes 4, 5, 6, 76, 85, 89) against `Governance_Gateway`, unrelated to `Triad-42`'s own code. Recovered here only to positively distinguish it from Triad-42's adversarial history, since both used the same "adversarial pass" methodology contemporaneously. | convs `6a8b83d9…`, `6a8c3250…`; `ChatGPT_History/PROVENANCE.md` |
| 2026-08-24T23:41:01Z | `d6260cc`, **"Update README.md."** This is the automated commit that cut the README from 234 to 39 lines, truncated mid-code-block. **Correction of a prior claim:** a previous recovery pass characterized "August 28" as the point a "developed Triad-42 repository harness existed." The harness had already existed, fully hardened, since **August 14**. What actually happened on August 24/28 was an unrelated README-corruption-and-fix cycle, recovered below. | `Triad-42` commit log |
| 2026-08-28T10:19:00Z | `241a55d`, PR #1, **"Restore full README, add pyproject license metadata."** Commit message explicitly diagnoses the Aug 24 commit as having "cut the README... leaving it truncated mid-code-block," and restores it to the last hand-written version (`ef3b196`). No source or test changes. **This is a bug fix, not a build event.** | `Triad-42` commit log |
| 2026-09-02T19:48:44Z | `af96bf9`, "Add bounded operational review upgrades," co-authored by GitHub Copilot. | `Triad-42` commit log |
| 2026-09-03T03:45:52Z | `15c9de2` (PR #2), ghost_buster mechanical-layer baseline (42 findings, coincidental number) accepted as suppressed noise-control. | `Triad-42` commit log |
| 2026-09-07T20:39Z | Two uncommitted-then-committed upgrade investigations, `FACTS_STRIDE_OPTIONAL_UPGRADE_INVESTIGATION.md` and `OPTIONAL_CROSS_CODEBASE_UPGRADES.md`, against commit `af96bf9`; conclusion in `ENHANCEMENT_REJECTION.md`: three bounded operational upgrades (content-integrity manifests, read-only telemetry, reviewer-only linguistic observations) integrated, all decision-making automation rejected. | `Triad-42` repository files |
| 2026-09-08T03:45:20Z | `19cf383` (current `main` head): ghost baseline regenerated against a path-relative finding ID instead of an absolute-path ID, fixing a baseline that had been silently inert since it was written. | `Triad-42` commit log |

---

## 2. What the Chronology Resolves

Against the specific unknowns a prior recovery attempt raised:

- **"Was August 28, 2026 the point a developed Triad-42 repository
  existed?"** — **No.** The harness reached its still-current architecture
  (stage order, human-root requirement, severity floor, two-phase Gray,
  write-once records) on **August 14**, fourteen days earlier. August 28 is
  a README bug fix. This corrects, rather than confirms, the earlier
  "REPORTED" claim.
- **"Did a mature conceptual definition exist by August 12, 2026?"** —
  **Yes, RECOVERED**, not merely REPORTED. Conversation
  `6a7cbaad-c488-83ea-94de-ac333f9a3029`, opened 2026-08-12T18:25:58Z,
  contains the definition verbatim, including the 🔴 Red / Assumption
  Breaker framing that survives unchanged into the current README.
- **"Is there a predecessor to Triad-42?"** — **Partially resolved.**
  Triad-42 is one of at least 21 named repositories/modules the account
  holder was mapping as a single ecosystem by August 21, 2026, with a
  separate "core spine" (CCC, Conservation_Kernel, Sentinel_OS, SYNAPSIS).
  Triad-42 is explicitly a "surrounding system," not the root. What CCC or
  the core spine actually is, and when it originated, is **not established**
  by the sources in scope — none of the six in-scope repositories is CCC,
  Conservation_Kernel, Sentinel_OS, or SYNAPSIS itself.
- **"Does Green's idea predate the name Green?"** — **Suggestively yes, not
  proven.** The July 18 "AI Governance Integration" and "Governance Pipeline
  Comparison" conversations already contain an audit-lineage /
  provenance-chain concern three and a half weeks before "Green" or "Triad"
  appear. That is evidence of a broader, earlier grounding/provenance
  concern in the same account's work, not proof that it is Green's direct
  ancestor.
- **"Where does '42' come from?"** — **Still UNKNOWN.** No artifact in
  scope explains the choice. The current codebase's internal module name,
  `deepthought.py`, is a Hitchhiker's-Guide-to-the-Galaxy allusion (Deep
  Thought being the fictional computer that produces the answer "42"), but
  this is a naming choice **recovered from the current implementation**, not
  evidence of the term's original 2026 motivation.
- **"Why does the first commit call itself 'v2'?"** — **Still UNKNOWN.** The
  first commit (`c155ee1`, 2026-08-14T03:34:46Z) is titled "Initial Triad-42
  harness (**v2**)" and its own successor commit refers to "the six defects
  found by adversarial review of **v2.0.0**." No "v1" of the *repository*
  exists in `Triad-42`'s git history — `519d491` ("Initial commit," GitHub's
  auto-generated scaffold) precedes it by less than a day and contains no
  code. The most defensible reading is that "v2" numbers the **concept's**
  maturity (an unrecovered "v1" being the pre-repository conceptual work
  traced in §1, possibly the August 12 conversation itself, possibly
  earlier), not the repository's. This is offered as the most defensible
  reading available, not as a recovered fact.

---

## 3. What Triad-42 Is (Current Architecture)

Recovered directly from `Triad-42/README.md` and `CURRENT_ARCHITECTURE.md`
at commit `19cf383`.

Triad-42 is an advisory cognitive review harness: a dependency-free Python
3.11 package that enforces the **procedure** of a Triad+42 pass without
performing the reasoning itself. Four components:

- **Red — Assumption Breaker.** Attacks hidden assumptions, authority
  overreach, unverified claims, silent deletion, scope expansion. Findings
  carry severity (LOW/MEDIUM/HIGH/CRITICAL); only HIGH/CRITICAL can support
  a `FAILS` verdict; volume never aggregates into severity. A same-scope
  cluster of three findings mandates an examination (1 = anomaly, 2 =
  pattern, 3 = mandate), with an inverted burden: declining to escalate
  requires a distinct origin account for each finding in the group.
- **Gray — Structural Thinker.** Runs in two phases: an independent
  architectural read, then (only after sealing that phase by requesting
  Red's findings) a cross-cutting-observation phase that must name a shared
  cause spanning at least two scopes. Gray holds no severity — holding
  severity would grant a veto the framework does not extend to it — but
  must record an affirmative structural assessment
  (holds/compromised/insufficient-to-assess) rather than defaulting to
  silence read as agreement.
- **Green — Real-World and Analogical Grounding.** Requires a stated break
  point for every analogy (where the comparison fails, not just where it
  holds) and tracks whether an analogy is new or a session reaffirmation via
  normalized keys. Analogy is grounding; analogy is never proof.
- **42 — separate synthesis, not a fourth Triad member.** A five-check
  novelty gate (already stated? renamed? abstraction? genuinely new
  relationship? materially consequential?) that can legitimately terminate
  in "no 42 identified," which the harness treats as a complete, correct
  answer rather than a failure to be worked around.

Two further systems run underneath all four: a **provenance model**
(Chain A — who originated a claim; Chain B — whether a cited source actually
supports the conclusion drawn from it) requiring every fact-labeled claim to
trace to a human-originated root, with a strictly downward-only erasure
cascade; and an **epistemic-label system** (FACT / INFERENCE / ASSUMPTION /
DECISION / RECOMMENDATION / UNKNOWN) that persists across passes and changes
only by recorded human authorization.

The mechanism is constitutionally advisory: it cannot create authority,
override governance, or convert a recommendation into a decision. The
intended chain is Observation → Analysis → Insight → Recommendation → Human
Decision → Authorized State Transition, and the harness actively refuses
verdicts the record cannot support (a `FAILS` with no blocking findings, an
all-clear with blocking findings still open) rather than trusting the
reviewer's self-report.

The reasoning layer — an actual automated Red, Gray, or Green — is
**deliberately unimplemented**. `engines.py` defines protocols only. The
stated reason: three prompts wearing three sets of instructions could
collapse into one reviewer with no way to demonstrate they hadn't, and
Red's protocol specifically omits severity so no automated component can
assign the value that gates a failing verdict.

---

## 4. Component-by-Component Origin Ledger

| Component | Current definition (RECOVERED, `Triad-42` repo) | Earliest recovered occurrence | Status |
|---|---|---|---|
| Red | Assumption Breaker; severity-gated; 1/2/3 clustering | 2026-08-12T18:25:58Z, verbatim, including 🔴 emoji | **RECOVERED** to Aug 12; predecessor before that date UNKNOWN |
| Gray | Structural Thinker; two-phase (added v2.2.0) | 2026-08-12T18:25:58Z (named); two-phase mechanism 2026-08-14T03:58:33Z | **RECOVERED**; earliest naming Aug 12, earliest two-phase design Aug 14 |
| Green | Real-world/analogical grounding; break-statement required | 2026-08-12T18:25:58Z (named); provenance/audit-lineage concern arguably present 2026-07-18 under no name | **RECOVERED** naming to Aug 12; conceptual antecedent (unnamed) plausible from Jul 18, not proven |
| 42 | Separate synthesis; five-check novelty gate | 2026-08-12T18:25:58Z (named, as part of "Triad+42") | **RECOVERED** naming to Aug 12; reason for "42" specifically UNKNOWN |
| Authority boundary (advisory-only) | Explicit throughout README | Assistant's Aug 12 reply already states "the entire mechanism is advisory" | **RECOVERED** to Aug 12 as a stated principle; enforced in code from Aug 14 |
| Human-root / provenance requirement | `provenance.py`, Chain A/B | Conceptually present, unnamed, in "AI Governance Integration" 2026-07-18 (audit lineage, immutable context envelope) | Naming/formal mechanism **RECOVERED** to Aug 14 code; earlier conceptual lineage **suggestive, not proven** |
| Novelty gate ("no 42 identified") | `deepthought.py`, five ordered checks | Named as a requirement in the Aug 12 conversation ("novelty is a requirement for a genuine 42") | **RECOVERED** to Aug 12 as a requirement; the five-check formalization's date is not separately recoverable from chat, only from the Aug 14 code |
| "SOONG" protocol (earliest named predecessor found, any lineage) | N/A — not part of Triad-42's vocabulary | Referenced only as the thing "Submission Protocol" replaced, 2026-03-25 | **UNKNOWN** — SOONG itself was not independently recovered; only its supersession was |

---

## 5. What Was Searched and Came Back Empty

For completeness, and to avoid the earlier report's error of treating an
unsearched source as merely "not yet searched" when it had in fact been
checked and found silent:

- **`Claude_History`** (265 Claude.ai conversations): index carries no
  conversation titles, only IDs and timestamps, so keyword search over
  titles was not possible within this investigation's scope; a full-text
  sweep of all 265 summaries was not performed. The only Claude-attributed
  primary artifacts recovered are the two `Triad-42` commits authored
  `claude <claude@local>` on 2026-08-14 (v2.1.0, v2.2.0) — i.e., Claude's
  documented role in this project's history is as the repository's own
  commit author, not as a separate ideation channel.
- **`CoPilot_History`** (369 conversations, titled by conversation subject):
  zero matches for triad/governance/epistemic/novelty/advisory/vassal/
  citadel/GSA/gatekeeper. CoPilot's only recovered role in this project is
  as a co-author credit on one `Triad-42` commit (`af96bf9`,
  2026-09-02), consistent with in-repo code-completion rather than a
  separate design conversation.
- **`Gemini_History`** (the raw Takeout export): the manifest itself
  contains no dated, titled conversations — it is an activity/HTML export
  lacking canonical conversation IDs, exactly as `Gemini_Extraction`'s own
  `README.md` and `METHODOLOGY.md` describe. All Gemini-sourced findings in
  this document are drawn from `Gemini_Extraction`'s already-completed
  extraction, not from re-parsing `Gemini_History` directly.
- **GitHub code search** (`search_code`) returned zero results for every
  query issued against these repositories, including exact-phrase queries
  known to match content directly read by other means. This tool did not
  function as a reliable search path for private-repository content in this
  environment; every finding in this document was instead obtained by
  direct file/commit retrieval (`get_file_contents`, `list_commits`) or by
  downloading and locally searching index manifests.

---

## 6. Unresolved Questions

Listed in the order they matter most to a future investigator:

1. **What is CCC, Conservation_Kernel, Sentinel_OS, or SYNAPSIS?** The
   August 21 blueprint names these as Triad-42's "core spine." None is one
   of the six repositories in scope for this investigation. Recovering any
   of them would likely resolve most of what remains open about Triad-42's
   true predecessor.
2. **Is Vassal-State Architecture (March 2026) actually ancestral to
   Triad-42, or merely thematically parallel?** The concern (bounding an
   AI's authority, requiring a human root/sovereign, keeping an immutable
   ledger) is the same; the vocabulary is entirely different (Root/Vassal/
   Sovereign/Gatekeeper/Ledger vs. Red/Gray/Green/42/provenance). No
   artifact bridges the two by name.
3. **What is "SOONG"?** The earliest-named entity in any lineage recovered
   here, mentioned only as something Submission Protocol replaced on
   2026-03-25. Not independently recovered.
4. **Why does the Triad-42 repository's first commit call itself "v2"?**
   See §2. The most defensible reading (an unrecovered conceptual "v1"
   predating the repository) is offered, not established.
5. **Were the "eight specified repositories" in the August 16 "Hostile
   Epistemic Conservation Test" inclusive of Triad-42?** Not established
   from the recovered summary text; would require the full transcript.
6. **Why "42"?** Not recovered from any primary source; the Hitchhiker's
   Guide allusion is visible only in the current code's internal naming
   (`deepthought.py`), which is evidence of the current implementer's
   framing, not of the term's original selection.

---

## 7. Source Ledger

| Source | What was directly inspected |
|---|---|
| `Triad-42` | Full commit log (`main`, 13 commits, `519d491`→`19cf383`); `README.md`; `CURRENT_ARCHITECTURE.md`; `DECISIONS_PENDING.md`; `ENHANCEMENT_PROPOSAL.md`; `ENHANCEMENT_REJECTION.md`; module directory listing |
| `ChatGPT_History` | `PROVENANCE.md`; `index/manifest.json` (863 conversations, parsed programmatically for title/date); 9 individual conversation summaries selected by keyword match |
| `Claude_History` | `index/manifest.json` (265 conversations; schema has no titles) |
| `CoPilot_History` | `index/manifest.json` (369 conversations; zero keyword matches) |
| `Gemini_History` | Top-level structure and `index/manifest.json` (activity-export format, no canonical conversation list) |
| `Gemini_Extraction` | `README.md`, `ARCHITECTURE.md`, `METHODOLOGY.md`, `EVIDENCE_POLICY.md`, `PROVENANCE_POLICY.md`, `reports/ENTITY_REGISTRY.md`, `reports/EXECUTIVE_VERDICT.md`, `reports/ROOT_ANALYSIS.md`, `reports/UNKNOWN_ROOT_REPORT.md`, `reports/HISTORICAL_RECONSTRUCTION.md`, `reports/HISTORICAL_CONTAMINATION_REPORT.md`, `chronology/master_timeline.md`, `investigations/GOVERNANCE_KERNEL/` (files present but empty/placeholder) |

---

## Closing Note

The prior draft of this recovery correctly refused to fabricate a
chronology it hadn't earned. That discipline held. What changed is that a
chronology was, in fact, reachable — not by reasoning about the current
architecture, but by reading the repository's own commit log and by
searching the dated conversation archives for the exact vocabulary the
current architecture uses. Where those searches came back with a dated,
quotable, sourced artifact, this document says so and cites it. Where they
came back empty, or where a source turned out to document an adjacent but
distinct project, this document says that too, by name, rather than
folding the silence into an unmarked "unknown."

The correct summary is no longer "the mature architecture is established,
but its genealogy is not." It is: **the repository's genealogy is fully
established from 2026-08-13 forward; the conceptual genealogy is
established back to 2026-08-12, with a plausible but unconfirmed deeper
root in a differently-named governance-architecture lineage reaching back to
at least 2026-03-25; and the ultimate root — SOONG, or whatever preceded
it — remains UNKNOWN: NOT YET RECOVERED.**
