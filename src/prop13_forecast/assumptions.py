"""Model inputs: one triangular (low, mode, high) range per row, each with a status and source.

Same contract as the Ontario model: status is `official` (a published figure), `design`
(a choice in the proposal) or `assumption` (a team placeholder to be replaced with data).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

STATUSES = ("official", "design", "assumption")


@dataclass(frozen=True)
class Assumption:
    key: str
    label: str
    alternative: str
    description: str
    low: float
    mode: float
    high: float
    unit: str
    status: str
    source: str

    def draw(self, n: int, rng: np.random.Generator) -> np.ndarray:
        if self.low == self.high:
            return np.full(n, self.mode)
        return rng.triangular(self.low, self.mode, self.high, n)

    def fixed(self, value: float | None = None) -> Assumption:
        """Collapse to a single value (mode by default), for deterministic runs."""
        v = self.mode if value is None else value
        return replace(self, low=v, mode=v, high=v)


def load_assumptions(path: Path) -> dict[str, Assumption]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for r in rows:
        a = Assumption(
            r["key"],
            r["label"],
            r["alternative"],
            r["description"],
            float(r["low"]),
            float(r["mode"]),
            float(r["high"]),
            r["unit"],
            r["status"],
            r["source"],
        )
        if not a.low <= a.mode <= a.high:
            raise ValueError(f"{a.key}: need low <= mode <= high")
        if a.status not in STATUSES:
            raise ValueError(f"{a.key}: status must be one of {STATUSES}")
        if not a.source.strip():
            raise ValueError(f"{a.key}: every input needs a source")
        out[a.key] = a
    return out


def override(a: Assumption, low: float, mode: float, high: float, status: str, source: str) -> Assumption:
    """Replace a placeholder with a data-derived value (data takes precedence)."""
    return replace(a, low=low, mode=mode, high=high, status=status, source=source)
