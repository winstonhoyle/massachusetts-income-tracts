import math

from format_data import clean, column_name


def test_column_name():
    assert column_name("Estimate!!Households!!Total") == "total-households"
    assert (
        column_name("Estimate!!Households!!Total!!$10,000 to $14,999")
        == "10,000_to_14,999-households"
    )
    assert (
        column_name("Estimate!!Married-couple families!!Median income (dollars)")
        == "median_income_(dollars)-married_couple_families"
    )
    assert (
        column_name(
            "Estimate!!Households!!PERCENT ALLOCATED!!Household income in the past 12 months"
        )
        is None
    )
    assert column_name("Geographic Area Name") is None


def test_clean():
    assert clean("1298") == 1298.0
    assert clean("3.2") == 3.2
    assert math.isnan(clean("-666666666"))
