# Prop 13 Alternatives: Outcome Projections

Projects what each policy alternative in the PPD 554 Group 3 analysis would add to the status quo
over FY 2027-28 to FY 2036-37, with low, likely and high ranges. Built on the design of the
Connecting Ontario forecast model (`~/sunstone`).

| Code | Alternative | Main outcome projected |
|---|---|---|
| A1 | Status quo | Baseline (zero by construction) |
| A2 | Proportional reassessment of company-owned property | New local property tax; state Prop 98 savings |
| A3 | Renter's circuit breaker | State cost; households helped |
| A4 | Housing growth allocation | State cost; City of LA revenue |
| A5 | A2 + A3 as linked bills | Credit funded within A2's savings; share of full credit funded |

> **Preliminary.** Most inputs are team placeholders marked `assumption` in
> `data/assumptions/assumptions.csv`. The ranking of alternatives is more reliable than the dollar
> amounts. [Sources](docs/sources.md) lists the data that replaces each placeholder.

## Quick start

```bash
uv sync --extra analysis --extra dev
uv run pytest
uv run python -m prop13_forecast.run
```

Outputs:

- `outputs/tables/summary.csv`: headline results (10th / 50th / 90th percentile)
- `outputs/tables/sensitivity.csv`: which input moves each result most
- `outputs/tables/inputs_used.csv`: every input with its status and source
- `outputs/charts/annual_outcomes.png`: annual ranges for A2-A5

To replace the circuit breaker placeholders with Census data (free key at
https://api.census.gov/data/key_signup.html):

```bash
CENSUS_API_KEY=your_key uv run python -m prop13_forecast.pums
```

## Layout

```
data/assumptions/assumptions.csv   every input: range, status, source
src/prop13_forecast/
  config.py        window, phase-in, circuit breaker design
  assumptions.py   loads and validates inputs
  model.py         formulas for A2-A5, summaries, sensitivity
  pums.py          circuit breaker cost from Census household microdata
  run.py           tables and charts
docs/methods.md    formulas and what is not modeled
docs/sources.md    data to replace each placeholder
```
