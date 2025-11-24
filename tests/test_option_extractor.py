# tests/test_option_extractor.py

import pytest
import pandas as pd
from unittest.mock import MagicMock

from src.data.option_extractor import OptionDataExtractor

@pytest.fixture
def mock_yfinance(mocker):
    """Fixture to mock the yfinance.Ticker object."""
    mock = mocker.patch('src.data.option_extractor.yf.Ticker', autospec=True)
    return mock

def test_get_option_chain_exception(mock_yfinance):
    """Tests that an exception during yfinance call is handled."""
    mock_yfinance.side_effect = Exception("Test yfinance error")
    extractor = OptionDataExtractor()
    result = extractor.get_option_chain('FAIL', '2025-01-01')
    assert result['calls'].empty
    assert result['puts'].empty

def test_get_available_expirations_exception(mock_yfinance):
    """Tests exception handling for get_available_expirations."""
    mock_yfinance.side_effect = Exception("Test yfinance error")
    extractor = OptionDataExtractor()
    result = extractor.get_available_expirations('FAIL')
    assert result == []

def test_get_current_price_exception(mock_yfinance):
    """Tests exception handling for get_current_price."""
    mock_yfinance.side_effect = Exception("Test yfinance error")
    extractor = OptionDataExtractor()
    result = extractor.get_current_price('FAIL')
    assert result is None

def test_get_stock_info_exception(mock_yfinance):
    """Tests exception handling for get_stock_info."""
    mock_yfinance.side_effect = Exception("Test yfinance error")
    extractor = OptionDataExtractor()
    result = extractor.get_stock_info('FAIL')
    assert 'error' not in result # Should return a partial dict

def test_fetch_with_explicit_dates(mock_yfinance):
    """Tests passing explicit expiration dates to fetch_and_store_options."""
    # Setup mock
    instance = mock_yfinance.return_value
    instance.history.return_value = pd.DataFrame({'Close': [100]})
    
    # Mock the get_option_chain method to track calls
    mock_chain = MagicMock()
    mock_chain.return_value = {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}
    
    extractor = OptionDataExtractor()
    extractor.get_option_chain = mock_chain

    dates_to_fetch = ['2025-01-17', '2025-02-21']
    extractor.fetch_and_store_options(tickers=['TEST'], expiration_dates=dates_to_fetch)
    
    # Assert that get_option_chain was called for each of the specified dates
    assert mock_chain.call_count == 2
    mock_chain.assert_any_call('TEST', '2025-01-17')
    mock_chain.assert_any_call('TEST', '2025-02-21')

def test_load_latest_data(tmp_path):
    """Tests loading the latest data file."""
    data_dir = tmp_path / "option_chains"
    data_dir.mkdir()
    
    # Create dummy files
    (data_dir / "options_data_20230101_120000.csv").touch()
    (data_dir / "options_data_20230103_120000.csv").write_text("col1,col2\n1,2")
    (data_dir / "options_data_20230102_120000.csv").touch()
    
    extractor = OptionDataExtractor(data_dir=str(data_dir))
    df = extractor.load_latest_data()
    
    # Should load the one from Jan 3rd and parse it correctly
    assert not df.empty
    assert len(df) == 1
    assert df.iloc[0]['col1'] == 1
