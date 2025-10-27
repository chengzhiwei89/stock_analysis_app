"""
Setup My Portfolio
Add your current holdings and analyze opportunities
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.portfolio.portfolio_manager import PortfolioManager
from src.data.option_extractor import OptionDataExtractor
from src.data.recommendations_manager import RecommendationsManager
from src.strategies.covered_call import CoveredCallAnalyzer
from tabulate import tabulate
from datetime import datetime
import config


def setup_my_portfolio():
    """Add your current holdings to the portfolio"""
    portfolio = PortfolioManager()

    print("="*80)
    print("SETTING UP YOUR PORTFOLIO")
    print("="*80 + "\n")

    # Add your NVDA position
    portfolio.add_stock_position(
        ticker='NVDA',
        shares=120,
        cost_basis=100.00,
        purchase_date='2024-01-01',  # Adjust to your actual purchase date
        notes='Core AI holding - Can sell 1 covered call contract'
    )

    print("\nPortfolio setup complete!")
    return portfolio


def analyze_nvda_covered_calls():
    """Analyze covered call opportunities for your NVDA shares"""
    print("\n" + "="*80)
    print("NVDA COVERED CALL ANALYSIS")
    print("="*80)

    # Initialize
    extractor = OptionDataExtractor()
    analyzer = CoveredCallAnalyzer()

    # Get current NVDA price
    print("\nFetching NVDA data...")
    current_price = extractor.get_current_price('NVDA')
    if current_price:
        print(f"Current NVDA price: ${current_price:.2f}")
        print(f"Your position: 120 shares @ $100 average")
        print(f"Current value: ${current_price * 120:,.2f}")
        print(f"Unrealized P&L: ${(current_price - 100) * 120:,.2f} ({((current_price - 100) / 100 * 100):.1f}%)")

    # Fetch NVDA options
    print("\nFetching NVDA option chains...")
    options_data = extractor.fetch_and_store_options(['NVDA'], num_expirations=6)

    if options_data.empty:
        print("Could not fetch options data.")
        return

    # Analyze covered calls
    print("\n" + "-"*80)
    print("COVERED CALL OPPORTUNITIES FOR YOUR 120 NVDA SHARES")
    print("-"*80)
    print("\nNote: You can sell 1 contract (100 shares) with 20 shares remaining uncovered")
    print()

    # Get opportunities with different timeframes
    timeframes = [
        ("Weekly (7-14 days)", 7, 14),
        ("Bi-Weekly (14-21 days)", 14, 21),
        ("Monthly (30-45 days)", 30, 45),
    ]

    for label, min_days, max_days in timeframes:
        print(f"\n{label}:")
        print("-" * 60)

        # Filter options for this timeframe
        timeframe_options = options_data[
            (options_data['ticker'] == 'NVDA') &
            (options_data['option_type'] == 'call')
        ].copy()

        # Analyze
        results = analyzer.analyze_covered_calls(
            timeframe_options,
            min_premium=0.5,
            min_annual_return=0,  # Show all for comparison
            max_days=max_days
        )

        if not results.empty:
            # Filter to this timeframe
            results = results[results['days_to_expiration'] >= min_days]

            if not results.empty:
                # Show top 5 for this timeframe
                display_cols = [
                    'strike', 'expiration', 'days_to_expiration',
                    'premium_received', 'annual_return', 'monthly_return',
                    'max_profit_pct', 'downside_protection', 'distance_pct'
                ]

                display_cols = [col for col in display_cols if col in results.columns]
                display_df = results[display_cols].head(5).copy()

                # Format
                display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
                display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f} (${x*100:.0f}/contract)")
                display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")
                display_df['monthly_return'] = display_df['monthly_return'].apply(lambda x: f"{x:.1f}%")
                if 'max_profit_pct' in display_df.columns:
                    display_df['max_profit_pct'] = display_df['max_profit_pct'].apply(lambda x: f"{x:.1f}%")
                if 'downside_protection' in display_df.columns:
                    display_df['downside_protection'] = display_df['downside_protection'].apply(lambda x: f"{x:.1f}%")
                display_df['distance_pct'] = display_df['distance_pct'].apply(lambda x: f"{x:.1f}%")

                print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False, maxcolwidths=20))

                # Show best opportunity
                best = results.iloc[0]
                print(f"\nBest opportunity: Sell ${best['strike']:.0f} call expiring {best['expiration']}")
                print(f"  Premium: ${best['premium_received']:.2f}/share = ${best['premium_received']*100:.0f} for 1 contract")
                print(f"  Annual return: {best['annual_return']:.1f}%")
                if current_price:
                    print(f"  Breakeven: ${current_price - best['premium_received']:.2f} (down {(best['premium_received']/current_price*100):.1f}%)")
            else:
                print("  No opportunities in this timeframe")
        else:
            print("  No opportunities found")

    # Conservative recommendations
    print("\n" + "="*80)
    print("RECOMMENDED STRATEGIES FOR YOUR POSITION")
    print("="*80)

    # Strategy 1: Conservative monthly income
    print("\n1. CONSERVATIVE MONTHLY INCOME:")
    print("   - Sell 30-45 DTE calls at 5-10% OTM")
    print("   - Target: 1-2% monthly return")
    print("   - Keep 20 shares uncovered for upside")

    # Strategy 2: Aggressive weekly income
    print("\n2. AGGRESSIVE WEEKLY INCOME:")
    print("   - Sell 7-14 DTE calls at 2-5% OTM")
    print("   - Target: 0.5-1% weekly return (26-52% annual)")
    print("   - Higher chance of assignment but more premium")

    # Strategy 3: Hold and protect
    print("\n3. HOLD & PROTECT:")
    print("   - Sell 30-45 DTE calls at 10-15% OTM")
    print("   - Target: 0.5-1% monthly return")
    print("   - Low assignment risk, downside protection")

    print("\n" + "-"*80)
    print("IMPORTANT NOTES:")
    print("-"*80)
    print("• You have 120 shares, so you can sell 1 contract (covers 100 shares)")
    print("• 20 shares will remain uncovered and keep full upside potential")
    print("• If assigned, you'll sell 100 shares at the strike price + premium")
    print(f"• Your cost basis is $100, so any strike above $100 is profitable")
    print("• Consider your tax situation - this may trigger capital gains")

    # Auto-save all NVDA recommendations
    if config.RECOMMENDATIONS_SETTINGS['auto_save'] and options_data is not None:
        print("\n" + "-"*80)
        print("Saving NVDA recommendations...")
        rec_manager = RecommendationsManager(config.RECOMMENDATIONS_SETTINGS['save_directory'])

        # Get all results combined
        all_results = analyzer.analyze_covered_calls(
            options_data,
            min_premium=0.5,
            min_annual_return=0,
            max_days=60
        )

        if not all_results.empty:
            rec_manager.save_covered_call_recommendations(
                all_results,
                tickers=['NVDA'],
                criteria={'for_position': '120 shares @ $100 cost basis'},
                notes='Covered call opportunities for NVDA position (120 shares)'
            )


def show_portfolio_summary():
    """Show current portfolio"""
    portfolio = PortfolioManager()

    print("\n" + "="*80)
    print(portfolio.summary())

    stocks = portfolio.get_stocks_dataframe()
    if not stocks.empty:
        print("STOCK POSITIONS:")
        print("-"*80)
        print(tabulate(stocks, headers='keys', tablefmt='grid', showindex=True))

        # Get current prices
        print("\n" + "-"*80)
        print("CURRENT VALUATION:")
        print("-"*80)

        extractor = OptionDataExtractor()
        price_data = {}
        for ticker in stocks['ticker'].unique():
            price = extractor.get_current_price(ticker)
            if price:
                price_data[ticker] = price

        if price_data:
            analysis = portfolio.analyze_portfolio_with_current_prices(price_data)

            print(f"\nTotal Value: ${analysis['total_stock_value']:,.2f}")
            print(f"Total Cost:  ${analysis['total_stock_cost']:,.2f}")
            print(f"Gain/Loss:   ${analysis['total_gain_loss']:,.2f} ({analysis['total_gain_loss_pct']:.2f}%)")

            if analysis['stock_positions']:
                print("\nPOSITION DETAILS:")
                for pos in analysis['stock_positions']:
                    print(f"\n{pos['ticker']}:")
                    print(f"  Shares: {pos['shares']}")
                    print(f"  Cost Basis: ${pos['cost_basis']:.2f}")
                    print(f"  Current Price: ${pos['current_price']:.2f}")
                    print(f"  Value: ${pos['position_value']:,.2f}")
                    print(f"  Gain/Loss: ${pos['gain_loss']:,.2f} ({pos['gain_loss_pct']:.1f}%)")

        # Show covered call opportunities
        cc_opps = portfolio.get_covered_call_opportunities()
        if not cc_opps.empty:
            print("\n" + "-"*80)
            print("STOCKS AVAILABLE FOR COVERED CALLS:")
            print("-"*80)
            print(tabulate(cc_opps, headers='keys', tablefmt='grid', showindex=False))

    # Show open options
    options = portfolio.get_options_dataframe(status='open')
    if not options.empty:
        print("\nOPEN OPTION POSITIONS:")
        print("-"*80)
        print(tabulate(options, headers='keys', tablefmt='grid', showindex=True))


def main():
    """Main function"""
    print("\n" + "#"*80)
    print("# MY PORTFOLIO SETUP & ANALYSIS")
    print("#"*80)

    # Setup portfolio (run this once)
    print("\n[Step 1] Setting up portfolio...")
    portfolio = setup_my_portfolio()

    # Show portfolio summary
    print("\n[Step 2] Portfolio Summary...")
    show_portfolio_summary()

    # Analyze NVDA covered calls
    print("\n[Step 3] Analyzing NVDA Covered Call Opportunities...")
    analyze_nvda_covered_calls()

    print("\n\n" + "#"*80)
    print("# ANALYSIS COMPLETE!")
    print("#"*80)

    print("\nNext Steps:")
    print("1. Review the covered call opportunities above")
    print("2. Choose a strategy that fits your goals:")
    print("   - Conservative: 30-45 DTE, 5-10% OTM, lower premium")
    print("   - Aggressive: 7-14 DTE, 2-5% OTM, higher premium")
    print("3. Log into your broker and sell the call option")
    print("4. Track the position using portfolio.add_option_position()")
    print("\nExample to track a position:")
    print("""
    portfolio.add_option_position(
        ticker='NVDA',
        option_type='call',
        strike=150.00,
        expiration='2024-12-20',
        contracts=1,
        premium=3.50,
        open_date='2024-10-25',
        strategy='covered_call',
        notes='Monthly income strategy'
    )
    """)


if __name__ == "__main__":
    main()
