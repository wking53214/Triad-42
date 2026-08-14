"""Chain A, Chain B, human roots, and the erasure cascade.

Run with: python3 example_provenance.py
"""

from triad42 import (
    Authorization,
    EpistemicViolation,
    Label,
    LabeledItem,
    Origin,
    ProvenanceGraph,
)


def main() -> None:
    g = ProvenanceGraph()

    stated = g.register(
        LabeledItem("I ran the migration on staging and it completed.", Label.FACT),
        Origin.USER_ESTABLISHED,
    )
    guessed = g.register(
        LabeledItem("The migration is safe for production.", Label.INFERENCE),
        Origin.MACHINE_DERIVED,
    )
    stacked = g.register(
        LabeledItem("No rollback plan is needed.", Label.INFERENCE),
        Origin.MACHINE_DERIVED,
    )

    print("Chain A, who originated each claim:")
    for i in (stated, guessed, stacked):
        print(f"  {g.origin_of(i.item_id).value:<20} {i.text}")

    print("\nBefore any support is asserted:")
    t = g.trace(guessed.item_id)
    print(f"  reaches a human root: {t.reaches_human_root}")
    try:
        g.promote_to_fact(guessed.item_id, Authorization("William", "seems right"))
    except EpistemicViolation as exc:
        print(f"  promotion refused: {str(exc)[:70]}...")

    g.add_support(stated.item_id, guessed.item_id,
                  "A completed staging run is the observation the claim rests on.")
    g.add_support(guessed.item_id, stacked.item_id,
                  "Safety is the premise the rollback conclusion depends on.")

    print("\nAfter Chain B links are asserted:")
    t = g.trace(stacked.item_id)
    print(f"  reaches a human root: {t.reaches_human_root}")
    print(f"  machine steps in the chain: {t.machine_steps}")

    g.promote_to_fact(guessed.item_id, Authorization("William", "confirmed on staging"))
    g.promote_to_fact(stacked.item_id, Authorization("William", "accepted the reasoning"))
    print(f"  both promoted to: {guessed.label.value}, {stacked.label.value}")

    print("\nNow the human retracts the root:")
    event = g.erase(stated.item_id, "William", "The staging run was against the wrong DB.")
    for d in event.downgrades:
        print(f"  downgraded {d['from']} -> {d['to']}")
    print(f"  zombie evidence remaining: {g.zombie_check()}")


if __name__ == "__main__":
    main()
