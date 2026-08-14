# Decisions Pending

Five questions the framework does not answer. Each was given a working default
so the build could proceed. None of these are decisions. They are placeholders
with reasons attached, and each should be settled deliberately.

---

## 1. What a passing verdict is called and what it means

**The gap.** The framework names four outputs precisely, and all four are
negative: fails, insufficient evidence, requires human decision, no 42
identified. It never says what a clean result looks like.

**Default chosen.** `NO_BLOCKING_FINDINGS`. It is admissible only when no
critical or high findings remain after all escalation is complete.

**Alternatives considered.**
- `PASS`, rejected because it implies approval, and the mechanism has no
  authority to approve anything.
- `REVIEW COMPLETE`, rejected because it says nothing about what was found.
- No positive verdict at all, with absence of failure being the result.
  Rejected because a record with no verdict cannot be distinguished from a
  review that was abandoned halfway.

**Why this one.** It states what is true about the record without implying a
judgement the mechanism cannot make. A proposal can have no blocking findings
and still be a bad idea.

**What would change the answer.** If Triad+42 becomes a gate in a pipeline
rather than an advisory pass, the pipeline will need to know the difference
between "reviewed and clean" and "reviewed and acceptable," and those are not
the same thing.

---

## 2. How component disagreement resolves

**The gap.** Red returns blocking findings. Gray finds nothing structurally
wrong. Green establishes real grounding. The framework says the mechanism is
advisory, which implies the disagreement surfaces to a human, but it never
says so.

**Default chosen.** Disagreement routes to `REQUIRES_HUMAN_DECISION`. Declaring
any other verdict over an active disagreement requires a written override that
is stored in the record.

**Alternatives considered.**
- Red wins automatically, on the theory that an unrefuted objection stands.
  Rejected because it gives Red an effective veto, and the framework grants no
  component authority over the others.
- Majority across the three lenses. Rejected because the three do different
  jobs on different evidence, so counting them treats disagreement as a tie
  rather than as information.
- Silent precedence. Rejected outright: a disagreement that does not appear in
  the record is a disagreement that gets lost.

**Why this one.** It uses an output the framework already has, and it makes
overriding possible but visible.

**⚠️ This is the one most worth settling by hand.** The detection rule is
currently crude: it fires when Red has blocking findings, Gray recorded nothing
at all, and Green established at least one new grounding. Real disagreement is
subtler than that, and a better rule would need Gray to say something
affirmative about whether the structure holds rather than the harness reading
Gray's silence as agreement.

---

## 3. Whether the harness should refuse thin input

**The gap.** Nothing stops a review of something too vague to review. A
mechanism that always produces output will produce output on nothing.

**Default chosen.** No automatic refusal. The harness requires a labelled
subject and nothing more. `INSUFFICIENT_EVIDENCE` is available as a
reviewer-declared verdict.

**Alternatives considered.**
- A minimum length or structure requirement on the subject. Rejected because
  any threshold would be arbitrary, and a short proposal can be perfectly
  reviewable.
- Requiring a minimum number of findings before a verdict. Rejected because it
  would pressure reviewers into producing findings, which is the theatre
  problem in a new place.

**Why this one.** Judging whether input is reviewable is a judgement, and the
harness does not make judgements. Leaving it to the reviewer is consistent with
everything else here.

**What would change the answer.** If the harness ever runs unattended, this
becomes the missing guard, because nothing else would catch a review of
nothing.

---

## 4. How a session is bounded

**The gap.** Two rules need history to work: repetition is not verification,
and an analogy used twice is a reaffirmation rather than a second discovery.
Both need to know what counts as "before." The framework never says.

**Default chosen.** The caller creates a session explicitly and decides when it
ends. Analogy history is shared across every pass in that session and is not
shared between sessions.

**Alternatives considered.**
- One session per subject. Rejected because a single subject reviewed across
  weeks would carry stale analogy history forever.
- Time-boxed sessions. Rejected because elapsed time has nothing to do with
  whether grounding was already established.
- Global history across everything. Rejected because an analogy that grounded a
  point about one system is genuinely new when applied to another.

**Why this one.** The caller knows what belongs together and the harness does
not.

