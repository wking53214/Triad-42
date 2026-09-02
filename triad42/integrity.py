"""Content-integrity metadata for exported records.

Digests attest to a canonical byte representation only. They do not establish
truth, provenance, support quality, or epistemic status.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Optional


ALGORITHM = "sha256"
CANONICALIZATION = "json-sort-keys-utf8"


def canonical_bytes(record: Mapping[str, Any]) -> bytes:
    """Encode an export deterministically for content-integrity purposes."""
    return json.dumps(
        record, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def content_digest(record: Mapping[str, Any]) -> str:
    """Return the SHA-256 digest of a canonical exported representation."""
    return hashlib.sha256(canonical_bytes(record)).hexdigest()


@dataclass(frozen=True)
class IntegrityManifest:
    """A storage-boundary commitment to one exported representation."""

    digest: str
    algorithm: str = ALGORITHM
    canonicalization: str = CANONICALIZATION
    previous_digest: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "canonicalization": self.canonicalization,
            "digest": self.digest,
            "previous_digest": self.previous_digest,
        }

    def verify(self, record: Mapping[str, Any]) -> bool:
        """Check content identity; no epistemic conclusion is implied."""
        return (
            self.algorithm == ALGORITHM
            and self.canonicalization == CANONICALIZATION
            and self.digest == content_digest(record)
        )


def manifest_for(
    record: Mapping[str, Any], previous_digest: Optional[str] = None
) -> IntegrityManifest:
    """Create a content manifest, optionally linking an export sequence."""
    return IntegrityManifest(
        digest=content_digest(record),
        previous_digest=previous_digest,
    )
