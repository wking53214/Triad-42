"""Binding Triad output to CNS verdicts: the content, its digest, and ``binds``.

These skip where ``cns`` is not installed. CI installs the extra and sets
TRIAD42_REQUIRE_CNS=1, so there they cannot skip. The connector is binding
only: nothing here judges a review output.
"""
import dataclasses
import hashlib
import json
import os
import sys

import pytest

if os.environ.get("TRIAD42_REQUIRE_CNS") == "1":  # CI: a missing cns is a failure, not a skip
    import cns.gate as gate
else:
    gate = pytest.importorskip("cns.gate", reason="CNS is not installed")

from cns_composition import ccc_admission  # noqa: E402  (ships in the same cns wheel)

from triad42 import (  # noqa: E402
    CandidateKind, CandidateRecord, Label, LabeledItem, Session, Severity, SurfacingStatus,
)
from triad42.ccc_handoff import SOURCE_TAG  # noqa: E402
from triad42.cns_connector import (  # noqa: E402
    SOURCE, CnsNotInstalled, binds, cns_available, output_content, output_digest, subject_for,
)

TEXT = "Step 3 has no rollback."


def make_session() -> Session:
    """A session harvested by Triad's own functions: two surfaced findings, one not."""
    session = Session()
    rp = session.start_pass(LabeledItem("The plan as written.", Label.ASSUMPTION))
    shown = rp.add_finding(TEXT, Severity.HIGH, scope="plan")
    also = rp.add_finding("Nothing checks the backup.", Severity.MEDIUM, scope="ops")
    rp.add_finding("Naming is inconsistent.", Severity.LOW, scope="docs")
    session.harvest(rp, surfaced_ids={shown.finding_id, also.finding_id})
    return session


def surfaced(session: Session) -> list[CandidateRecord]:
    """What Link hands on: exactly the candidates whose status is SURFACED."""
    return [c for c in session.candidates.all() if c.status is SurfacingStatus.SURFACED]


def make_output(**overrides) -> CandidateRecord:
    fields = dict(text=TEXT, kind=CandidateKind.FINDING, status=SurfacingStatus.SURFACED,
                  reason="Presented to the human.", pass_id="p-1", scope="plan", source_id="f-1",
                  candidate_id="c-1", recorded_at="2026-01-01T00:00:00+00:00")
    fields.update(overrides)
    return CandidateRecord(**fields)


def result_for(content_digest, subject, outcome=None):
    return gate.GateResult(
        gate="other.repo.gate", position=gate.GatePosition.ALPHA,
        outcome=outcome or gate.GateOutcome.PASS, reason="r", subject=subject, subject_digest=content_digest)


# ------------------------------------------------------------ determinism

def test_the_same_output_gives_the_same_content_and_digest():
    one, two = make_output(), make_output()
    assert one is not two
    assert output_content(one) == output_content(two)
    assert output_digest(one) == output_digest(two)


def test_digest_is_a_full_sha256_hex_and_repeatable():
    output = make_output()
    digest = output_digest(output)
    assert len(digest) == 64 and int(digest, 16) >= 0
    assert digest == output_digest(output)


# ------------------------------------------------------------ what is bound

def test_the_content_is_source_candidate_id_and_the_full_text_digest():
    content = output_content(make_output())
    assert content == {
        "source": "triad42",
        "candidate_id": "c-1",
        "text_digest": hashlib.sha256(TEXT.encode("utf-8")).hexdigest(),
    }
    assert SOURCE == SOURCE_TAG == ccc_admission.SOURCE == "triad42"
    assert TEXT not in json.dumps(content)


CHANGES = {
    "candidate id": dict(candidate_id="c-2"),
    "text": dict(text="Step 4 has no rollback."),
    "text, one character": dict(text=TEXT.replace("rollback", "rollbacK")),
    "text, trailing space": dict(text=TEXT + " "),
}


@pytest.mark.parametrize("name", list(CHANGES))
def test_the_digest_changes_when_any_bound_field_changes(name):
    output = make_output()
    changed = make_output(**CHANGES[name])
    assert output_content(changed) != output_content(output)
    assert output_digest(changed) != output_digest(output)


def test_the_bound_fields_are_exactly_what_link_hands_on():
    assert {key for change in CHANGES.values() for key in change} == {"candidate_id", "text"}
    assert {f.name for f in dataclasses.fields(ccc_admission.TriadOutput)} == {"candidate_id", "text"}


# ------------------------------------------------------------ what is not bound

@pytest.mark.parametrize("fields", [
    dict(kind=CandidateKind.OBSERVATION), dict(reason="Shown later."), dict(pass_id="p-2"),
    dict(scope="ops"), dict(source_id=None), dict(recorded_at="2027-01-01T00:00:00+00:00"),
])
def test_fields_that_do_not_travel_to_cns_are_not_bound(fields):
    assert output_digest(make_output(**fields)) == output_digest(make_output())


# ------------------------------------------------------------ types

@pytest.mark.parametrize("bad", [None, TEXT, {"candidate_id": "c-1", "text": TEXT}, 7,
                                 ccc_admission.TriadOutput(candidate_id="c-1", text=TEXT)])
