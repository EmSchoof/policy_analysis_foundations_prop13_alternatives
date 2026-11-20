# Methods

[← README](../README.md) · [Sources →](sources.md)

## Approach

- **Status quo is the baseline.** Every number the model reports is what an alternative *adds*
  to the status quo, so the status quo itself is zero by construction.
- **Every input is a range with a source.** `data/assumptions/assumptions.csv` gives each input
  a low, likely (mode) and high value, a status (`official`, `design` or `assumption`) and a
  source. Team placeholders are marked `assumption` and listed when the model runs.
- **Ranges, not a single answer.** 20,000 simulations draw every input from its range at once
  (triangular distributions). Results are reported as 10th, 50th and 90th percentiles.
- **Simple formulas, not fitted models.** None of these policies exists yet in California, so
  outcomes are projected from explicit cause-and-effect formulas, not estimated from history.
- **Sensitivity.** Each input is swung from low to high with the others held at their likely
  value, to show which assumption matters most (`outputs/tables/sensitivity.csv`).

Window: FY 2027-28 through FY 2036-37, real FY 2026-27 dollars.

## Formulas

### A2 Proportional reassessment of company-owned property

```
newly reassessed value_t = entity value x untaxed turnover x (1 - untaxed turnover)^t
added taxable value_t    = newly reassessed value_t x market-to-assessed gap
new local property tax_t = 1% x sum of all past cohorts of added taxable value
state savings_t          = new local property tax_t x school share x Prop 98 offset
```

Proposition 98 (Prop 98) is California's minimum funding guarantee for K-14 schools; the offset is the
share of new school property tax that lowers the state's required General Fund spending.

The pool of not-yet-reassessed value shrinks as it turns over, so annual additions decline while
revenue accumulates. Calibration check: the California State Board of Equalization (BOE) estimated about $26 million a year for SB 259's
narrower 90% rule (California State Senate Committee on Appropriations, 2016). A proportional
rule should exceed that.

### A3 Renter's circuit breaker

```
credit per household = min(cap, 20% x max(0, annual rent - 30% x income)), if income <= limit
state cost_t         = eligible households x take-up x average credit x (1 + real rent growth)^t
```

`python -m prop13_forecast.pums` computes eligible households and the average credit from
California American Community Survey (ACS) household microdata, replacing the placeholders.

### A4 Housing growth allocation

```
allocation_t = 0.1% x sum over the last 10 years of (net new homes x assessed value per home)
```

The state backfills schools, so the allocation equals the state's cost. The City of Los Angeles
share is shown separately.

### A5 Linked package (A2 + A3)

```
credit paid_t = min(A3 state cost_t, A2 state savings_t)
coverage_t    = credit paid_t / A3 state cost_t
```

Coverage below 1 means the cap binds: the credit must be scaled down (lower cap or income limit)
to stay budget-neutral.

## Not modeled (stated, not hidden)

- Deals restructured to avoid A2 (lowers A2 revenue).
- Landlords raising rents to capture part of the A3 credit (lowers A3's benefit to renters).
- Any added housing supply from A4 beyond the homes assumed to be completed (the main
  uncertainty about A4's effectiveness; the Legislative Analyst's Office (LAO) (2016) found limited evidence it changes zoning).
