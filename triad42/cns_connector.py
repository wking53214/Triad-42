"""Optional connector to CNS (``cns.gate``): binding only.

Triad+42 is independent. It has no runtime dependency, imports nothing from CNS
when it loads, and its whole suite passes with CNS absent. This module is the
one place that knows CNS exists, and it asks for CNS only when a function that
needs it is called. Without CNS installed those calls raise
:class:`CnsNotInstalled` with the install command; nothing else in Triad+42 is
affected, and :func:`output_content` works without CNS at all.

What connecting means
---------------------
Triad output already reaches CNS through Link: for each candidate a session
surfaced, Link hands on its candidate id and text, and CNS's admission gate
(``cns_composition.ccc_admission``) binds its verdict to the source
``triad42``, that candidate id and the SHA-256 of the text, under the subject
``triad42:<candidate id>``. This module computes that same content and digest
from the Triad side, so a CNS verdict about one piece of review output can be
checked against exactly that output with ``GateResult.binds``.

That is all it does. Triad+42 is advisory, this module judges nothing, and
CNS judges nothing for Triad+42 here. So there is no gate in this module, no
verdict mapping and no chain. Whether an output may be used is CNS's question
at its own door, and this module does not answer it.

What is bound
-------------
:func:`output_content` is one surfaced ``CandidateRecord``, as Link hands it
on: ``source`` (always ``triad42``), ``candidate_id``, and ``text_digest``, the
full SHA-256 hex of the UTF-8 text, which is the fingerprint the CCC handoff
and CCC both record. The text itself is not copied. The kind, reason, pass id,
scope, source id and recorded time do not travel to CNS and are not bound.

A candidate that was not surfaced is refused: it is an audit record, not review
output, and Link never offers it to CNS.

Install with the extra: ``pip install -e ".[cns]"``.
"""

from __future__ import annotations

import importlib
from types import ModuleType
from typing import Optional

from .ccc_handoff import SOURCE_TAG, _text_digest
from .retrieval import CandidateRecord, SurfacingStatus

__all__ = [
    "CnsNotInstalled",
    "SOURCE",
    "binds",
    "cns_available",
    "output_content",
    "output_digest",
    "subject_for",
]

INSTALL_HINT = 'pip install -e ".[cns]"'

#: The source every bound Triad output names, and the prefix of its subject label.
SOURCE = SOURCE_TAG


class CnsNotInstalled(ImportError):
    """Raised by this module's functions when ``cns`` cannot be imported."""


def _cns_gate() -> ModuleType:
    """Import ``cns.gate`` on demand, or say exactly what is missing."""
    try:
        return importlib.import_module("cns.gate")
    except ImportError as exc:
        raise CnsNotInstalled(
            "triad42.cns_connector needs the CNS package (cns.gate), which is not "
            f"installed. Install it with: {INSTALL_HINT}. Triad+42 itself works "
            "without it."
        ) from exc


def cns_available() -> bool:
    """Whether the CNS gate contract can be imported in this environment."""
    try:
        _cns_gate()
    except CnsNotInstalled:
        return False
    return True


def _require(candidate: object) -> CandidateRecord:
    if not isinstance(candidate, CandidateRecord):
        raise TypeError(f"a triad42 CandidateRecord is expected here; got {type(candidate).__name__}")
    if candidate.status is not SurfacingStatus.SURFACED:
        raise ValueError(
            f"candidate {candidate.candidate_id!r} was not surfaced; it is not review "
            "output and is never handed to CNS"
        )
    for name in ("candidate_id", "text"):
        value = getattr(candidate, name)
        if not isinstance(value, str) or not value:
            raise TypeError(f"CandidateRecord.{name} must be a non-empty string to be bound")
    return candidate


def subject_for(candidate: CandidateRecord) -> str:
    """The subject label a verdict on ``candidate`` carries: ``triad42:<candidate id>``."""
    return f"{SOURCE}:{_require(candidate).candidate_id}"


def output_content(candidate: CandidateRecord) -> dict:
    """The content a verdict on ``candidate`` is bound to (plain data, no CNS needed)."""
    _require(candidate)
    return {
        "source": SOURCE,
        "candidate_id": candidate.candidate_id,
        "text_digest": _text_digest(candidate.text),
    }


def output_digest(candidate: CandidateRecord) -> str:
    """The digest a verdict bound to ``candidate`` carries, with :func:`subject_for`."""
    content = output_content(candidate)
    return _cns_gate().subject_digest(content)


def binds(result: object, candidate: CandidateRecord, *, subject: Optional[str] = None) -> bool:
    """Whether ``result`` is a CNS verdict issued against exactly ``candidate``.

    ``subject`` defaults to :func:`subject_for` the candidate. An unbound or
    hand-built result, anything that is not a ``cns.gate.GateResult``, a
    different subject label, or a verdict about different content is ``False``.
    """
    computed = output_digest(candidate)
    label = subject_for(candidate) if subject is None else subject
    if not isinstance(result, _cns_gate().GateResult):
        return False
    return bool(result.binds(label, computed))
