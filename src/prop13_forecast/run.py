"""Run the projection: summary table, sensitivity table and charts.

    python -m prop13_forecast.run
"""

from __future__ import annotations

import csv

import numpy as np

from . import config
from .assumptions import load_assumptions
from .model import ALTERNATIVES, simulate, summarize, tornado

TORNADO_SERIES = {
    "A2": "A2_local_revenue",
    "A3": "A3_state_cost",
    "A4": "A4_state_cost",
    "A5": "A5_credit_paid",
}


def _write(path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def _charts(res, years) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed: skipping charts (uv sync --extra analysis)")
        return
    panels = [
        ("A2_local_revenue", "A2 new local property tax"),
        ("A3_state_cost", "A3 circuit breaker state cost"),
        ("A4_state_cost", "A4 housing growth allocation state cost"),
        ("A5_credit_paid", "A5 credit paid within savings cap"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True)
    for ax, (key, title) in zip(axes.flat, panels, strict=True):
        p10, p50, p90 = np.quantile(res.series[key] / 1e6, [0.1, 0.5, 0.9], axis=0)
        ax.fill_between(years, p10, p90, alpha=0.25, label="10th–90th percentile")
        ax.plot(years, p50, lw=2, label="Median")
        ax.set_title(title, fontsize=10)
        ax.set_ylabel("$ millions per year (real)")
        ax.grid(alpha=0.3)
    axes.flat[0].legend(fontsize=8)
    fig.suptitle("Projected annual outcomes by alternative (increment over the status quo)")
    fig.tight_layout()
    config.CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.CHARTS_DIR / "annual_outcomes.png", dpi=150)
    print(f"Wrote {config.CHARTS_DIR / 'annual_outcomes.png'}")


def main() -> None:
    A = load_assumptions(config.ASSUMPTIONS)
    years = np.arange(config.FIRST_FY, config.LAST_FY + 1)
    res = simulate(A, years, config.N_SIMS, np.random.default_rng(config.SEED))

    summary = summarize(res)
    _write(config.TABLES_DIR / "summary.csv", summary)

    rows = []
    for alt, series in TORNADO_SERIES.items():
        for key, lo, hi, base in tornado(A, years, series):
            rows.append({"alternative": alt, "series": series, "input": key, "at_low": lo, "at_high": hi,
                         "at_mode": base, "status": A[key].status})
    _write(config.TABLES_DIR / "sensitivity.csv", rows)

    _write(config.TABLES_DIR / "inputs_used.csv", [
        {"key": a.key, "low": a.low, "mode": a.mode, "high": a.high, "unit": a.unit, "status": a.status,
         "source": a.source} for a in A.values()
    ])
    _charts(res, years)

    print(f"\nFY {config.FIRST_FY}-{config.LAST_FY}, {config.N_SIMS:,} simulations (real FY 2026-27 $)")
    print(f"{ALTERNATIVES['A1']}: baseline (all outcomes are increments over it)")
    for r in summary:
        fmt = "{:,.2f}" if "share" in r["metric"] else "{:,.0f}"
        print(f"  {r['metric']:<58} " + " / ".join(fmt.format(r[k]) for k in ("p10", "p50", "p90")))
    n_placeholder = sum(a.status == "assumption" for a in A.values())
    print(f"\n{n_placeholder} of {len(A)} inputs are still team assumptions (see inputs_used.csv).")


if __name__ == "__main__":
    main()
