# Triad+42

An advisory cognitive review harness.

## What this is

Triad+42 is a review mechanism made of three lenses and one separate synthesis
step. Red attacks assumptions. Gray maps structure. Green tests the idea against
systems that actually exist. Then 42 looks for a genuinely new insight in what
the three of them turned up.

This package does not do any of that thinking. A human or a model does the
thinking. What the package does is hold the reviewer to the rules.

That split is deliberate. The framework says the mechanism is advisory and
carries no authority. Software that judged the content of findings would be
claiming exactly the authority the framework denies it. So the harness never
decides whether a finding is serious, whether an analogy is apt, or whether an
insight is novel. It only refuses records that break the framework's own rules.

## What it enforces

**The stages run in order.** Red, then Gray, then Green, then 42. Trying to
ground an idea before anyone has attacked it is rejected. The order matters
because Green's job produces confidence, and if Green went first that confidence
would reach Red as a premise instead of a claim to be tested.

**Epistemic labels survive.** Everything entering or leaving a pass is marked as
a fact, an inference, an assumption, a decision, a recommendation, or unknown.
Those marks do not change on their own. A recommendation that survives ten
reviews is still a recommendation. Inside Triad+42 a label cannot change at all:
there is no relabel operation, and a labeled item is immutable. Changing what a
claim is, or recording that a human adopted it, happens in CCC, never here.
This is the rule that stops a suggestion from quietly becoming a premise three
passes later.

**Findings carry severity, and volume does not aggregate.** Every Red finding is
marked critical, high, medium, or low, by the reviewer. A failing verdict can
only rest on a critical or high finding. Fifty medium findings do not add up to
a failure. This closes off the review that looks rigorous because it is long.

**Three findings in one place force an examination.** One finding is an anomaly
and gets recorded. Two is a pattern, and the reviewer may look for a shared
cause. Three is a mandate: the examination is required, and escalation is
assumed to be the right answer.

Declining to escalate at that point is allowed, but it costs something. The
reviewer has to give a separate, distinct origin for each finding in the group.
Saying "these are unrelated" is not accepted. Giving the same explanation for
all three is not accepted either, because one explanation covering three
findings is a shared cause, which is an escalation rather than an exemption from
one.

Escalation moves exactly one step. Three low findings with a shared cause
produce one medium, never a high. That new finding can go on to join a group of
its own, so a real systemic problem can climb, but it climbs one rung at a time
with a named reason at each step.

If the reviewer senses something is wrong but cannot name what, the examination
can return "requires human decision." That result cannot be folded into any
other verdict.

**Gray works in two phases, and the second one is what catches cross-cutting
causes.** In the first phase Gray reads the architecture on its own, with no
access to what Red found. Asking for Red's findings is what seals that phase:
Gray cannot see them without first putting its own observations on the record.
That keeps Red's framing of the problem from shaping Gray's structural read,
which is the same reason Green runs after Red rather than before.

In the second phase Gray can record a cross-cutting observation, which is one
structural cause showing up in separate places. It has to name the cause, cite
the findings, and span at least two distinct scopes. One that stays inside a
single scope is same-scope accumulation, which is Red's clustering job.

That division is deliberate. Red's 1/2/3 rule measures accumulation inside one
scope, so unrelated findings that happen to sit near each other do not cluster.
A cause that spans scopes is invisible to that rule by design, and it is Gray's
to find.

A cross-cutting observation never changes severity. Gray does not hold severity,
because severity gates the failing verdict and holding it would give Gray a veto
it was not granted.

**Gray says what it concluded.** Before Gray closes it records whether the
structure holds, is compromised, or could not be assessed, with a reason. If it
closes without saying, the record says it could not assess rather than leaving a
blank. This matters because the disagreement check used to read Gray's silence
as agreement, which treated "looked and found nothing wrong" and "did not look"
as the same state. They are not.

**Green has to say where the analogy fails.** A grounding that only says where
the comparison holds is incomplete and gets rejected. Green also has to declare
whether an analogy is new or a repeat of one already used in this session, and
the harness checks that claim against the session's history. Using the same
comparison twice does not establish the point twice.

**42 runs a gate before anything is called an insight.** Five checks in order:
is it already stated, is it just a rename, is it an abstraction of something
that already exists, does it identify a genuinely new relationship, and does it
actually matter. Failing any of them ends the gate and produces "no 42
identified," with a record of which check failed. Being an abstraction is not a
failure, but it changes the label the result carries, so an abstraction cannot
be presented as a discovery.

"No 42 identified" is a complete and correct answer. The harness will produce it
by default rather than let the format pressure a reviewer into inventing
something.

**Verdicts are declared, then checked.** The reviewer states the verdict. The
harness only asks whether the record can carry it. Declaring failure with no
blocking findings is rejected. Declaring everything clear while blocking
findings sit on the record is rejected. If Red raised blocking findings while
Gray found nothing structurally wrong and Green established grounding, the
default is to route the disagreement to a human, and overriding that requires a
written reason.

## What comes out

Every pass produces a full record: the labelled inputs, every finding with its
severity, every examination and what it concluded, every grounding with its
break statement, the 42 gate result, and the verdict with its reason.

