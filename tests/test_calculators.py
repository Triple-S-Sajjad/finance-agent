import pytest
from finance_agent.tools.calculators import calculate_emi, ToolArgError


def test_known_value():
    r = calculate_emi({"principal": 100000, "annual_rate_percent": 12, "months": 12})
    assert r["monthly_payment"] == 8884.88


def test_zero_interest():
    r = calculate_emi({"principal": 12000, "annual_rate_percent": 0, "months": 12})
    assert r["monthly_payment"] == 1000
    assert r["total_interest"] == 0


def test_accepts_formatted_strings():
    r = calculate_emi({"principal": "$20,000", "annual_rate_percent": "7%", "months": "60"})
    assert r["monthly_payment"] == 396.02


@pytest.mark.parametrize("bad_args", [
    {"annual_rate_percent": 7, "months": 60},                      # missing principal
    {"principal": -5, "annual_rate_percent": 7, "months": 60},      # negative
    {"principal": 5000, "annual_rate_percent": 7, "months": 6.5},   # fractional months
    {"principal": "abc", "annual_rate_percent": 7, "months": 60},   # not a number
])
def test_rejects_bad_args(bad_args):
    with pytest.raises(ToolArgError):
        calculate_emi(bad_args)