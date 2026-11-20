import numpy as np
import pytest

from prop13_forecast import config
from prop13_forecast.assumptions import load_assumptions
from prop13_forecast.model import cohort_sum, ramp, simulate, summarize, tornado

YEARS = np.arange(config.FIRST_FY, config.LAST_FY + 1)


@pytest.fixture(scope="module")
def A():
    return load_assumptions(config.ASSUMPTIONS)


@pytest.fixture(scope="module")
def res(A):
    return simulate(A, YEARS, 2_000, np.random.default_rng(1))


def test_ramp():
    np.testing.assert_allclose(ramp(np.array([2027, 2028, 2029, 2030]), 2028, 2029), [0, 0.5, 1, 1])
    np.testing.assert_allclose(ramp(np.array([2027, 2028]), 2028, 2028), [0, 1])


def test_cohort_sum_life_drops_old_cohorts():
    inflow = np.ones((1, 5))
    out = cohort_sum(inflow, np.zeros(1), life=2)
    np.testing.assert_allclose(out[0], [1, 2, 2, 2, 2])
    np.testing.assert_allclose(cohort_sum(inflow, np.zeros(1))[0], [1, 2, 3, 4, 5])


def test_every_input_has_source_and_valid_status(A):
    assert all(a.source and a.status in ("official", "design", "assumption") for a in A.values())


def test_outcomes_nonnegative(res):
    for key, x in res.series.items():
        assert x.shape == (2_000, len(YEARS)), key
        assert (x >= 0).all(), key


def test_package_credit_within_cap_and_cost(res):
    s = res.series
    assert (s["A5_credit_paid"] <= s["A3_state_cost"] + 1e-6).all()
    assert (s["A5_credit_paid"] <= s["A2_state_savings"] + 1e-6).all()
    assert ((s["A5_coverage"] >= 0) & (s["A5_coverage"] <= 1)).all()


def test_a4_hand_calc(A):
    fixed = {k: a.fixed() for k, a in A.items()}
    r = simulate(fixed, YEARS, 1, np.random.default_rng(0))
    per_year = A["net_new_units"].mode * A["new_unit_av"].mode * A["extra_share"].mode
    # zero real growth at the mode: year t holds t+1 cohorts (all within the 10-year life)
    np.testing.assert_allclose(r.series["A4_state_cost"][0], per_year * np.arange(1, len(YEARS) + 1))


def test_summary_and_tornado_run(A, res):
    rows = summarize(res)
    assert all(r["p10"] <= r["p50"] <= r["p90"] for r in rows)
    tor = tornado(A, YEARS, "A2_local_revenue")
    assert tor and abs(tor[0][2] - tor[0][1]) >= abs(tor[-1][2] - tor[-1][1])
