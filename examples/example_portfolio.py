"""
Example: Portfolio Management and Analysis
Demonstrates how to track positions and analyze opportunities
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.portfolio.portfolio_manager import PortfolioManager
from src.data.option_extractor import OptionDataExtractor
from src.strategies.covered_call import CoveredCallAnalyzer
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
from tabulate import tabulate


def setup_example_portfolio():
    """Create an example portfolio"""
    portfolio = PortfolioManager()

    print("Setting up example portfolio...\n")

    # Add some stock positions
    portfolio.add_stock_position(
        ticker='AAPL',
        shares=200,
        cost_basis=150.00,
        purchase_date='2024-01-15',
        notes='Core holding'
    )

    portfolio.add_stock_position(
        ticker='MSFT',
        shares=150,
        cost_basis=350.00,
        purchase_date='2024-02-01',
        notes='Tech allocation'
    )

    portfolio.add_stock_position(
        ticker='NVDA',
        shares=100,
        cost_basis=450.00,
        purchase_date='2024-03-10',
        notes='AI exposure'
    )

    # Add some option positions
    portfolio.add_option_position(
        ticker='AAPL',
        option_type='call',
        strike=160.00,
        expiration='2024-12-20',
        contracts=2,
        premium=3.50,
        open_date='2024-10-25',
        strategy='covered_call',
        notes='Monthly income'
    )

    portfolio.add_option_position(
        ticker='TSLA',
        option_type='put',
        strike=200.00,
        expiration='2024-11-15',
        contracts=1,
        premium=5.00,
        open_date='2024-10-20',
        strategy='cash_secured_put',
        notes='Entry position'
    )

    return portfolio


def analyze_portfolio_opportunities():
    """Analyze covered call opportunities for portfolio stocks"""
    print("\n" + "="*70)
    print("ANALYZING PORTFOLIO OPPORTUNITIES")
    print("="*70 + "\n")

    # Initialize
    portfolio = PortfolioManager()
    extractor = OptionDataExtractor()
    cc_analyzer = CoveredCallAnalyzer()

    # Get stocks that can be used for covered calls
    cc_stocks = portfolio.get_covered_call_opportunities()

    if cc_stocks.empty:
        print("No stocks with 100+ shares found for covered calls.")
        print("Add stock positions first using portfolio.add_stock_position()")
        return

    print("Stocks available for covered calls:")
    print(tabulate(cc_stocks, headers='keys', tablefmt='grid', showindex=False))
    print()

    # Fetch options for these tickers
    tickers = cc_stocks['ticker'].unique().tolist()
    print(f"\nFetching options data for: {', '.join(tickers)}")

    options_data = extractor.fetch_and_store_options(tickers, num_expirations=3)

    if options_data.empty:
        print("No options data found.")
        return

    # Analyze covered call opportunities
    print("\n" + "-"*70)
    print("TOP COVERED CALL OPPORTUNITIES FROM YOUR PORTFOLIO")
    print("-"*70)

    for ticker in tickers:
        ticker_options = options_data[options_data['ticker'] == ticker]
        ticker_cc = cc_analyzer.get_top_opportunities(
            ticker_options,
            min_premium=0.5,
            min_annual_return=15.0,
            max_days=45,
            top_n=5
        )

        if not ticker_cc.empty:
            stock_info = cc_stocks[cc_stocks['ticker'] == ticker].iloc[0]
            print(f"\n{ticker} - {stock_info['shares']} shares ({stock_info['contracts_available']} contracts available)")
            print(f"Cost Basis: ${stock_info['cost_basis']:.2f}")

            display_cols = ['strike', 'expiration', 'days_to_expiration',
                          'premium_received', 'annual_return', 'monthly_return',
                          'downside_protection', 'volume']

            display_cols = [col for col in display_cols if col in ticker_cc.columns]
            display_df = ticker_cc[display_cols].copy()

            # Format
            display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
            display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
            display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")
            display_df['monthly_return'] = display_df['monthly_return'].apply(lambda x: f"{x:.1f}%")
            display_df['downside_protection'] = display_df['downside_protection'].apply(lambda x: f"{x:.1f}%")

            print(tabulate(display_df.head(3), headers='keys', tablefmt='grid', showindex=False))


def analyze_put_opportunities():
    """Find cash secured put opportunities"""
    print("\n" + "="*70)
    print("CASH SECURED PUT OPPORTUNITIES")
    print("="*70 + "\n")

    extractor = OptionDataExtractor()
    csp_analyzer = CashSecuredPutAnalyzer()

    # Tickers you're interested in acquiring
    target_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

    print(f"Finding put opportunities for: {', '.join(target_tickers)}\n")

    options_data = extractor.fetch_and_store_options(target_tickers, num_expirations=3)

    if options_data.empty:
        print("No options data found.")
        return

    # Find best opportunities
    csp_results = csp_analyzer.get_top_opportunities(
        options_data,
        min_premium=1.0,
        min_annual_return=20.0,
        max_days=45,
        top_n=15
    )

    if csp_results.empty:
        print("No opportunities found matching criteria.")
        return

    # Display
    display_cols = [
        'ticker', 'current_stock_price', 'strike', 'expiration',
        'days_to_expiration', 'premium_received', 'annual_return',
        'net_purchase_price', 'discount_from_current', 'volume'
    ]

    display_cols = [col for col in display_cols if col in csp_results.columns]
    display_df = csp_results[display_cols].copy()

    # Format
    display_df['current_stock_price'] = display_df['current_stock_price'].apply(lambda x: f"${x:.2f}")
    display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
    display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
    display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")
    display_df['net_purchase_price'] = display_df['net_purchase_price'].apply(lambda x: f"${x:.2f}")
    display_df['discount_from_current'] = display_df['discount_from_current'].apply(lambda x: f"{x:.1f}%")

    print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))


def view_portfolio():
    """View current portfolio"""
    portfolio = PortfolioManager()

    print("\n" + "="*70)
    print(portfolio.summary())

    stocks = portfolio.get_stocks_dataframe()
    if not stocks.empty:
        print("\nSTOCK POSITIONS:")
        print(tabulate(stocks, headers='keys', tablefmt='grid', showindex=True))

        # Get current prices and analyze
        print("\n" + "-"*70)
        print("Fetching current prices...")
        extractor = OptionDataExtractor()

        price_data = {}
        for ticker in stocks['ticker'].unique():
            price = extractor.get_current_price(ticker)
            if price:
                price_data[ticker] = price

        if price_data:
            analysis = portfolio.analyze_portfolio_with_current_prices(price_data)

            print("\nPORTFOLIO ANALYSIS:")
            print(f"Total Value: ${analysis['total_stock_value']:,.2f}")
            print(f"Total Cost:  ${analysis['total_stock_cost']:,.2f}")
            print(f"Gain/Loss:   ${analysis['total_gain_loss']:,.2f} ({analysis['total_gain_loss_pct']:.2f}%)")

            if analysis['stock_positions']:
                positions_df = pd.DataFrame(analysis['stock_positions'])
                print("\nPOSITION DETAILS:")

                display_df = positions_df.copy()
                display_df['cost_basis'] = display_df['cost_basis'].apply(lambda x: f"${x:.2f}")
                display_df['current_price'] = display_df['current_price'].apply(lambda x: f"${x:.2f}")
                display_df['position_value'] = display_df['position_value'].apply(lambda x: f"${x:,.2f}")
                display_df['position_cost'] = display_df['position_cost'].apply(lambda x: f"${x:,.2f}")
                display_df['gain_loss'] = display_df['gain_loss'].apply(lambda x: f"${x:,.2f}")
                display_df['gain_loss_pct'] = display_df['gain_loss_pct'].apply(lambda x: f"{x:.2f}%")

                print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))

    open_options = portfolio.get_options_dataframe(status='open')
    if not open_options.empty:
        print("\nOPEN OPTION POSITIONS:")
        print(tabulate(open_options, headers='keys', tablefmt='grid', showindex=True))


def main():
    """Main example function"""
    print("\n" + "#"*70)
    print("# Portfolio Management & Analysis Example")
    print("#"*70)

    # Uncomment to create example portfolio
    # setup_example_portfolio()

    # View current portfolio
    view_portfolio()

    # Analyze covered call opportunities for portfolio stocks
    # analyze_portfolio_opportunities()

    # Find cash secured put opportunities
    # analyze_put_opportunities()

    print("\n" + "#"*70)
    print("# Example Complete!")
    print("#"*70)
    print("\nTo manage your portfolio:")
    print("1. Use setup_example_portfolio() to create sample data")
    print("2. Use portfolio.add_stock_position() to add your stocks")
    print("3. Use portfolio.add_option_position() to track your options")
    print("4. Run analyze_portfolio_opportunities() to find covered calls")
    print("5. Run analyze_put_opportunities() to find puts")


if __name__ == "__main__":
    import pandas as pd
    main()
