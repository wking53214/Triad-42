import pytest

from triad42 import (
    CandidateKind,
    CandidateRecord,
    IntegrityManifest,
    Label,
    LabeledItem,
    Session,
    Severity,
    SurfacingStatus,
    content_digest,
    collect_pass_telemetry,
    manifest_for,
    observe_language,
)


def test_manifest_is_deterministic_and_detects_content_change():
    first = {"b": 2, "a": ["x", 1]}
    second = {"a": ["x", 1], "b": 2}
    manifest = manifest_for(first)

    assert manifest.digest == content_digest(second)
    assert manifest.verify(second)
    assert not manifest.verify({"a": ["x", 2], "b": 2})
    assert manifest.to_dict()["algorithm"] == "sha256"


def test_manifest_does_not_claim_epistemic_integrity():
    manifest = IntegrityManifest("0" * 64)
    assert set(manifest.to_dict()) == {
        "algorithm", "canonicalization", "digest", "previous_digest"
    }


def test_linguistic_observations_preserve_text_and_are_non_authoritative():
    text = "We should perhaps do this because it improves 25%."
    observation = observe_language(text)

    assert observation.original_text == text
    assert "first-person-framing-present" in observation.signals
    assert "uncertainty-language-present" in observation.signals
    assert "causal-language-present" in observation.signals
    assert "quantitative-claim-present" in observation.signals


def test_empty_linguistic_input_is_rejected():
    with pytest.raises(ValueError):
        observe_language(" ")


def test_telemetry_is_read_only_and_counts_recorded_process_data():
    session = Session()
    review_pass = session.start_pass(
        LabeledItem("Subject", Label.ASSUMPTION)
    )
    review_pass.add_finding("Finding", Severity.LOW, "scope")
    for _ in range(4):
        review_pass.close_stage()
    session.candidates.record(CandidateRecord(
        text="recorded", kind=CandidateKind.FINDING,
        status=SurfacingStatus.NOT_SURFACED, reason="not shown",
        pass_id=review_pass.pass_id,
    ))

    telemetry = collect_pass_telemetry(review_pass, session)
    assert telemetry.stages_closed == 4
    assert telemetry.findings == 1
    assert telemetry.retrieval_records == 1
    assert review_pass.verdict is None
