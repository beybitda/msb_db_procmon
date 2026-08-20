"""Small typed data holders passed between services and UI components."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KPIMetrics:
    total: int
    success: int
    failed: int
    running: int
    warning: int
    success_rate: float
    avg_duration_seconds: float | None