The record exports one way, to JSON. It does not load back in. That is
intentional. A pass is a historical event, and rehydrating one so it could be
edited would make the history rewritable, which defeats the point of keeping it.

## Running it

`python3 example_pass.py` runs a complete worked pass, including a verdict that
gets rejected and then corrected.

`python3 example_cross_cutting.py` runs two-phase Gray against the three real
defects found in v2.0.0, showing why Red's clustering cannot connect them and
Gray can.

`python3 -m pytest tests/` runs the suite. Every rule above has tests for both
the accepted and the rejected case.

No dependencies outside the standard library. Python 3.11 or newer. CCC is an
optional install, needed only to hand output off (below).

## Origin, promotion, and erasure belong to CCC

Earlier versions of this harness kept their own record of who originated each
claim, allowed a claim to be promoted to fact with a human authorization, and
handled erasure. As of 3.0.0 all of that is gone from Triad+42, on purpose.

A review tool that can certify facts is the authority creep the framework is
meant to prevent, and two separate copies of the same origin rules drift apart.
CCC (the Cognitive Continuity Constitution) is now the single owner of those
rules. The removed code is preserved in the Graveyard repository under
`triad-42/2026-10-06-origin-rules`.

What that leaves Triad+42 with is a clean division of labor: the Triad thinks,
CCC remembers and guards, humans decide.

## Handing output to CCC

`triad42.ccc_handoff.hand_off(session, ccc_system)` records every candidate from
a session into CCC. What it guarantees is fixed, not configurable:

- **Always machine-originated, under one identity.** Every record arrives in CCC
  from the model actor `triad42`. There is no actor parameter, so Triad+42
  output can neither arrive as human-originated nor borrow a human-looking name.
- **A real CCC only.** The target must be a CCC system. Handing output to
  anything else is refused rather than counted as delivered.
- **Nothing dropped.** Candidates never shown to the human go across with their
  not-surfaced status and the reason, so "what did you not show me" still has an
  answer after the session ends. A pass that was started but never harvested
  blocks the handoff, since its output would otherwise go missing unnoticed.
- **Never twice, and erasure sticks.** What counts as already delivered is
  decided by what the target CCC holds for this session, including material a
  human erased. Handing off again never duplicates output and never brings
  erased material back.
- **No silent skip.** If CCC is not installed and you ask for a handoff, it
  raises. A handoff that quietly did nothing would look like one that worked.

Install CCC with `pip install -e ".[ccc]"`. CI installs it and fails, rather
than skips, if the handoff tests cannot run.

Where Triad+42 output feeds a governed decision inside ≡TACK, the rule is "no
CCC record, no use": the integration point refuses output that was not handed
off. That check lives at the integration point, not here, so Triad+42 still runs
on its own for plain review work.

## The retrieval right

Everything a pass detects goes into the session's candidate store, whether or
not it was shown. Not surfacing something is a presentation decision and never a deletion,
so every candidate stays queryable by kind, scope, pass, and surfacing status,
along with the stated reason it was or was not shown.

Insights that fail the 42 gate are kept too. A rejected insight is still a
detected one, and the record of which check it failed is worth more later than
the insight would have been.

The store is append-only for the life of the session. There is no delete. It
is working memory, not the durable record: the durable copy, and the human's
right to erase it, live in CCC after a handoff. Keeping a long-lived copy here
instead would create a shadow record that an erasure in CCC could not reach.

## The reasoning layer is deliberately empty

An automated Red, Gray, and Green would make this a system that performs reviews
rather than one that governs them. The interfaces for that are written down and
nothing implements them.

The reason is not effort. If all three lenses are the same model wearing three
sets of instructions, there is currently no stated way to demonstrate they stayed
distinct, and three prompts that quietly collapse into one reviewer would produce
output that looks like a Triad without being one.

There is a second reason. Severity is what gates a failing verdict, so anything
that assigns severity holds veto power. The Red interface therefore returns
findings without severity, and four questions are written into that module that
have to be answered before anything fills the slot.

## Records are write-once

Ledgers seal when their stage closes, so nothing can be added to Red after Red
is done. Verdicts can be declared once. Every record carries the time it was
created, and a verdict carries the time it was declared.

None of this was true in 2.0.0. All of it came out of an adversarial pass that
found six ways to get around the rules, which are now regression tests.

## What is still open

Eight design questions were answered with defaults rather than decisions. They
are written up in `DECISIONS_PENDING.md` with the alternatives that were
considered. None of them should be treated as settled.

## Operational upgrades

Three non-authoritative facilities are available:

- `triad42.integrity` creates SHA-256 manifests for canonical exported
  representations. A digest attests only to content identity, not truth,
  provenance, or epistemic status.
- `triad42.telemetry` collects read-only pass counters for operations. The
  counters are never consulted by stage, severity, verdict, or novelty logic.
- `triad42.observations` detects surface linguistic patterns while preserving
  the exact original text. Signals are reviewer metadata only; they do not
  rewrite claims or determine their status.

These facilities are isolated from the constitutional decision path. They are
observability and boundary conveniences, not reasoning engines.
