# tests/test_leaps_analysis.py

import pytest
import pandas as pd
from datetime import datetime, timedelta

from src.analysis.leaps_analysis import find_leaps_opportunities

# Default config for tests
TEST_CONFIG = {
    'days_to_expiration_min': 365,
    'max_ask_price': 5.00,
    'min_open_interest': 100,
    'min_volume': 50,
    'otm_percentage_min': 5,
}

@pytest.fixture
def mock_extractor(mocker):
    """Fixture to mock the OptionDataExtractor and its methods."""
    mock = mocker.patch('src.analysis.leaps_analysis.OptionDataExtractor', autospec=True)
    instance = mock.return_value

    # Mock data
    today = datetime.now()
    leaps_exp_1 = (today + timedelta(days=400)).strftime('%Y-%m-%d')
    leaps_exp_2 = (today + timedelta(days=500)).strftime('%Y-%m-%d')
    short_exp = (today + timedelta(days=30)).strftime('%Y-%m-%d')

    # Mock method return values
    instance.get_current_price.return_value = 150.00
    instance.get_available_expirations.return_value = [short_exp, leaps_exp_1, leaps_exp_2]

    def get_option_chain_side_effect(ticker, exp_date):
        if exp_date == leaps_exp_1:
            # This chain has one good option and one bad one
            return {
                'calls': pd.DataFrame({
                    'strike': [160.0, 170.0], # 160 is not OTM enough, 170 is
                    'ask': [4.50, 4.80], # Both are cheap enough
                    'openInterest': [150, 120], # Both are liquid
                    'volume': [60, 70], # Both are liquid
                    'delta': [0.4, 0.3],
                    'expiration': [exp_date, exp_date],
                    'ticker': [ticker, ticker]
                }),
                'puts': pd.DataFrame()
            }
        elif exp_date == leaps_exp_2:
             # This chain has one option that is too expensive
            return {
                'calls': pd.DataFrame({
                    'strike': [180.0],
                    'ask': [6.00], # Too expensive
                    'openInterest': [200],
                    'volume': [100],
                    'delta': [0.25],
                    'expiration': [exp_date],
                    'ticker': [ticker]
                }),
                'puts': pd.DataFrame()
            }
        return {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}

    instance.get_option_chain.side_effect = get_option_chain_side_effect
    
    return instance

def test_find_leaps_opportunities_happy_path(mock_extractor):
    """
    Tests the main function with ideal data, expecting to find two opportunities.
    """
    watchlist = ['GOODTICKER']
    
    # The minimum OTM strike is 150 * (1 + 5/100) = 157.5
    # The 160 strike is > 157.5, ask=4.50 <= 5.00, liquid. This is one.
    # The 170 strike is > 157.5, ask=4.80 <= 5.00, liquid. This is the second one.
    # The 180 strike from the second chain is OTM, but ask=6.00 > 5.00, so it's filtered out.
    
    results = find_leaps_opportunities(watchlist, TEST_CONFIG)
    
    assert not results.empty
    assert len(results) == 2
    assert results.iloc[0]['ticker'] == 'GOODTICKER'
    assert results.iloc[0]['strike'] == 160.0
    assert results.iloc[1]['strike'] == 170.0
    assert 'days_to_expiration' in results.columns

def test_find_leaps_no_opportunities_found(mock_extractor):
    """
    Tests a scenario where no options meet the criteria (e.g., all too expensive).
    """
    # We can reuse the mock but change the config for this test
    tight_config = TEST_CONFIG.copy()
    tight_config['max_ask_price'] = 4.00 # Make all existing options too expensive

    watchlist = ['GOODTICKER']
    results = find_leaps_opportunities(watchlist, tight_config)

    assert results.empty

def test_find_leaps_no_leaps_expirations(mock_extractor):
    """
    Tests a scenario where a ticker has no long-term expiration dates.
    """
    # Adjust the mock to return no LEAPS dates
    mock_extractor.get_available_expirations.return_value = [(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')]

    watchlist = ['NOLEAPS']
    results = find_leaps_opportunities(watchlist, TEST_CONFIG)

    assert results.empty
    
def test_find_leaps_no_option_data(mock_extractor):
    """
    Tests a scenario where a ticker has no option data at all.
    """
    # Adjust the mock to return nothing
    mock_extractor.get_available_expirations.return_value = []
    mock_extractor.get_option_chain.side_effect = None
    mock_extractor.get_option_chain.return_value = {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}

    watchlist = ['NODATA']
    results = find_leaps_opportunities(watchlist, TEST_CONFIG)

    assert results.empty

def test_fetch_leaps_no_current_price(mock_extractor):
    """
    Tests the case where the current price for a ticker cannot be fetched.
    """
    mock_extractor.get_current_price.return_value = None
    
    watchlist = ['PRICEFAIL']
    results = find_leaps_opportunities(watchlist, TEST_CONFIG)
    
    assert results.empty

def test_fetch_leaps_empty_calls_chain(mock_extractor):
    """
    Tests the case where a LEAPS expiration exists but has no call options.
    """
    # Have get_option_chain return an empty 'calls' dataframe
    mock_extractor.get_option_chain.side_effect = lambda ticker, exp_date: {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}
    
    watchlist = ['EMPTYCALLS']
    results = find_leaps_opportunities(watchlist, TEST_CONFIG)

    assert results.empty

def test_find_leaps_missing_delta_column(mock_extractor):
    """
    Tests the safeguard that handles missing columns in the data.
    """
    # Redefine the side effect to return data without a 'delta' column
    def get_option_chain_no_delta(ticker, exp_date):
        today = datetime.now()
        leaps_exp_1 = (today + timedelta(days=400)).strftime('%Y-%m-%d')
        if exp_date == leaps_exp_1:
            return {
                'calls': pd.DataFrame({
                    'strike': [170.0],
                    'ask': [4.80],
                    'openInterest': [120],
                    'volume': [70],
                    # 'delta' column is intentionally missing
                    'expiration': [exp_date],
                    'ticker': [ticker]
                }),
                'puts': pd.DataFrame()
            }
        return {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}
    
    mock_extractor.get_option_chain.side_effect = get_option_chain_no_delta
    
    watchlist = ['MISSINGCOL']
    results = find_leaps_opportunities(watchlist, TEST_CONFIG)

    assert not results.empty
    assert len(results) == 1
    assert results.iloc[0]['ticker'] == 'MISSINGCOL'
    assert results.iloc[0]['strike'] == 170.0
    assert 'delta' in results.columns
    assert results.iloc[0]['delta'] == 'N/A'
