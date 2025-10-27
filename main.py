"""
Stock Options Analysis App
Main application for analyzing covered calls and cash secured puts
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.data.option_extractor import OptionDataExtractor
from src.strategies.covered_call import CoveredCallAnalyzer
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
from src.portfolio.portfolio_manager import PortfolioManager
from tabulate import tabulate
import pandas as pd


class OptionsAnalysisApp:
    """Main application for options analysis"""

    def __init__(self):
        self.extractor = OptionDataExtractor()
        self.cc_analyzer = CoveredCallAnalyzer()
        self.csp_analyzer = CashSecuredPutAnalyzer()
        self.portfolio = PortfolioManager()

    def fetch_options_data(self, tickers: list, num_expirations: int = 4):
        """
        Fetch options data for given tickers

        Args:
            tickers: List of ticker symbols
            num_expirations: Number of expiration dates to fetch
        """
        print("\n" + "="*70)
        print("FETCHING OPTIONS DATA")
        print("="*70)

        options_df = self.extractor.fetch_and_store_options(
            tickers=tickers,
            num_expirations=num_expirations
        )

        return options_df

    def analyze_covered_calls(self, options_df: pd.DataFrame,
                             min_premium: float = 0.5,
                             min_annual_return: float = 15.0,
                             max_days: int = 45,
                             top_n: int = 15):
        """Analyze covered call opportunities"""
        print("\n" + "="*70)
        print("COVERED CALL OPPORTUNITIES")
        print("="*70)
        print(f"Criteria: Min Premium=${min_premium}, Min Annual Return={min_annual_return}%, Max Days={max_days}")
        print()

        results = self.cc_analyzer.get_top_opportunities(
            options_df,
            min_premium=min_premium,
            min_annual_return=min_annual_return,
            max_days=max_days,
            top_n=top_n
        )

        if results.empty:
            print("No opportunities found matching criteria.")
            return results

        # Display results
        display_cols = [
            'ticker', 'current_stock_price', 'strike', 'expiration',
            'days_to_expiration', 'premium_received', 'annual_return',
            'monthly_return', 'downside_protection', 'distance_pct',
            'volume', 'openInterest'
        ]

        display_cols = [col for col in display_cols if col in results.columns]
        display_df = results[display_cols].copy()

        # Format for display
        display_df['current_stock_price'] = display_df['current_stock_price'].apply(lambda x: f"${x:.2f}")
        display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
        display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
        display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")
        display_df['monthly_return'] = display_df['monthly_return'].apply(lambda x: f"{x:.1f}%")
        display_df['downside_protection'] = display_df['downside_protection'].apply(lambda x: f"{x:.1f}%")
        display_df['distance_pct'] = display_df['distance_pct'].apply(lambda x: f"{x:.1f}%")

        print(tabulate(display_df.head(top_n), headers='keys', tablefmt='grid', showindex=False))

        # Summary by ticker
        print("\n" + "-"*70)
        print("SUMMARY BY TICKER")
        print("-"*70)
        summary = self.cc_analyzer.summarize_by_ticker(results)
        print(tabulate(summary, headers='keys', tablefmt='grid'))

        return results

    def analyze_cash_secured_puts(self, options_df: pd.DataFrame,
                                 min_premium: float = 0.5,
                                 min_annual_return: float = 15.0,
                                 max_days: int = 45,
                                 top_n: int = 15):
        """Analyze cash secured put opportunities"""
        print("\n" + "="*70)
        print("CASH SECURED PUT OPPORTUNITIES")
        print("="*70)
        print(f"Criteria: Min Premium=${min_premium}, Min Annual Return={min_annual_return}%, Max Days={max_days}")
        print()

        results = self.csp_analyzer.get_top_opportunities(
            options_df,
            min_premium=min_premium,
            min_annual_return=min_annual_return,
            max_days=max_days,
            top_n=top_n
        )

        if results.empty:
            print("No opportunities found matching criteria.")
            return results

        # Display results
        display_cols = [
            'ticker', 'current_stock_price', 'strike', 'expiration',
            'days_to_expiration', 'premium_received', 'annual_return',
            'monthly_return', 'net_purchase_price', 'discount_from_current',
            'volume', 'openInterest'
        ]

        display_cols = [col for col in display_cols if col in results.columns]
        display_df = results[display_cols].copy()

        # Format for display
        display_df['current_stock_price'] = display_df['current_stock_price'].apply(lambda x: f"${x:.2f}")
        display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
        display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
        display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")
        display_df['monthly_return'] = display_df['monthly_return'].apply(lambda x: f"{x:.1f}%")
        display_df['net_purchase_price'] = display_df['net_purchase_price'].apply(lambda x: f"${x:.2f}")
        display_df['discount_from_current'] = display_df['discount_from_current'].apply(lambda x: f"{x:.1f}%")

        print(tabulate(display_df.head(top_n), headers='keys', tablefmt='grid', showindex=False))

        # Summary by ticker
        print("\n" + "-"*70)
        print("SUMMARY BY TICKER")
        print("-"*70)
        summary = self.csp_analyzer.summarize_by_ticker(results)
        print(tabulate(summary, headers='keys', tablefmt='grid'))

        return results

    def show_portfolio(self):
        """Display portfolio information"""
        print("\n" + "="*70)
        print(self.portfolio.summary())
        print("="*70)

        # Show stock positions
        stocks = self.portfolio.get_stocks_dataframe()
        if not stocks.empty:
            print("\nSTOCK POSITIONS:")
            print(tabulate(stocks, headers='keys', tablefmt='grid', showindex=True))

        # Show open options
        open_options = self.portfolio.get_options_dataframe(status='open')
        if not open_options.empty:
            print("\nOPEN OPTION POSITIONS:")
            print(tabulate(open_options, headers='keys', tablefmt='grid', showindex=True))

        # Show covered call opportunities from portfolio
        cc_opps = self.portfolio.get_covered_call_opportunities()
        if not cc_opps.empty:
            print("\nSTOCKS AVAILABLE FOR COVERED CALLS:")
            print(tabulate(cc_opps, headers='keys', tablefmt='grid', showindex=False))


def main():
    """Example usage of the app"""
    app = OptionsAnalysisApp()

    # Example 1: Analyze options for popular stocks
    print("\n" + "#"*70)
    print("# Stock Options Analysis App")
    print("# Covered Calls & Cash Secured Puts")
    print("#"*70)

    # Define tickers to analyze
    tickers = ['AAPL', 'MSFT', 'NVDA', 'AMD', 'TSLA']

    # Fetch options data
    options_data = app.fetch_options_data(tickers, num_expirations=4)

    if not options_data.empty:
        # Analyze covered calls
        cc_results = app.analyze_covered_calls(
            options_data,
            min_premium=1.0,
            min_annual_return=20.0,
            max_days=45,
            top_n=15
        )

        # Analyze cash secured puts
        csp_results = app.analyze_cash_secured_puts(
            options_data,
            min_premium=1.0,
            min_annual_return=20.0,
            max_days=45,
            top_n=15
        )

    # Example 2: Portfolio management
    print("\n" + "#"*70)
    print("# Portfolio Management Example")
    print("#"*70)

    # Show current portfolio
    app.show_portfolio()

    print("\n" + "#"*70)
    print("# Analysis Complete!")
    print("#"*70)
    print("\nTo use this app:")
    print("1. Modify the 'tickers' list with your desired stocks")
    print("2. Adjust min_premium, min_annual_return, and max_days criteria")
    print("3. Add your positions using portfolio.add_stock_position() and portfolio.add_option_position()")
    print("4. Run the analysis to find opportunities")
    print("\nData is saved in the 'data' directory for further analysis.")


if __name__ == "__main__":
    main()
