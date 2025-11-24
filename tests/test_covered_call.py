# tests/test_covered_call.py

import pytest
import pandas as pd
from datetime import datetime, timedelta

from src.strategies.covered_call import CoveredCallAnalyzer

@pytest.fixture
def cc_analyzer():
    """Returns an instance of CoveredCallAnalyzer."""
    return CoveredCallAnalyzer()

@pytest.fixture
def sample_options_df():
    """Provides a sample DataFrame of options for covered call testing."""
    today = datetime.now()
    return pd.DataFrame({
        'ticker': ['TICK1', 'TICK1', 'TICK1', 'TICK2', 'TICK2'],
        'option_type': ['call', 'call', 'put', 'call', 'call'],
        'current_stock_price': [50.0, 50.0, 50.0, 100.0, 100.0],
        'strike': [52.0, 55.0, 48.0, 105.0, 95.0],
        'expiration': [
            (today + timedelta(days=30)).strftime('%Y-%m-%d'),
            (today + timedelta(days=70)).strftime('%Y-%m-%d'), # Too far out
            (today + timedelta(days=30)).strftime('%Y-%m-%d'),
            (today + timedelta(days=40)).strftime('%Y-%m-%d'),
            (today + timedelta(days=40)).strftime('%Y-%m-%d')  # In-the-money, usually not for CC
        ],
        'bid': [1.0, 2.0, 1.5, 2.5, 6.0],
        'ask': [1.1, 2.1, 1.6, 2.6, 6.2],
        'lastPrice': [1.05, 2.05, 1.55, 2.55, 6.1],
        'volume': [100, 120, 110, 130, 140],
        'openInterest': [1000, 2000, 1500, 2500, 3000],
        'delta': [0.4, 0.3, -0.45, 0.35, 0.6],
        'prob_otm': [60.0, 70.0, 65.0, 65.0, 30.0],
        'distance_pct': [4.0, 10.0, -4.0, 5.0, -5.0]
    })

def mock_enrich_data(df):
    """A realistic mock for enrich_option_data for testing purposes."""
    df_copy = df.copy()
    df_copy['days_to_expiration'] = (pd.to_datetime(df_copy['expiration']) - datetime.now()).dt.days
    return df_copy

def test_analyze_calls_basic_filters(cc_analyzer, sample_options_df, mocker):
    """Tests that the basic filters (type, DTE, premium) are applied correctly."""
    mocker.patch.object(cc_analyzer.greeks_calc, 'enrich_option_data', side_effect=mock_enrich_data)
    # Annual return will be calculated, so let's mock it to avoid calculation errors with mock data
    mocker.patch.object(cc_analyzer.greeks_calc, 'calculate_annualized_return', return_value=15.0)

    results = cc_analyzer.analyze_covered_calls(sample_options_df)

    # Should filter out: the put, and the one with DTE > 60
    assert len(results) == 3
    assert 'put' not in results['option_type'].unique()
    assert results['days_to_expiration'].max() <= 60

def test_analyze_calls_empty_input(cc_analyzer):
    """Tests that an empty DataFrame in results in an empty DataFrame out."""
    results = cc_analyzer.analyze_covered_calls(pd.DataFrame())
    assert results.empty

def test_analyze_calls_delta_filters(cc_analyzer, sample_options_df, mocker):
    """Tests the min and max delta filters."""
    mocker.patch.object(cc_analyzer.greeks_calc, 'enrich_option_data', side_effect=mock_enrich_data)
    mocker.patch.object(cc_analyzer.greeks_calc, 'calculate_annualized_return', return_value=15.0)

    # Filter for deltas between 0.32 and 0.42
    results = cc_analyzer.analyze_covered_calls(sample_options_df, min_delta=0.32, max_delta=0.42)
    
    # In the valid DTE range, two calls match this: delta 0.4 and 0.35
    assert len(results) == 2
    assert results['delta'].min() >= 0.32
    assert results['delta'].max() <= 0.42

def test_analyze_calls_min_return_filter(cc_analyzer, sample_options_df, mocker):
    """Tests the minimum annual return filter."""
    mocker.patch.object(cc_analyzer.greeks_calc, 'enrich_option_data', side_effect=mock_enrich_data)
    # The three valid calls will have these returns assigned sequentially
    mocker.patch.object(cc_analyzer.greeks_calc, 'calculate_annualized_return', side_effect=[12.0, 8.0, 15.0])
    
    results = cc_analyzer.analyze_covered_calls(sample_options_df, min_annual_return=10.0)
    
    # Of the 3 valid calls, one has a return of 8.0, so it should be filtered out
    assert len(results) == 2
    assert results['annual_return'].min() >= 10.0

def test_get_top_opportunities(cc_analyzer, mocker):
    """Tests that get_top_opportunities correctly limits the number of results."""
    mock_results = pd.DataFrame({'a': range(10)})
    mocker.patch.object(cc_analyzer, 'analyze_covered_calls', return_value=mock_results)

    results = cc_analyzer.get_top_opportunities(pd.DataFrame(), top_n=5)
    assert len(results) == 5

def test_summarize_by_ticker(cc_analyzer, sample_options_df, mocker):
    """Tests the summarize_by_ticker method."""
    mocker.patch.object(cc_analyzer.greeks_calc, 'enrich_option_data', side_effect=mock_enrich_data)
    mocker.patch.object(cc_analyzer.greeks_calc, 'calculate_annualized_return', return_value=15.0)
    
    analyzed_df = cc_analyzer.analyze_covered_calls(sample_options_df)
    summary = cc_analyzer.summarize_by_ticker(analyzed_df)
    
    assert len(summary) == 2
    assert 'TICK1' in summary.index
    assert summary.loc['TICK1']['num_opportunities'] == 1

def test_compare_expirations(cc_analyzer, sample_options_df, mocker):
    """Tests the compare_expirations method."""
    mocker.patch.object(cc_analyzer.greeks_calc, 'enrich_option_data', side_effect=mock_enrich_data)
    
    # Strike range (0.95, 1.05) for TICK2 (price 100) -> 95 to 105
    results = cc_analyzer.compare_expirations(sample_options_df, ticker='TICK2', strike_range=(0.95, 1.05))
    
    assert len(results) == 2
    assert results['strike'].isin([105.0, 95.0]).all()
