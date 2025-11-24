# tests/test_greeks_calculator.py

import pytest
import pandas as pd
from src.data.greeks_calculator import GreeksCalculator

@pytest.fixture
def calculator():
    return GreeksCalculator()

def test_calculate_days_to_expiration_invalid_date(calculator):
    assert calculator.calculate_days_to_expiration("invalid-date") == 0

@pytest.mark.parametrize("capital, days", [(0, 30), (100, 0), (0, 0)])
def test_calculate_annualized_return_zero_inputs(calculator, capital, days):
    assert calculator.calculate_annualized_return(1.0, capital, days) == 0.0

@pytest.mark.parametrize("capital, days", [(0, 30), (100, 0), (0, 0)])
def test_calculate_monthly_return_zero_inputs(calculator, capital, days):
    assert calculator.calculate_monthly_return(1.0, capital, days) == 0.0

def test_calculate_breakeven_put(calculator):
    # This covers the 'else' branch
    assert calculator.calculate_breakeven(100, 2.0, 'put') == 98.0

@pytest.mark.parametrize("days, iv", [(0, 0.2), (30, 0)])
def test_calculate_probability_otm_zero_inputs(calculator, days, iv):
    assert calculator.calculate_probability_otm(100, 95, iv, days, 'put') == 0.0

def test_calculate_probability_otm_put(calculator):
    # This covers the 'else' branch for option_type
    # Not a perfect test of the math, but it exercises the code path
    prob = calculator.calculate_probability_otm(100, 95, 0.2, 30, 'put')
    assert 0 < prob < 100

def test_enrich_option_data_empty_df(calculator):
    assert calculator.enrich_option_data(pd.DataFrame()).empty

def test_enrich_option_data_atm_classification(calculator):
    """Tests the ATM classification in enrich_option_data."""
    df = pd.DataFrame({
        'ticker': ['ATM_CALL', 'ATM_PUT'],
        'option_type': ['call', 'put'],
        'current_stock_price': [100.0, 100.0],
        'strike': [100.0, 100.0],
        'expiration': ['2025-12-19', '2025-12-19'],
        'bid': [1.0, 1.0], 'ask': [1.1, 1.1], 'lastPrice': [1.05, 1.05]
    })
    
    result_df = calculator.enrich_option_data(df)
    assert 'ATM' in result_df['moneyness_class'].values
