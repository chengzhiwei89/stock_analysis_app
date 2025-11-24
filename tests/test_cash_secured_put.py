# tests/test_cash_secured_put.py

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import config

from src.strategies.cash_secured_put import CashSecuredPutAnalyzer

@pytest.fixture
def csp_analyzer():
    """Returns an instance of CashSecuredPutAnalyzer."""
    return CashSecuredPutAnalyzer()

@pytest.fixture
def sample_options_df():
    """Provides a sample DataFrame of options for testing."""
    today = datetime.now()
    return pd.DataFrame({
        'ticker': ['TICK1', 'TICK1', 'TICK1', 'TICK1', 'TICK2'],
        'option_type': ['put', 'put', 'put', 'call', 'put'],
        'current_stock_price': [100.0, 100.0, 100.0, 100.0, 200.0],
        'strike': [95.0, 90.0, 85.0, 95.0, 180.0],
        'expiration': [
            (today + timedelta(days=30)).strftime('%Y-%m-%d'),
            (today + timedelta(days=30)).strftime('%Y-%m-%d'),
            (today + timedelta(days=65)).strftime('%Y-%m-%d'),
            (today + timedelta(days=30)).strftime('%Y-%m-%d'),
            (today + timedelta(days=40)).strftime('%Y-%m-%d')
        ],
        'bid': [1.0, 0.5, 1.5, 1.1, 2.0],
        'ask': [1.1, 0.6, 1.6, 1.2, 2.2],
        'lastPrice': [1.05, 0.55, 1.55, 1.15, 2.1],
        'volume': [100, 5, 200, 150, 300],
        'openInterest': [1000, 50, 2000, 1500, 3000],
        'delta': [-0.3, -0.2, -0.25, 0.6, -0.28],
        'prob_otm': [70.0, 80.0, 75.0, 30.0, 72.0],
        'distance_pct': [-5.0, -10.0, -15.0, -5.0, -10.0]
    })

def test_calculate_effective_price(csp_analyzer):
    """Tests the _calculate_effective_price method with various scenarios."""
    df = pd.DataFrame({
        'bid':       [1.0, 0.0, 0.0, 0.0, np.nan],
        'lastPrice': [1.1, 0.8, 0.0, 0.0, 0.0],
        'ask':       [1.2, 0.9, 0.6, 0.0, 0.0]
    })
    
    result_df = csp_analyzer._calculate_effective_price(df)
    
    # 1. Prefers bid
    assert result_df.loc[0, 'effective_price'] == 1.0
    assert result_df.loc[0, 'price_source'] == 'bid'
    
    # 2. Falls back to lastPrice
    assert result_df.loc[1, 'effective_price'] == 0.8
    assert result_df.loc[1, 'price_source'] == 'lastPrice'

    # 3. Falls back to ask/2
    assert result_df.loc[2, 'effective_price'] == 0.3
    assert result_df.loc[2, 'price_source'] == 'ask/2'
    
    # 4. Returns 0 if all are 0
    assert result_df.loc[3, 'effective_price'] == 0
    assert result_df.loc[3, 'price_source'] == 'none'
    
    # 5. Handles NaN values
    assert result_df.loc[4, 'effective_price'] == 0
    assert result_df.loc[4, 'price_source'] == 'none'

def test_analyze_puts_basic_filters(csp_analyzer, sample_options_df):
    """Tests basic filtering of the analyze_cash_secured_puts method."""
    
    # Default filters should remove the call option, the one with low premium, and the one with long DTE
    results = csp_analyzer.analyze_cash_secured_puts(sample_options_df)
    
    # Expected to keep TICK1 strike 95 and TICK2 strike 180
    assert not results.empty
    assert len(results) == 2
    assert 'call' not in results['option_type'].unique()
    assert results['premium_received'].min() >= 0.5
    assert results['days_to_expiration'].max() <= 60

def test_analyze_puts_empty_input(csp_analyzer):
    """Tests that an empty DataFrame in results in an empty DataFrame out."""
    results = csp_analyzer.analyze_cash_secured_puts(pd.DataFrame())
    assert results.empty

def test_analyze_puts_quality_ticker_filter(csp_analyzer, sample_options_df):
    """Tests the quality_tickers filter."""
    results = csp_analyzer.analyze_cash_secured_puts(sample_options_df, quality_tickers=['TICK1'])
    
    assert not results.empty
    assert len(results) == 1
    assert results.iloc[0]['ticker'] == 'TICK1'

def test_analyze_puts_delta_filter(csp_analyzer, sample_options_df):
    """Tests the min_delta and max_delta filters."""
    # Filter for deltas between -0.26 and -0.22 (should only match the TICK1 strike 85 option, but it has long DTE)
    # Let's adjust max_days to include it
    results = csp_analyzer.analyze_cash_secured_puts(sample_options_df, max_days=70, min_delta=-0.26, max_delta=-0.22)
    
    assert not results.empty
    assert len(results) == 1
    assert results.iloc[0]['delta'] == -0.25

def test_analyze_puts_volume_filter(csp_analyzer, sample_options_df):
    """Tests the min_volume filter."""
    # The TICK1 strike 90 option has volume of 5
    results = csp_analyzer.analyze_cash_secured_puts(sample_options_df, min_premium=0.1, min_volume=10)

    # Should filter out the one with volume=5
    assert len(results) == 2
    assert 90.0 not in results['strike'].values

