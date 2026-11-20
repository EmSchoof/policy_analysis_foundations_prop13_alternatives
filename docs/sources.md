# Sources

[← Methods](methods.md) · [README](../README.md)

**All data is restricted to California.** Every dataset below is a California state agency source or
a federal dataset filtered to California (state FIPS 06), its counties or its cities. No national or
out-of-state data feeds the model.

Replace each team assumption with data, then change its row's `status` to `official` and its
`source` to the dataset. Data always takes precedence over a placeholder.

| Input (`assumptions.csv` key) | California data to replace it with | Where |
|---|---|---|
| `eligible_renters`, `avg_credit` | Census ACS 1-year PUMS household microdata, California renter households only (rent, income, weights); HUD CHAS California state file to cross-check totals | `python -m prop13_forecast.pums` (needs `CENSUS_API_KEY`); huduser.gov |
| `takeup` | California FTB statistics on renters' credit and CalEITC claims among eligible filers | ftb.ca.gov |
| `rent_growth` | BLS CPI rent of primary residence for California metro areas (Los Angeles, San Francisco, San Diego, Riverside) | bls.gov; FRED |
| `entity_av`, `untaxed_transfer_rate` | California State Board of Equalization annual report statistics; county assessor roll data (LA County as the California case study) | boe.ca.gov; data.lacounty.gov |
| `value_gap` | LA County Assessor roll (base year vs. recent sales) | data.lacounty.gov |
| `school_share` | California property tax allocation figures | LAO (2012); county auditor-controller allocation tables |
| `prop98_offset` | Which California Prop 98 test applies in each projected year | LAO Prop 98 outlook reports |
| `net_new_units`, `la_unit_share` | California DOF E-5 housing estimates; HCD Housing Element Annual Progress Report data | dof.ca.gov; data.ca.gov |
| `new_unit_av` | County assessor new-construction values (California counties) | data.lacounty.gov |
| Status quo revenue baseline | California State Controller city revenue data (City of Los Angeles) | bythenumbers.sco.ca.gov |

Michigan's homestead credit informs the circuit breaker's *design* only (see the memo); none of its
data is used in the model.
