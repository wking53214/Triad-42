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
reviews is still a recommendation. The only thing that can change a label is a
human authorization, and that authorization has to name who gave it and why.
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

`python3 example_provenance.py` runs the provenance side: origin, support links,
a promotion that gets refused for lack of a human root, and an erasure cascade
that leaves no zombie evidence.

`python3 -m pytest tests/` runs the suite. Every rule above has tests for both
the accepted and the rejected case.

No dependencies outside the standard library. Python 3.11 or newer.

## Provenance: two different questions

The harness asks two questions about every claim, and keeps them apart.

**Chain A asks who originated it.** User established, user accepted, assistant
proposed, machine derived, external source, or uncertain. This is separate from
the epistemic label, which says what kind of claim it is. A user can state an
assumption and a machine can produce an inference; origin does not change which
is which.

**Chain B asks whether the source actually backs the conclusion.** Support is an
explicit link with a stated reason, not something inferred from adjacency. A
statement can be authentically human and still fail to support the thing being
drawn from it. Human origin is not an evidentiary upgrade.

Keeping these apart closes a specific hole. Without it, "the user said something
related" starts functioning as proof.

## The human root requirement

Nothing reaches fact status on machine reasoning alone. A claim marked as fact
must have a support chain that terminates in human-originated material, and the
harness can walk that chain and answer why the claim exists, what backs it, how
many machine steps sit in between, and whether it terminates anywhere legitimate.

Three machine inferences supporting each other in sequence do not produce
evidence at the end. That chain is rejected regardless of length.

## Erasure and the cascade

The human can remove anything from their own record. The system has no veto. Its
job is to record the removal and follow the consequences.

When a root is erased, everything that rested on it is re-checked. Any fact that
can no longer reach a human root is downgraded, to inference if some support
survives and to unknown if none does. No claim keeps evidentiary status on ground
that has been removed.

Two details matter here.

The cascade only ever moves status downward. That is what keeps it consistent
with the rule that labels change only by human authorization: the erasure is the
authorizing act, and nothing is ever raised automatically.

A human decision is flagged, not downgraded. Erasing the analysis that informed a
choice does not unmake the choice. The record notes that the decision now stands
on removed ground and leaves the decision where the human put it.

## The retrieval right

Everything a pass detects goes into a candidate store, whether or not it was
shown. Not surfacing something is a presentation decision and never a deletion,
so every candidate stays queryable by kind, scope, pass, and surfacing status,
along with the stated reason it was or was not shown.

Insights that fail the 42 gate are kept too. A rejected insight is still a
detected one, and the record of which check it failed is worth more later than
the insight would have been.

The store is append-only. There is no delete.

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