**What would change the answer.** If passes get archived and reloaded later,
the session boundary becomes a storage question rather than a caller decision,
and the answer will have to move.

---

## 5. Whether Gray needs its own severity scheme

**The gap.** Red findings carry severity. Green groundings carry a status. Gray
observations carry neither.

**Default chosen.** No severity on Gray. Gray records observations, the
distinction at stake, and where two overlapping rules should be consolidated,
scoped, inherited, or kept separate. Keeping rules separate requires a stated
reason, which is the framework's own rule.

**Alternatives considered.**
- Mirror Red's four tiers. Rejected because Red severity means "how much does
  this threaten the proposal," and that question does not translate. A
  collapsed distinction is either present or it is not.
- A binary sound/unsound marker. Rejected as too coarse to be useful, though it
  would help with question 2 above.

**Why this one.** Structural problems are not naturally ranked, and inventing a
ranking would invite the same volume-as-rigor substitution the Red amendment
was written to close.

**What would change the answer.** Question 2. If disagreement detection needs
Gray to affirmatively say the structure holds, Gray will need some marker, and
this decision reopens.

---

## 6. Whether an automated lens may assign severity

**The gap.** Severity gates the failing verdict, so whoever assigns it holds an
effective veto. The framework never says whether a machine may hold it.

**Default chosen.** The Red interface returns findings without severity.
Severity stays a human act.

**Alternatives considered.**
- Machine-assigned severity with human override. Rejected for now because an
  override that is rarely exercised is not a control.
- Machine-proposed severity marked as a proposal. Plausible and not yet
  designed, since it needs a rule for what happens when the human never
  responds.

**Why this one.** It was the conclusion of a worked Triad+42 pass run against
this exact question, and the escalated finding was a blocking one.

---

## 7. How lens independence would be demonstrated

**The gap.** Three prompts driving the same model can collapse into one
reviewer in three costumes. No test distinguishes that from a working Triad.

**Default chosen.** No automated lenses at all. The interfaces exist and
nothing implements them.

**Alternatives considered.**
- Ship the lenses and assume distinctness. Rejected: it asserts a property that
  cannot currently be checked.
- Use different models per lens. Reduces the risk without measuring it, and
  introduces a new question about whether the lenses are then comparable.

**Why this one.** Building the seam is cheap. Building lenses whose central
claim cannot be tested is not.

**What would change the answer.** A stated test with a defined failure
threshold. That is the actual prerequisite, and it is a design question rather
than an engineering one.

---

## 8. Terminology: two meanings of "mandate"

**The collision.** In the clustering rule, mandate means the examination is
mandatory. Elsewhere it means an established requirement that only a human may
authorize.

**Default chosen.** Explicitly scoped rather than renamed. In this package,
mandate refers to an examination duty placed on the reviewer and nothing more.
No cluster at any count produces an authorized conclusion.

**Alternatives considered.**
- Rename the cluster state. Rejected because the 1/2/3 wording is
  user-established and the specification says not to dilute it.
- Consolidate the two meanings. Rejected: they are different concepts, and
  collapsing them is exactly the structural drift the mechanism exists to
  catch.

**Why this one.** Gray's own rule offers four dispositions for overlapping
concepts. This is the second: explicitly scoped.

---

## Known limitations, recorded rather than fixed

- **Escalation is now the cheap path.** Inverting the burden at three findings
  means writing three origin accounts is harder than escalating. Over-escalation
  is therefore the expected drift, not under-escalation. That is the right trade
  at a mandate threshold, but it is a trade.
- **Scope is a free-text string.** Two reviewers can spell the same component
  differently and their findings will not cluster. Nothing detects this.
- **Support links are asserted, not verified.** Chain B records that someone
  claimed a source backs a conclusion, and requires a reason. It cannot check
  whether the reason is any good.
- **External sources are trusted as roots.** Material marked as coming from an
  external source can root a fact without a human in the chain. That is a
  convenience, and it is the weakest point in the human root requirement.
- **Nothing verifies reasoning quality.** Every check that requires reasoning
  accepts any non-empty text. The harness confirms that a reason was given, not
  that it is a good one. Closing this would require the harness to judge
  content, which is the line the whole design refuses to cross.
