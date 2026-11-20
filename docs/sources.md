# Sources

[← Methods](methods.md) · [README](../README.md)

Replace each team assumption with data, then change its row's `status` to `official` and its
`source` to the dataset. Data always takes precedence over a placeholder.

| Input (`assumptions.csv` key) | Data to replace it with | Where |
|---|---|---|
| `eligible_renters`, `avg_credit` | Census ACS 1-year PUMS household microdata (rent, income, weights) | `python -m prop13_forecast.pums` (needs `CENSUS_API_KEY`) |
| `takeup` | Michigan homestead property tax credit claim statistics | michigan.gov/treasury |
| `rent_growth` | Zillow Observed Rent Index (ZORI), California and Los Angeles | zillow.com/research/data |
| `entity_av`, `untaxed_transfer_rate` | BOE annual report statistics; Legal Entity Ownership Program filings; LA County Assessor parcel data | boe.ca.gov; data.lacounty.gov |
| `value_gap` | LA County Assessor roll (base year vs. recent sales) | data.lacounty.gov |
| `school_share` | Property tax allocation figures | LAO (2012); county auditor-controller allocation tables |
| `prop98_offset` | Which Prop 98 test applies in each projected year | LAO Prop 98 outlook reports |
| `net_new_units`, `la_unit_share` | HCD Housing Element Annual Progress Report data; DOF E-5 housing estimates | data.ca.gov; dof.ca.gov |
| `new_unit_av` | County assessor new-construction values | data.lacounty.gov |

## Reusable from the Ontario model (`~/sunstone`)

- `ingest/sources.py`: `sco_city_revenue_lines` (State Controller city revenues; point it at
  Los Angeles for a status quo revenue-mix baseline) and `_ckan_csv_url` (data.ca.gov uses the
  same CKAN platform, so it can pull the HCD progress report data).
- `modeling/evaluation.py` and `modeling/scenarios.py`: backtested baseline forecast with
  low/likely/high fans, if the paper needs a status quo revenue projection.
