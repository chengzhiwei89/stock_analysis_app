# tests/test_portfolio_manager.py

import pytest
import pandas as pd
import json
import os
from datetime import datetime

from src.portfolio.portfolio_manager import PortfolioManager

@pytest.fixture
def empty_manager(tmp_path):
    """Provides a PortfolioManager instance pointed at an empty temp directory."""
    portfolio_file = tmp_path / "portfolio.json"
    return PortfolioManager(portfolio_file=str(portfolio_file))

@pytest.fixture
def populated_manager(empty_manager):
    """Provides a manager with one stock and one option position."""
    empty_manager.add_stock_position(
        ticker='AAPL', shares=100, cost_basis=150.0, purchase_date='2023-01-01'
    )
    empty_manager.add_option_position(
        ticker='AAPL', option_type='call', strike=170.0, expiration='2024-12-20',
        contracts=1, premium=2.50, open_date='2023-06-01', strategy='covered_call'
    )
    return empty_manager

def test_load_portfolio_nonexistent(empty_manager):
    """Tests that a new portfolio is created if the file doesn't exist."""
    assert empty_manager.portfolio['stocks'] == []
    assert empty_manager.portfolio['options'] == []

def test_add_stock_position(empty_manager):
    """Tests adding a stock position and saving it."""
    empty_manager.add_stock_position(
        ticker='MSFT', shares=50, cost_basis=300.0, purchase_date='2023-02-01'
    )
    
    # Verify internal state
    assert len(empty_manager.portfolio['stocks']) == 1
    assert empty_manager.portfolio['stocks'][0]['ticker'] == 'MSFT'
    
    # Verify data is saved to file by creating a new manager from the same file
    new_manager = PortfolioManager(portfolio_file=empty_manager.portfolio_file)
    assert len(new_manager.portfolio['stocks']) == 1
    assert new_manager.portfolio['stocks'][0]['shares'] == 50

def test_add_option_position(empty_manager):
    """Tests adding an option position."""
    empty_manager.add_option_position(
        ticker='SPY', option_type='put', strike=400.0, expiration='2024-09-20',
        contracts=2, premium=5.50, open_date='2023-08-01', strategy='cash_secured_put'
    )
    assert len(empty_manager.portfolio['options']) == 1
    assert empty_manager.portfolio['options'][0]['strategy'] == 'cash_secured_put'

def test_close_option_position(populated_manager):
    """Tests closing an open option position."""
    # There is one open option at index 0
    populated_manager.close_option_position(index=0, close_date='2023-09-01', outcome='expired')
    
    closed_option = populated_manager.portfolio['options'][0]
    assert closed_option['status'] == 'closed'
    assert closed_option['outcome'] == 'expired'

    # Test invalid index
    # Note: This will print "Invalid index: 99", but the test will pass
    populated_manager.close_option_position(index=99, close_date='2023-09-01')

def test_remove_stock_position(populated_manager):
    """Tests removing a stock position."""
    # There is one stock at index 0
    assert len(populated_manager.portfolio['stocks']) == 1
    populated_manager.remove_stock_position(index=0)
    assert len(populated_manager.portfolio['stocks']) == 0

    # Test invalid index
    populated_manager.remove_stock_position(index=99)

def test_get_dataframes(populated_manager):
    """Tests the get_*_dataframe methods."""
    stocks_df = populated_manager.get_stocks_dataframe()
    assert isinstance(stocks_df, pd.DataFrame)
    assert len(stocks_df) == 1

    # Get all options
    all_options_df = populated_manager.get_options_dataframe(status='all')
    assert len(all_options_df) == 1
    
    # Get open options
    open_options_df = populated_manager.get_options_dataframe(status='open')
    assert len(open_options_df) == 1

    # Get closed options
    closed_options_df = populated_manager.get_options_dataframe(status='closed')
    assert len(closed_options_df) == 0
    
    # Close the option and test again
    populated_manager.close_option_position(0, '2023-09-01')
    assert len(populated_manager.get_options_dataframe(status='open')) == 0
    assert len(populated_manager.get_options_dataframe(status='closed')) == 1

def test_get_covered_call_opportunities(empty_manager):
    """Tests the logic for finding covered call opportunities."""
    empty_manager.add_stock_position('LOW', shares=50, cost_basis=100, purchase_date='2023-01-01')
    empty_manager.add_stock_position('HIGH', shares=150, cost_basis=100, purchase_date='2023-01-01')
    
    opportunities = empty_manager.get_covered_call_opportunities()
    assert len(opportunities) == 1
    assert opportunities.iloc[0]['ticker'] == 'HIGH'
    assert opportunities.iloc[0]['contracts_available'] == 1

def test_analyze_portfolio_with_current_prices(populated_manager):
    """Tests the portfolio analysis with mock price data."""
    price_data = {'AAPL': 180.0} # AAPL cost basis is 150
    analysis = populated_manager.analyze_portfolio_with_current_prices(price_data)

    assert analysis['total_stock_value'] == 180.0 * 100
    assert analysis['total_stock_cost'] == 150.0 * 100
    assert analysis['total_gain_loss'] == 30.0 * 100
    assert len(analysis['stock_positions']) == 1
    assert len(analysis['option_positions']) == 1
    assert analysis['option_positions'][0]['days_remaining'] is not None

def test_export_to_csv(populated_manager, tmp_path):
    """Tests exporting the portfolio to CSV files."""
    output_dir = tmp_path / "export"
    populated_manager.export_to_csv(output_dir=str(output_dir))

    assert (output_dir / "stocks.csv").exists()
    assert (output_dir / "options.csv").exists()

def test_summary(populated_manager):
    """Tests the portfolio summary string generation."""
    summary_str = populated_manager.summary()
    assert "Stock Positions: 1" in summary_str
    assert "Open Options: 1" in summary_str
    assert "Closed Options: 0" in summary_str
