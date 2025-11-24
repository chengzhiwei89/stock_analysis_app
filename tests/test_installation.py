"""
Test Installation
Quick test to verify all components are working.
This test makes live network calls and is intended to be a diagnostic tool.
"""
import sys
import os
import pytest

# Add project root to path to allow imports from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_imports():
    """Test if all core modules can be imported."""
    print("Testing imports...")

    import yfinance
    print("[OK] yfinance")

    import pandas
    print("[OK] pandas")

    import numpy
    print("[OK] numpy")

    from src.data.option_extractor import OptionDataExtractor
    print("[OK] OptionDataExtractor")

    from src.strategies.covered_call import CoveredCallAnalyzer
    print("[OK] CoveredCallAnalyzer")

    from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
    print("[OK] CashSecuredPutAnalyzer")

    from src.portfolio.portfolio_manager import PortfolioManager
    print("[OK] PortfolioManager")

    # If all imports succeed, the test passes implicitly
    assert True

@pytest.mark.network
def test_basic_functionality():
    """Test basic functionality requiring a network connection."""
    print("\nTesting basic functionality...")

    from src.data.option_extractor import OptionDataExtractor
    extractor = OptionDataExtractor()

    # Test getting available expirations for a simple ticker
    print("Fetching expiration dates for SPY...")
    expirations = extractor.get_available_expirations('SPY')

    assert expirations, "No expirations found (this might be a network issue)"
    print(f"[OK] Found {len(expirations)} expiration dates")
    print(f"  Next 3 expirations: {', '.join(expirations[:3])}")

    # Test getting current price
    print("\nFetching current price for SPY...")
    price = extractor.get_current_price('SPY')

    assert price, "Could not fetch price (this might be a network issue)"
    print(f"[OK] Current SPY price: ${price:.2f}")

@pytest.mark.local
def test_portfolio_management():
    """Test portfolio management functionality locally."""
    print("\nTesting portfolio management...")

    from src.portfolio.portfolio_manager import PortfolioManager
    
    test_portfolio_path = "data/portfolio/test_portfolio.json"

    # Ensure the test file doesn't exist before we start
    if os.path.exists(test_portfolio_path):
        os.remove(test_portfolio_path)

    # Create a test portfolio
    portfolio = PortfolioManager(portfolio_file=test_portfolio_path)
    print("[OK] Portfolio manager initialized")

    # Test adding a stock position
    portfolio.add_stock_position(
        ticker='TEST',
        shares=100,
        cost_basis=100.0,
        purchase_date='2024-01-01',
        notes='Test position'
    )
    print("[OK] Stock position added")

    # Test retrieving positions
    stocks = portfolio.get_stocks_dataframe()
    assert not stocks.empty, "Failed to retrieve stock positions"
    assert len(stocks) == 1, "Incorrect number of stock positions retrieved"
    print(f"[OK] Retrieved {len(stocks)} stock position(s)")

    # Clean up test file
    if os.path.exists(test_portfolio_path):
        os.remove(test_portfolio_path)
        print("[OK] Test cleanup complete")
