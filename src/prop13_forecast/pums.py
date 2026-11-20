"""Renter's circuit breaker cost from Census ACS household microdata (PUMS).

Replaces the `eligible_renters` and `avg_credit` placeholders with values computed from real
California renter households only (the query is restricted to state FIPS 06). Needs a free
Census API key in CENSUS_API_KEY (https://api.census.gov/data/key_signup.html).

    python -m prop13_forecast.pums            # 2023 ACS 1-year, writes outputs/tables/

Credit per household (annual):
    excess  = max(0, gross rent - burden_threshold x income)
    credit  = min(credit_cap, credit_rate x excess), only if 0 < income <= income_limit
"""

from __future__ import annotations

import csv
import json
import os
import sys
import urllib.parse
import urllib.request

import numpy as np

from . import config

PUMS_URL = "https://api.census.gov/data/{year}/acs/acs1/pums"
# GRNTP: monthly gross rent; HINCP: household income; ADJINC: income inflation adjustment
# (x 1e-6); WGTP: household weight; TEN=3: rented; SPORDER=1: one record per household.
FIELDS = "SERIALNO,GRNTP,HINCP,ADJINC,WGTP"
STATE_FIPS = "06"  # California only: every household in the cost estimate is a CA renter


def credit(annual_rent, income, income_limit, burden_threshold, credit_rate, credit_cap) -> np.ndarray:
    rent = np.asarray(annual_rent, float)
    inc = np.asarray(income, float)
    excess = np.maximum(0.0, rent - burden_threshold * inc)
    c = np.minimum(credit_cap, credit_rate * excess)
    return np.where((inc > 0) & (inc <= income_limit), c, 0.0)


def summarize(annual_rent, income, weight, design: dict) -> dict:
    c = credit(annual_rent, income, **design)
    w = np.asarray(weight, float)
    eligible = c > 0
    hh = float(w[eligible].sum())
    total = float((c * w).sum())
    return {
        "renter_households": float(w.sum()),
        "eligible_households": hh,
        "avg_credit": total / hh if hh else 0.0,
        "total_cost_full_takeup": total,
        "share_at_cap": float(w[c >= design["credit_cap"]].sum() / hh) if hh else 0.0,
    }


def fetch(year: int = 2023, key: str | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    key = key or os.environ.get("CENSUS_API_KEY")
    if not key:
        raise RuntimeError("Set CENSUS_API_KEY (free at https://api.census.gov/data/key_signup.html)")
    params = {"get": FIELDS, "for": f"state:{STATE_FIPS}", "TEN": "3", "SPORDER": "1", "key": key}
    url = PUMS_URL.format(year=year) + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=300) as r:  # noqa: S310 (fixed https host)
        rows = json.load(r)
    head, body = rows[0], rows[1:]
    col = {name: i for i, name in enumerate(head)}

    def num(name: str) -> np.ndarray:
        return np.array([float(r[col[name]] or 0) for r in body])

    rent = num("GRNTP") * 12
    income = num("HINCP") * num("ADJINC") / 1e6
    return rent, income, num("WGTP")


def main(year: int = 2023) -> None:
    rent, income, weight = fetch(year)
    s = summarize(rent, income, weight, config.CIRCUIT_BREAKER)
    config.TABLES_DIR.mkdir(parents=True, exist_ok=True)
    path = config.TABLES_DIR / "pums_circuit_breaker.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerows([["acs_year", year], *[[k, v] for k, v in {**config.CIRCUIT_BREAKER, **s}.items()]])
    print(f"Wrote {path}")
    print(
        f"Set eligible_renters mode to {s['eligible_households']:,.0f} and avg_credit mode to "
        f"{s['avg_credit']:,.0f} in data/assumptions/assumptions.csv "
        f"(status official, source: U.S. Census Bureau ACS {year} 1-year PUMS)."
    )


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2023)
