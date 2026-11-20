# Sources

[← Methods](methods.md) · [README](../README.md)

**All data is restricted to California.** Every dataset below is a California state agency source or
a federal dataset filtered to California (state FIPS code 06, the Federal Information Processing
Standards code for California), its counties or its cities. No national or out-of-state data feeds
the model.

Replace each team assumption with data, then change its row's `status` to `official` and its
`source` to the dataset. Data always takes precedence over a placeholder.

## Abbreviations

| Abbreviation | Meaning |
|---|---|
| ACS | American Community Survey (U.S. Census Bureau) |
| BLS | U.S. Bureau of Labor Statistics |
| BOE | California State Board of Equalization |
| CalEITC | California Earned Income Tax Credit |
| CHAS | Comprehensive Housing Affordability Strategy data (HUD) |
| CPI | Consumer Price Index (BLS) |
| DOF | California Department of Finance |
| E-5 | DOF's annual population and housing estimates for cities and counties |
| ERAF | Educational Revenue Augmentation Fund (county funds that shift property tax to schools) |
| FIPS | Federal Information Processing Standards (geographic codes) |
| FRED | Federal Reserve Economic Data (Federal Reserve Bank of St. Louis) |
| FTB | California Franchise Tax Board |
| HCD | California Department of Housing and Community Development |
| HUD | U.S. Department of Housing and Urban Development |
| LA | Los Angeles |
| LAO | California Legislative Analyst's Office |
| Prop 98 | Proposition 98 (1988), California's minimum funding guarantee for K-14 schools |
| PUMS | Public Use Microdata Sample (household-level ACS records) |
| SCO | California State Controller's Office |
| VLF | Vehicle license fee; the 2004 "VLF swap" replaced cities' VLF revenue with property tax shifted from ERAF |

## Data for each model input

| Input (`assumptions.csv` key) | California data to replace it with | Where |
|---|---|---|
| `eligible_renters`, `avg_credit` | American Community Survey (ACS) 1-year Public Use Microdata Sample (PUMS) household records, California renter households only (rent, income, weights); U.S. Department of Housing and Urban Development (HUD) Comprehensive Housing Affordability Strategy (CHAS) California state file to cross-check totals | `python -m prop13_forecast.pums` (needs `CENSUS_API_KEY`); huduser.gov |
| `takeup` | California Franchise Tax Board (FTB) statistics on renters' credit and California Earned Income Tax Credit (CalEITC) claims among eligible filers | ftb.ca.gov |
| `rent_growth` | Bureau of Labor Statistics (BLS) Consumer Price Index (CPI) rent of primary residence for California metro areas (Los Angeles, San Francisco, San Diego, Riverside) | bls.gov; Federal Reserve Economic Data (FRED) |
| `entity_av`, `untaxed_transfer_rate` | California State Board of Equalization (BOE) annual report statistics; county assessor roll data (Los Angeles County as the California case study) | boe.ca.gov; data.lacounty.gov |
| `value_gap` | Los Angeles County Assessor roll (base year vs. recent sales) | data.lacounty.gov |
| `school_share` | California property tax allocation figures | Legislative Analyst's Office (LAO) (2012); county auditor-controller allocation tables |
| `prop98_offset` | Which Proposition 98 (Prop 98) test applies in each projected year | LAO Prop 98 outlook reports |
| `net_new_units`, `la_unit_share` | California Department of Finance (DOF) E-5 housing estimates; California Department of Housing and Community Development (HCD) Housing Element Annual Progress Report data | dof.ca.gov; data.ca.gov |
| `new_unit_av` | County assessor new-construction values (California counties) | data.lacounty.gov |
| Status quo revenue baseline | California State Controller's Office (SCO) city revenue data (City of Los Angeles) | bythenumbers.sco.ca.gov |

Michigan's homestead credit informs the circuit breaker's *design* only (see the memo); none of its
data is used in the model.
