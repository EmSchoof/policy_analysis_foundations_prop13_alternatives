import numpy as np

from prop13_forecast import config
from prop13_forecast.pums import credit, summarize

DESIGN = config.CIRCUIT_BREAKER


def test_credit_formula():
    # rent $24,000, income $50,000: excess = 24,000 - 15,000 = 9,000; 20% = 1,800 (at cap)
    assert credit([24_000], [50_000], **DESIGN)[0] == 1_800
    # rent $18,000, income $50,000: excess 3,000 -> 600
    assert credit([18_000], [50_000], **DESIGN)[0] == 600
    # not rent-burdened, over the income limit, or zero income -> no credit
    np.testing.assert_array_equal(credit([10_000, 30_000, 12_000], [50_000, 80_000, 0], **DESIGN), [0, 0, 0])


def test_summarize_weights():
    s = summarize([18_000, 10_000], [50_000, 50_000], [100, 300], DESIGN)
    assert s["renter_households"] == 400
    assert s["eligible_households"] == 100
    assert s["avg_credit"] == 600
    assert s["total_cost_full_takeup"] == 60_000