import config

def test_analyze_puts_safety_distance_filter(csp_analyzer, sample_options_df, mocker):
    """Tests the safety filter for min_distance_pct imported from config."""
    # The TICK1 strike 95 has a distance_pct of -5.0
    
    # Patch the config value to be more restrictive
    mocker.patch.dict(config.CASH_SECURED_PUT_ADVANCED, {'min_distance_pct': 6.0})
    
    results = csp_analyzer.analyze_cash_secured_puts(sample_options_df)

    # The TICK1 strike 95 option should now be filtered out
    assert not results.empty
    assert len(results) == 1
    assert results.iloc[0]['ticker'] == 'TICK2'

    # Reset and test with a less restrictive value
    mocker.patch.dict(config.CASH_SECURED_PUT_ADVANCED, {'min_distance_pct': 4.0})

    results_less_restrictive = csp_analyzer.analyze_cash_secured_puts(sample_options_df)
    assert len(results_less_restrictive) == 2

def test_analyze_puts_cash_filters(csp_analyzer, sample_options_df):
    """Tests the available_cash and max_cash_per_position filters."""
    # Capital for TICK1 strike 95 is 95 * 100 = 9500
    # Capital for TICK2 strike 180 is 180 * 100 = 18000
    
    # Test with not enough cash for any position
    results_no_cash = csp_analyzer.analyze_cash_secured_puts(sample_options_df, available_cash=9000)
    assert results_no_cash.empty

    # Test with enough cash for one, but not the other
    results_some_cash = csp_analyzer.analyze_cash_secured_puts(sample_options_df, available_cash=10000)
    assert len(results_some_cash) == 1
    assert results_some_cash.iloc[0]['ticker'] == 'TICK1'
    assert results_some_cash.iloc[0]['max_affordable_contracts'] == 1

    # Test max_cash_per_position
    results_max_per_pos = csp_analyzer.analyze_cash_secured_puts(
        sample_options_df, 
        available_cash=100000, # Plenty of cash
        max_cash_per_position=10000 # But limited per trade
    )
    assert len(results_max_per_pos) == 1
    assert results_max_per_pos.iloc[0]['ticker'] == 'TICK1'
    assert results_max_per_pos.iloc[0]['max_affordable_contracts'] == 1

def test_get_top_opportunities(csp_analyzer, mocker):
    """Tests that get_top_opportunities correctly limits the number of results."""
    # Mock the main analysis function to isolate the get_top_opportunities logic
    mock_results = pd.DataFrame({'a': range(5)}) # A mock df with 5 rows
    mocker.patch.object(csp_analyzer, 'analyze_cash_secured_puts', return_value=mock_results)

    # Test that it correctly takes the top_n
    results = csp_analyzer.get_top_opportunities(pd.DataFrame(), top_n=3)
    assert len(results) == 3

    # Test with an empty dataframe from the analyzer
    mocker.patch.object(csp_analyzer, 'analyze_cash_secured_puts', return_value=pd.DataFrame())
    empty_results = csp_analyzer.get_top_opportunities(pd.DataFrame(), top_n=5)
    assert empty_results.empty

def test_summarize_by_ticker(csp_analyzer, sample_options_df):
    """Tests the summarize_by_ticker method."""
    analyzed_df = csp_analyzer.analyze_cash_secured_puts(sample_options_df)
    summary = csp_analyzer.summarize_by_ticker(analyzed_df)
    
    assert not summary.empty
    assert len(summary) == 2
    assert 'TICK1' in summary.index
    assert 'TICK2' in summary.index
    assert summary.loc['TICK1']['num_opportunities'] == 1
    
    # Test with empty input
    empty_summary = csp_analyzer.summarize_by_ticker(pd.DataFrame())
    assert empty_summary.empty

def test_compare_expirations(csp_analyzer, sample_options_df):
    """Tests the compare_expirations method."""
    # This should return the three puts for TICK1 within the strike range
    results = csp_analyzer.compare_expirations(sample_options_df, ticker='TICK1', strike_range=(0.8, 1.0))
    
    assert not results.empty
    assert len(results) == 3
    assert results['strike'].isin([95.0, 90.0, 85.0]).all()

    # Test with empty input
    empty_results = csp_analyzer.compare_expirations(pd.DataFrame(), ticker='TICK1')
    assert empty_results.empty

def test_find_wheel_candidates(csp_analyzer, mocker):
    """Tests the find_wheel_candidates method."""
    # Mock the main analysis function to isolate the wheel filtering logic
    mock_results = pd.DataFrame({
        'ticker': ['TICK1', 'TICK2'],
        'discount_from_current': [6.0, 4.0], # One above, one below the default 5%
        'annual_return': [25.0, 25.0],
        'prob_otm': [70, 70]
    })
    mocker.patch.object(csp_analyzer, 'analyze_cash_secured_puts', return_value=mock_results)

    # Test with default target discount (5.0)
    results = csp_analyzer.find_wheel_candidates(pd.DataFrame())
    assert len(results) == 1
    assert results.iloc[0]['ticker'] == 'TICK1'

    # Test with a higher discount requirement
    results_high_discount = csp_analyzer.find_wheel_candidates(pd.DataFrame(), target_entry_discount=7.0)
    assert results_high_discount.empty