def test_anything_that_is_not_a_candidate_record_is_refused(bad):
    for function in (output_content, output_digest, subject_for, lambda c: binds(None, c)):
        with pytest.raises(TypeError):
            function(bad)


def test_a_candidate_that_was_not_surfaced_is_not_review_output():
    hidden = make_output(status=SurfacingStatus.NOT_SURFACED)
    for function in (output_content, output_digest, subject_for, lambda c: binds(None, c)):
        with pytest.raises(ValueError):
            function(hidden)


@pytest.mark.parametrize("field,value", [("candidate_id", ""), ("candidate_id", 7), ("text", ""), ("text", None)])
def test_an_empty_or_non_string_id_or_text_is_refused(field, value):
    output = make_output()
    setattr(output, field, value)   # CandidateRecord is not frozen
    with pytest.raises(TypeError):
        output_content(output)


# ------------------------------------------------------------ binds

def test_subject_is_the_source_and_the_candidate_id():
    assert subject_for(make_output()) == "triad42:c-1"


def test_binds_is_true_for_the_output_it_was_issued_against():
    output = make_output()
    result = result_for(output_digest(output), subject_for(output))
    assert result.bound() and binds(result, output)


def test_binds_is_false_for_another_digest():
    output = make_output()
    for other in (make_output(text="Other."), make_output(candidate_id="c-2")):
        assert not binds(result_for(output_digest(other), subject_for(output)), output)
    assert not binds(result_for("0" * 64, subject_for(output)), output)


@pytest.mark.parametrize("label", ["", "triad42", "triad42:c-2", "triad42.c-1", "something.else"])
def test_binds_is_false_for_another_subject(label):
    output = make_output()
    assert not binds(result_for(output_digest(output), label), output)


def test_binds_uses_the_subject_it_is_given_and_not_the_default_one():
    output = make_output()
    labelled = result_for(output_digest(output), "custom.label")
    assert binds(labelled, output, subject="custom.label")
    assert not binds(labelled, output)
    assert not binds(result_for(output_digest(output), subject_for(output)), output, subject="custom.label")


def test_an_unbound_or_hand_built_result_binds_to_nothing():
    output = make_output()
    bare = gate.GateResult(gate="g", position=gate.GatePosition.ALPHA, outcome=gate.GateOutcome.PASS)
    assert not bare.bound() and not binds(bare, output)
    assert not binds(bare, output, subject="")
    no_digest = gate.GateResult(gate="g", position=gate.GatePosition.ALPHA, outcome=gate.GateOutcome.PASS,
                                subject=subject_for(output))
    assert not binds(no_digest, output)
    no_subject = gate.GateResult(gate="g", position=gate.GatePosition.ALPHA, outcome=gate.GateOutcome.PASS,
                                 subject_digest=output_digest(output))
    assert not binds(no_subject, output)


@pytest.mark.parametrize("impostor", [None, "pass", {"subject": "triad42:c-1"}, object()])
def test_something_that_is_not_a_gate_result_binds_to_nothing(impostor):
    assert binds(impostor, make_output()) is False


def test_an_impostor_that_claims_to_bind_is_not_believed():
    class Liar:
        def binds(self, subject, digest):
            return True

    assert binds(Liar(), make_output()) is False


@pytest.mark.parametrize("outcome", list(gate.GateOutcome))
def test_binding_does_not_depend_on_the_verdict(outcome):
    output = make_output()
    assert binds(result_for(output_digest(output), subject_for(output), outcome), output)


# ------------------------------------------------------------ against what CNS already issues

class Lookup:
    """Stands in for CCC's record lookup; CNS's gate asks it one question."""

    def __init__(self, answer):
        self.answer = answer

    def status(self, source, candidate_id, text_digest):
        return self.answer


@pytest.mark.parametrize("answer", ["held", "absent", "altered", "erased"])
def test_the_verdict_cns_admission_issues_on_a_session_binds_to_exactly_that_output(answer):
    session = make_session()
    outputs = surfaced(session)
    assert len(outputs) == 2 and len(session.candidates.all()) == 3
    door = ccc_admission.CccRecordGate(Lookup(answer))
    verdicts = [door.check(ccc_admission.TriadOutput(candidate_id=c.candidate_id, text=c.text)) for c in outputs]
    for verdict, output in zip(verdicts, outputs):
        assert verdict.subject == subject_for(output)
        assert verdict.subject_digest == output_digest(output)
        assert binds(verdict, output)
    assert not binds(verdicts[0], outputs[1]) and not binds(verdicts[1], outputs[0])
    edited = dataclasses.replace(outputs[0], text=outputs[0].text + " (edited)")
    assert not binds(verdicts[0], edited)


# ------------------------------------------------------------ cns missing

def test_without_cns_the_digest_and_binds_say_what_to_install(monkeypatch):
    monkeypatch.setitem(sys.modules, "cns.gate", None)   # any import of cns.gate now fails
    output = make_output()
    assert cns_available() is False
    assert output_content(output)["candidate_id"] == "c-1"   # plain data, no cns needed
    for call in (lambda: output_digest(output), lambda: binds(object(), output)):
        with pytest.raises(CnsNotInstalled, match=r'pip install -e "\.\[cns\]"') as raised:
            call()
        assert isinstance(raised.value, ImportError)
