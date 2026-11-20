"""Paths, projection window and the proposed policy design."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSUMPTIONS = ROOT / "data" / "assumptions" / "assumptions.csv"
RAW_DIR = ROOT / "data" / "raw"
TABLES_DIR = ROOT / "outputs" / "tables"
CHARTS_DIR = ROOT / "outputs" / "charts"

# Fiscal years projected (bills introduced in 2027 take effect in FY 2027-28 at the earliest).
FIRST_FY = 2028
LAST_FY = 2037
N_SIMS = 20_000
SEED = 554

# Phase-in: (first FY with any effect, first FY at full scale).
PHASES = {
    "A2": (2028, 2028),  # reassessment applies to transfers after the effective date
    "A3": (2028, 2029),  # credit phases in over two years
    "A4": (2028, 2028),  # homes completed from FY 2027-28 on
}

# Renter's circuit breaker design (the outline's example values). These are policy choices,
# not uncertain inputs, so they live here rather than in the assumptions file.
CIRCUIT_BREAKER = {
    "income_limit": 70_000,  # household income ceiling, USD/yr
    "burden_threshold": 0.30,  # rent above this share of income counts as excess
    "credit_rate": 0.20,  # share of the excess rent credited
    "credit_cap": 1_800,  # maximum credit, USD/yr
}

# Housing growth allocation: each completed home earns the extra share for this many years.
ALLOCATION_YEARS = 10
