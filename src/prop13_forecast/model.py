"""What each alternative adds on top of the status quo, simulated jointly over input ranges.

Status quo (A1) is the baseline: every outcome below is an increment over it, so A1 is zero
by construction. Each arrow is a row in data/assumptions/assumptions.csv.

  A2 Proportional reassessment   entity-held value not yet reassessed x untaxed turnover
                                 -> newly reassessed value x market-to-assessed gap x 1%
                                 -> new local property tax (accumulates as cohorts build up).
                                 State savings = new tax x school share x Prop 98 offset.
  A3 Renter's circuit breaker    eligible renter households x take-up x average credit
                                 (growing with real rents) -> state cost; households helped.
  A4 Housing growth allocation   net new homes x assessed value x 0.1%, for 10 years per
                                 cohort -> city revenue = state cost (the state backfills
                                 schools); City of LA share shown separately.
  A5 Linked package              A3's credit capped at A2's certified state savings:
                                 credit paid = min(A3 cost, A2 state savings); coverage =
                                 credit paid / full A3 cost.

Outputs are in real (FY 2026-27) dollars. Not modeled (stated, not hidden): behavioral
responses (restructured deals under A2, rent increases capturing part of A3's credit), and any
housing-supply effect of A4 beyond the homes assumed to be completed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import config
from .assumptions import Assumption

ALTERNATIVES = {
    "A1": "Status quo",
    "A2": "Proportional reassessment",
    "A3": "Renter's circuit breaker",
    "A4": "Housing growth allocation",
    "A5": "Reassessment + circuit breaker (linked)",
}


def ramp(years: np.ndarray, start: int, full: int) -> np.ndarray:
    """Program scale by year: 0 before start, rising linearly to 1 at `full`."""
    y = np.asarray(years, float)
    if full <= start:
        return (y >= start).astype(float)
    return np.clip((y - start + 1) / (full - start + 1), 0.0, 1.0)


def cohort_sum(inflow: np.ndarray, growth: np.ndarray, life: int | None = None) -> np.ndarray:
    """Sum of past cohorts, each growing at `growth` per year and lasting `life` years.

    inflow: (n, T) amount added each year; growth: (n,) real growth rate per year.
    """
    n, t_len = inflow.shape
    out = np.zeros_like(inflow)
    for t in range(t_len):
        first = 0 if life is None else max(0, t - life + 1)
        ages = t - np.arange(first, t + 1)
        out[:, t] = (inflow[:, first : t + 1] * (1 + growth[:, None]) ** ages).sum(axis=1)
    return out


@dataclass
class Result:
    years: np.ndarray
    series: dict[str, np.ndarray] = field(default_factory=dict)  # each (n, T)


def simulate(A: dict[str, Assumption], years: np.ndarray, n: int, rng: np.random.Generator) -> Result:
    d = {k: a.draw(n, rng) for k, a in A.items()}
    t = np.arange(len(years))
    res = Result(years=years)

    # A2: the pool of entity value not yet reassessed shrinks as it turns over.
    on2 = ramp(years, *config.PHASES["A2"])
    rate = d["untaxed_transfer_rate"][:, None]
    newly_reassessed = d["entity_av"][:, None] * rate * (1 - rate) ** t * on2
    added_value = newly_reassessed * d["value_gap"][:, None]
    a2_revenue = cohort_sum(added_value, d["value_growth"]) * d["prop_tax_rate"][:, None]
    a2_savings = a2_revenue * (d["school_share"] * d["prop98_offset"])[:, None]
    res.series["A2_local_revenue"] = a2_revenue
    res.series["A2_state_savings"] = a2_savings

    # A3: full credit cost, growing with real rents.
    on3 = ramp(years, *config.PHASES["A3"])
    households = (d["eligible_renters"] * d["takeup"])[:, None] * on3
    credit = d["avg_credit"][:, None] * (1 + d["rent_growth"][:, None]) ** t
    a3_cost = households * credit
    res.series["A3_state_cost"] = a3_cost
    res.series["A3_households"] = households

    # A4: each year's homes earn the extra share for ALLOCATION_YEARS years.
    on4 = ramp(years, *config.PHASES["A4"])
    new_value = (d["net_new_units"] * d["new_unit_av"])[:, None] * on4
    a4_alloc = cohort_sum(new_value, d["value_growth"], config.ALLOCATION_YEARS) * d["extra_share"][:, None]
    res.series["A4_state_cost"] = a4_alloc
    res.series["A4_la_revenue"] = a4_alloc * d["la_unit_share"][:, None]

    # A5: the credit is capped at the state's certified savings from A2.
    a5_paid = np.minimum(a3_cost, a2_savings)
    res.series["A5_credit_paid"] = a5_paid
    res.series["A5_coverage"] = np.divide(a5_paid, a3_cost, out=np.zeros_like(a5_paid), where=a3_cost > 0)
    res.series["A5_local_revenue_net"] = a2_revenue  # localities keep all new property tax
    return res


# ---------------------------------------------------------------------------
# Summaries
# ---------------------------------------------------------------------------
# (series, how to summarize, label). "sum" = 10-year total; "last" = final-year value.
HEADLINES = [
    ("A2_local_revenue", "sum", "A2 new local property tax, 10-yr total ($)"),
    ("A2_local_revenue", "last", "A2 new local property tax, final year ($/yr)"),
    ("A2_state_savings", "sum", "A2 state Prop 98 savings, 10-yr total ($)"),
    ("A3_state_cost", "sum", "A3 state cost, 10-yr total ($)"),
    ("A3_state_cost", "last", "A3 state cost, final year ($/yr)"),
    ("A3_households", "last", "A3 households helped, final year"),
    ("A4_state_cost", "sum", "A4 state cost, 10-yr total ($)"),
    ("A4_la_revenue", "sum", "A4 City of LA revenue, 10-yr total ($)"),
    ("A5_credit_paid", "sum", "A5 credit paid within savings cap, 10-yr total ($)"),
    ("A5_coverage", "last", "A5 share of full credit funded, final year"),
]


def summarize(res: Result, q=(0.10, 0.50, 0.90)) -> list[dict]:
    out = []
    for key, how, label in HEADLINES:
        x = res.series[key]
        v = x.sum(axis=1) if how == "sum" else x[:, -1]
        p = np.quantile(v, q)
        out.append({"metric": label, "series": key, "summary": how, "p10": p[0], "p50": p[1], "p90": p[2]})
    return out


def tornado(
    A: dict[str, Assumption], years: np.ndarray, series: str
) -> list[tuple[str, float, float, float]]:
    """One-at-a-time sensitivity of a series' 10-year total (all inputs at mode, swing one).

    Returns (key, value_at_low, value_at_high, value_at_mode), largest swing first.
    """
    rng = np.random.default_rng(0)
    fixed = {k: a.fixed() for k, a in A.items()}

    def run(assump):
        return float(simulate(assump, years, 1, rng).series[series].sum())

    base = run(fixed)
    out = []
    for k, a in A.items():
        if a.low == a.high:
            continue
        lo, hi = run({**fixed, k: a.fixed(a.low)}), run({**fixed, k: a.fixed(a.high)})
        if lo != hi:
            out.append((k, lo, hi, base))
    return sorted(out, key=lambda r: -abs(r[2] - r[1]))
