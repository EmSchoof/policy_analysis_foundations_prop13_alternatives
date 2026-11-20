# Prop 13 Reform Alternatives: Outcome Projections

**PPD 554: Foundations of Policy Analysis, Group 3: Economic Opportunity, Taxes, and Social Welfare**
USC Price School of Public Policy, Fall 2026

This repository supports the group's policy analysis memo. It projects the outcomes of each policy
alternative against the memo's four criteria, so the analysis can compare alternatives, name the key
tradeoff, and support a recommendation.

## The assignment

Each group writes a full policy analysis for its client on a chosen topic. The memo contains:

- an issue diagnosis
- three policy alternatives to address the issue
- four policy criteria
- a projection of policy outcomes with respect to those criteria
- a key tradeoff and, if appropriate, a policy recommendation

## The issue and the client

Proposition 13 (1978) caps the property tax rate at 1% and ties a property's taxable value to its
purchase price. It gives long-time owners predictable tax bills, but it also concentrates benefits among
higher-income owners, discourages turnover and new housing, pushes local governments toward volatile
revenue sources, and gives renters, who receive no direct benefit, little relief from high housing costs.

**Client:** Chair of the California Senate Revenue and Taxation Committee, which hears legislation on
property tax assessment and state income tax credits.

## Alternatives modeled

The status quo is the baseline: every projection is what an alternative **adds** to it.

| Code | Alternative | What it does |
|---|---|---|
| A1 | Status quo (baseline) | Prop 13, the 50% control rule and the current renters' credit remain unchanged |
| A2 | Proportional reassessment of company-owned property | When X% of a company's ownership changes hands, X% of its property is reassessed |
| A3 | Renter's circuit breaker | A refundable credit for the share of rent above a set portion of income, modeled on Michigan's program |
| A4 | Housing growth allocation | Cities receive an extra 0.1% of each new home's assessed value for 10 years, modeled on the 2004 VLF swap |
| A5 | A2 + A3 as linked bills | The circuit breaker, capped at the state's savings from reassessment (candidate recommendation) |

## How projections map to the criteria

| Criterion | What the model projects |
|---|---|
| Effectiveness | New local property tax (A2); households helped (A3); City of Los Angeles revenue (A4) |
| Feasibility (fiscal) | State cost (A3, A4); state Prop 98 savings (A2); share of the credit the savings cap can fund (A5) |
| Equity | Relief reaching rent-burdened renters (A3, A5) |
| Cost-effectiveness | Relief or revenue per public dollar (from the projected costs and revenues) |

Political and legal feasibility (vote thresholds, opposition) are assessed in the memo, not in the model.

## Method

Built on the design of the team's Connecting Ontario forecast model:

- **Every input is a range with a source.** `data/assumptions/assumptions.csv` gives each input a low,
  likely and high value, a status (`official`, `design` or `assumption`) and a source.
- **Ranges, not a single answer.** 20,000 simulations draw all inputs at once; results are reported as
  10th, 50th and 90th percentiles over FY 2027-28 to FY 2036-37, in real dollars.
- **Simple, explicit formulas.** None of these policies exists yet in California, so outcomes come from
  cause-and-effect formulas, not models fitted to history.
- **Sensitivity.** Each input is swung from low to high to show which assumptions matter most.

Formulas and limitations: [docs/methods.md](docs/methods.md). Data to replace each placeholder:
[docs/sources.md](docs/sources.md).

> **Status: in progress.** Most inputs are still team placeholders marked `assumption`. Results are not
> committed to this repository; run the model to generate them locally.

## Running it

Requires [uv](https://docs.astral.sh/uv/) and Python 3.11.

```bash
uv sync --extra analysis --extra dev
uv run pytest
uv run python -m prop13_forecast.run
```

Results are written to `outputs/` (ignored by git):

- `outputs/tables/summary.csv`: headline results (10th / 50th / 90th percentile)
- `outputs/tables/sensitivity.csv`: which input moves each result most
- `outputs/tables/inputs_used.csv`: every input with its status and source
- `outputs/charts/annual_outcomes.png`: annual ranges for A2-A5

To replace the circuit breaker placeholders with Census household data (free key at
https://api.census.gov/data/key_signup.html):

```bash
CENSUS_API_KEY=your_key uv run python -m prop13_forecast.pums
```

## Repository layout

```
data/assumptions/assumptions.csv   every input: range, status, source
src/prop13_forecast/
  config.py        projection window, phase-in, circuit breaker design
  assumptions.py   loads and validates inputs
  model.py         formulas for A2-A5, summaries, sensitivity
  pums.py          circuit breaker cost from Census household microdata
  run.py           tables and charts
tests/             formula and data checks
docs/methods.md    formulas and what is not modeled
docs/sources.md    data to replace each placeholder
```

## Acknowledgments

Model design adapted from the team's Connecting Ontario forecast (Sunstone Economic Development
Challenge, USC Price). Claude (Anthropic, 2026) assisted with source research and code.
