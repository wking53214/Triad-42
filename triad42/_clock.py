"""Timestamps.

Every record carries the moment it was created. A review record without a
time cannot take its place in a lineage, and lineage is the point.
"""

from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> str:
    """Current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()
