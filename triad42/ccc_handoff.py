"""Hand a session's output to CCC, the single owner of origin and memory.

Triad+42 is advisory. It holds no origin rules, cannot promote anything, and
keeps no durable memory. When a session's output has to outlive the session,
or is about to be used inside a governed decision path, it goes to CCC (the
Cognitive Continuity Constitution) through this module. CCC then enforces the
rules Triad+42 deliberately does not: who originated what, what may become
human-established, and the human's right to erase.

These properties are fixed here and cannot be configured away:

- Machine-originated, under one fixed identity. Every record arrives in CCC
  from the MODEL actor named `triad42`. There is no parameter at all for the
  actor, so Triad+42 output can neither arrive as human-originated nor borrow
  a human-looking name.
- A real CCC system only. The target must be a `ccc.CCCSystem`. Anything else
  is refused, so output cannot be "handed off" to a stand-in and then treated
  as delivered.
- Delivered means present in that system. Whether something was already
  handed off is decided by what the target CCC system holds for this session,
  not by a note kept on the Triad side. Handing the same session to a second
  CCC system records everything there.
- Erasure sticks. An artifact a human erased in CCC still counts as delivered,
  so handing the session off again never brings erased material back.
- Nothing dropped. Candidates never shown to the human go across with their
  NOT_SURFACED status and the stated reason. A pass that was started but never
  harvested is refused, because its output would otherwise be missing without
  anyone noticing.
- Never twice. The same piece of output (same pass, kind, source and text) is
  recorded once per target system, even if a pass was harvested more than once.
- No silent skip. CCC is an optional install, but if `hand_off` is called and
  CCC is not importable, it raises. A handoff that quietly did nothing would
  look exactly like one that succeeded.
- Stamped when asked. Given an `attestation_key`, every record carries an HMAC
  stamp (`ccc.record_status.attest`) that CCC's record lookup checks, so a
  record anyone else wrote under the Triad's name does not count as held. The
  key is the caller's: there is no default, and nothing here stores it. A
  session whose earlier records in the target have no valid stamp is refused,
  not skipped, because those records could never be counted.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

from .review import Session

#: The one identity every CCC artifact created here carries.
SOURCE_TAG = "triad42"

#: Stated reason recorded with every artifact. CCC writes it to its audit trail.
HANDOFF_REASON = "Triad+42 review output: advisory, machine-originated, not ratified"


def _ccc() -> tuple[Any, Any, Any]:
    try:
        from ccc import Actor, CCCSystem, EpistemicStatus
    except ImportError as exc:
        raise ImportError(
            "hand_off requires the CCC package (cognitive-continuity-constitution). "
            "Install it, or do not hand off: Triad+42 never skips a requested "
            "handoff silently."
        ) from exc
    return Actor, CCCSystem, EpistemicStatus


def _attest() -> Any:
    try:
        from ccc.record_status import attest
    except ImportError as exc:
        raise ImportError(
            "an attestation_key needs a CCC that can stamp records (ccc.record_status.attest). "
            "Upgrade CCC, or hand off without a key; Triad+42 never stamps nothing silently."
        ) from exc
    return attest


def _text_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _key(pass_id: Any, kind: Any, source_id: Any, digest: str) -> tuple[Any, ...]:
    return (pass_id, kind, source_id, digest)


def hand_off(session: Session, system: Any, *, attestation_key: bytes | None = None) -> dict[str, str]:
    """Record every candidate in `session` not already in `system`.

    With `attestation_key`, each record is stamped so CCC's lookup can tell it from one written by anyone else.
    Raises ValueError, recording nothing, if this session already has a record in `system` that carries no valid
    stamp under that key.

    "Already in" is decided by what the target CCC system actually holds for
    this session, in any state, including erased. Returns a mapping of
    candidate id to CCC artifact id for the candidates recorded by this call.
    `session.handed_off` keeps the mapping for the most recent target.
    """
    Actor, CCCSystem, EpistemicStatus = _ccc()
    if not isinstance(system, CCCSystem):
        raise TypeError(
            "hand_off target must be a ccc.CCCSystem; got "
            f"{type(system).__name__}. Output handed to anything else is not "
            "in CCC's record."
        )
    unharvested = [p.pass_id for p in session.passes if p.pass_id not in session.harvested_passes]
    if unharvested:
        raise ValueError(
            "Refusing to hand off: these passes were never harvested, so their "
            f"output would be missing from CCC: {unharvested}. Call "
            "session.harvest(pass) first."
        )

    attest = _attest() if attestation_key is not None else None

    # What this CCC system already holds from this session. Erased artifacts
    # count: their text is gone but their metadata stays, and re-recording
    # them would undo the human's erasure.
    held_ids: dict[str, str] = {}
    held_keys: dict[tuple[Any, ...], str] = {}
    unstamped: list[str] = []
    for artifact in system.store.artifacts.values():
        meta = artifact.metadata or {}
        if meta.get("source") != SOURCE_TAG or meta.get("session_id") != session.session_id:
            continue
        if attest is not None and artifact.content is not None:
            want = attest(attestation_key, source=SOURCE_TAG, candidate_id=str(meta.get("candidate_id")),
                          text_digest=_text_digest(artifact.content))
            stamp = meta.get("attestation")
            if not (isinstance(stamp, str) and hmac.compare_digest(stamp, want)):
                unstamped.append(artifact.artifact_id)
        held_ids[meta.get("candidate_id")] = artifact.artifact_id
        held_keys[_key(meta.get("pass_id"), meta.get("candidate_kind"),
                       meta.get("source_id"), meta.get("text_digest"))] = artifact.artifact_id

    if unstamped:
        raise ValueError(
            "Refusing to hand off: this session already has record(s) in the target that carry no valid "
            f"attestation under this key, so CCC's lookup could never count them: {sorted(unstamped)}. Hand "
            "the session to a fresh CCC system, or hand off without a key."
        )

    actor = Actor.model(SOURCE_TAG)
    recorded: dict[str, str] = {}
    for candidate in session.candidates.all():
        digest = _text_digest(candidate.text)
        key = _key(candidate.pass_id, candidate.kind.value, candidate.source_id, digest)
        existing = held_ids.get(candidate.candidate_id) or held_keys.get(key)
        if existing is not None:
            session.handed_off[candidate.candidate_id] = existing
            continue
        metadata = {
            "source": SOURCE_TAG,
            "session_id": session.session_id,
            "pass_id": candidate.pass_id,
            "candidate_id": candidate.candidate_id,
            "candidate_kind": candidate.kind.value,
            "surfacing_status": candidate.status.value,
            "surfacing_reason": candidate.reason,
            "scope": candidate.scope,
            "source_id": candidate.source_id,
            "text_digest": digest,
            "recorded_at": candidate.recorded_at,
        }
        if attest is not None:
            metadata["attestation"] = attest(attestation_key, source=SOURCE_TAG,
                                             candidate_id=candidate.candidate_id, text_digest=digest)
        artifact = system.ingest(
            candidate.text,
            actor=actor,
            epistemic_status=EpistemicStatus.INFERENCE,
            topics=(SOURCE_TAG, candidate.kind.value),
            reason=HANDOFF_REASON,
            metadata=metadata,
        )
        held_ids[candidate.candidate_id] = artifact.artifact_id
        held_keys[key] = artifact.artifact_id
        session.handed_off[candidate.candidate_id] = artifact.artifact_id
        recorded[candidate.candidate_id] = artifact.artifact_id
    return recorded


__all__ = ["HANDOFF_REASON", "SOURCE_TAG", "hand_off"]
