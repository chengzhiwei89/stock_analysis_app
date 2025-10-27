"""
Test Installation
Quick test to verify all components are working
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")

    try:
        import yfinance
        print("[OK] yfinance")
    except ImportError as e:
        print(f"[FAIL] yfinance: {e}")
        return False

    try:
        import pandas
        print("[OK] pandas")
    except ImportError as e:
        print(f"[FAIL] pandas: {e}")
        return False

    try:
        import numpy
        print("[OK] numpy")
    except ImportError as e:
        print(f"[FAIL] numpy: {e}")
        return False

    try:
        from src.data.option_extractor import OptionDataExtractor
        print("[OK] OptionDataExtractor")
    except ImportError as e:
        print(f"[FAIL] OptionDataExtractor: {e}")
        return False

    try:
        from src.strategies.covered_call import CoveredCallAnalyzer
        print("[OK] CoveredCallAnalyzer")
    except ImportError as e:
        print(f"[FAIL] CoveredCallAnalyzer: {e}")
        return False

    try:
        from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
        print("[OK] CashSecuredPutAnalyzer")
    except ImportError as e:
        print(f"[FAIL] CashSecuredPutAnalyzer: {e}")
        return False

    try:
        from src.portfolio.portfolio_manager import PortfolioManager
        print("[OK] PortfolioManager")
    except ImportError as e:
        print(f"[FAIL] PortfolioManager: {e}")
        return False

    return True


def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")

    try:
        from src.data.option_extractor import OptionDataExtractor
        extractor = OptionDataExtractor()

        # Test getting available expirations for a simple ticker
        print("Fetching expiration dates for SPY...")
        expirations = extractor.get_available_expirations('SPY')

        if expirations:
            print(f"[OK] Found {len(expirations)} expiration dates")
            print(f"  Next 3 expirations: {', '.join(expirations[:3])}")
        else:
            print("[FAIL] No expirations found (this might be a network issue)")
            return False

        # Test getting current price
        print("\nFetching current price for SPY...")
        price = extractor.get_current_price('SPY')

        if price:
            print(f"[OK] Current SPY price: ${price:.2f}")
        else:
            print("[FAIL] Could not fetch price (this might be a network issue)")
            return False

    except Exception as e:
        print(f"[FAIL] Error during functionality test: {e}")
        return False

    return True


def test_portfolio():
    """Test portfolio management"""
    print("\nTesting portfolio management...")

    try:
        from src.portfolio.portfolio_manager import PortfolioManager

        # Create a test portfolio
        portfolio = PortfolioManager(portfolio_file="data/portfolio/test_portfolio.json")

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
        if not stocks.empty:
            print(f"[OK] Retrieved {len(stocks)} stock position(s)")
        else:
            print("[FAIL] Failed to retrieve stock positions")
            return False

        # Clean up test file
        import os
        if os.path.exists("data/portfolio/test_portfolio.json"):
            os.remove("data/portfolio/test_portfolio.json")
            print("[OK] Test cleanup complete")

    except Exception as e:
        print(f"[FAIL] Error during portfolio test: {e}")
        return False

    return True


def main():
    """Run all tests"""
    print("="*60)
    print("Stock Options Analysis App - Installation Test")
    print("="*60)
    print()

    # Run tests
    imports_ok = test_imports()
    if not imports_ok:
        print("\n[FAIL] Import test failed!")
        print("Please run: pip install -r requirements.txt")
        return

    functionality_ok = test_basic_functionality()
    if not functionality_ok:
        print("\n[FAIL] Functionality test failed!")
        print("This might be a network issue. Check your internet connection.")

    portfolio_ok = test_portfolio()
    if not portfolio_ok:
        print("\n[FAIL] Portfolio test failed!")

    # Summary
    print("\n" + "="*60)
    if imports_ok and functionality_ok and portfolio_ok:
        print("[SUCCESS] ALL TESTS PASSED!")
        print("="*60)
        print("\nYour installation is working correctly!")
        print("\nNext steps:")
        print("1. Edit config.py to set your preferences")
        print("2. Run: python quick_start.py")
        print("3. Or run: python main.py")
        print("4. Check README.md for detailed documentation")
    else:
        print("[FAIL] SOME TESTS FAILED")
        print("="*60)
        print("\nPlease check the errors above and:")
        print("1. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check your internet connection")
        print("3. Verify you have access to Yahoo Finance")


if __name__ == "__main__":
    main()
