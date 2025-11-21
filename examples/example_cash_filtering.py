"""
Example: Cash Filtering for CSP Strategies
Demonstrates how available cash limits CSP opportunities
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.data.option_extractor import OptionDataExtractor
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
from tabulate import tabulate
import config


def demonstrate_cash_filtering():
    """Demonstrate CSP opportunities with and without cash filtering"""
    print("="*80)
    print("CASH SECURED PUT - CASH FILTERING DEMONSTRATION")
    print("="*80)

    # Initialize
    extractor = OptionDataExtractor()
    analyzer = CashSecuredPutAnalyzer()

    # Example tickers
    tickers = ['AAPL', 'MSFT', 'SPY']

    print(f"\nFetching options for: {', '.join(tickers)}")
    options_data = extractor.fetch_and_store_options(tickers, num_expirations=2)

    if options_data.empty:
        print("No data available.")
        return

    print("\n" + "="*80)
    print("SCENARIO 1: WITHOUT CASH FILTERING (All Opportunities)")
    print("="*80 + "\n")

    # Analyze without cash filtering
    results_no_filter = analyzer.get_top_opportunities(
        options_data,
        min_premium=0.5,
        min_annual_return=15.0,
        max_days=45,
        top_n=10
    )

    if not results_no_filter.empty:
        display_cols = ['ticker', 'strike', 'expiration', 'days_to_expiration',
                       'premium_received', 'annual_return', 'capital_required']
        display_cols = [col for col in display_cols if col in results_no_filter.columns]

        display_df = results_no_filter[display_cols].copy()
        display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
        display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
        display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")
        if 'capital_required' in display_df.columns:
            display_df['capital_required'] = display_df['capital_required'].apply(lambda x: f"${x:,.0f}")

        print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))
        print(f"\nTotal opportunities found: {len(results_no_filter)}")
    else:
        print("No opportunities found.")

    print("\n" + "="*80)
    print("SCENARIO 2: WITH CASH FILTERING")
    print("="*80)

    # Configure cash amounts
    available_cash = config.CAPITAL_SETTINGS['available_cash']
    reserve_cash = config.CAPITAL_SETTINGS['reserve_cash']
    deployable_cash = available_cash - reserve_cash
    max_per_position = config.CAPITAL_SETTINGS['max_cash_per_position']

    print(f"\nCash Configuration:")
    print(f"  Total Cash Available: ${available_cash:,.0f}")
    print(f"  Reserve Cash:         ${reserve_cash:,.0f}")
    print(f"  Deployable Cash:      ${deployable_cash:,.0f}")
    print(f"  Max per Position:     ${max_per_position:,.0f}")
    print()

    # Analyze with cash filtering
    results_with_filter = analyzer.get_top_opportunities(
        options_data,
        min_premium=0.5,
        min_annual_return=15.0,
        max_days=45,
        top_n=10,
        available_cash=deployable_cash,
        max_cash_per_position=max_per_position
    )

    if not results_with_filter.empty:
        display_cols = ['ticker', 'strike', 'expiration', 'days_to_expiration',
                       'premium_received', 'annual_return', 'max_affordable_contracts',
                       'total_capital_required', 'total_premium_received']
        display_cols = [col for col in display_cols if col in results_with_filter.columns]

        display_df = results_with_filter[display_cols].copy()
        display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
        display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
        display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")

        if 'total_capital_required' in display_df.columns:
            display_df['total_capital_required'] = display_df['total_capital_required'].apply(lambda x: f"${x:,.0f}")
        if 'total_premium_received' in display_df.columns:
            display_df['total_premium_received'] = display_df['total_premium_received'].apply(lambda x: f"${x:,.0f}")

        print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False))
        print(f"\nAffordable opportunities: {len(results_with_filter)}")

        # Calculate total deployment
        if 'total_capital_required' in results_with_filter.columns:
            total_capital = results_with_filter['total_capital_required'].sum()
            total_premium = results_with_filter['total_premium_received'].sum()

            print(f"\nIf you deployed all {len(results_with_filter)} positions:")
            print(f"  Total Capital Required: ${total_capital:,.0f}")
            print(f"  Total Premium Income:   ${total_premium:,.0f}")
            print(f"  Remaining Cash:         ${deployable_cash - total_capital:,.0f}")
    else:
        print("No affordable opportunities found.")

    print("\n" + "="*80)
    print("KEY INSIGHTS:")
    print("="*80)
    print("\n1. WITHOUT cash filtering: Shows ALL profitable opportunities")
    print("   - Good for research and comparing different tickers")
    print("   - May include positions you cannot afford")
    print()
    print("2. WITH cash filtering: Shows ONLY affordable opportunities")
    print("   - Respects your available cash constraints")
    print("   - Shows max contracts you can sell per position")
    print("   - Calculates total capital and premium for each trade")
    print()
    print("3. The 'max_affordable_contracts' column shows how many contracts")
    print("   you can sell based on your max_cash_per_position setting")
    print()
    print("4. To enable cash filtering in quick_start.py:")
    print("   - Set CAPITAL_SETTINGS['available_cash'] in config.py")
    print("   - Set CASH_SECURED_PUT_SETTINGS['use_available_cash'] = True")


def compare_different_cash_levels():
    """Compare opportunities at different cash levels"""
    print("\n\n" + "="*80)
    print("COMPARING OPPORTUNITIES AT DIFFERENT CASH LEVELS")
    print("="*80)

    extractor = OptionDataExtractor()
    analyzer = CashSecuredPutAnalyzer()

    # Fetch data for a single ticker
    ticker = 'SPY'
    print(f"\nAnalyzing {ticker} at different cash levels...")

    options_data = extractor.fetch_and_store_options([ticker], num_expirations=2)

    if options_data.empty:
        print("No data available.")
        return

    # Test different cash levels
    cash_levels = [
        ('$10,000', 10000, 10000),
        ('$25,000', 25000, 10000),
        ('$50,000', 50000, 15000),
        ('$100,000', 100000, 20000),
    ]

    for label, total_cash, max_per_pos in cash_levels:
        print(f"\n{'-'*80}")
        print(f"Cash Level: {label} (Max per position: ${max_per_pos:,})")
        print(f"{'-'*80}")

        results = analyzer.get_top_opportunities(
            options_data,
            min_premium=0.5,
            min_annual_return=15.0,
            max_days=45,
            top_n=5,
            available_cash=total_cash,
            max_cash_per_position=max_per_pos
        )

        if not results.empty:
            print(f"Found {len(results)} opportunities")

            # Show just a summary
            for idx, row in results.head(3).iterrows():
                strike = row['strike']
                contracts = row.get('max_affordable_contracts', 1)
                capital = row.get('total_capital_required', strike * 100)
                premium = row.get('total_premium_received', row['premium_received'] * 100)

                print(f"  • Strike ${strike:.0f}, {contracts} contracts = "
                      f"${capital:,.0f} capital, ${premium:,.0f} premium")
        else:
            print("  No affordable opportunities")


def main():
    """Main example"""
    print("\n" + "#"*80)
    print("# Cash Filtering Example for Cash Secured Puts")
    print("#"*80)

    demonstrate_cash_filtering()
    compare_different_cash_levels()

    print("\n\n" + "#"*80)
    print("# Example Complete!")
    print("#"*80)
    print("\nHow to customize for your account:")
    print("1. Edit config.py -> CAPITAL_SETTINGS section")
    print("2. Set 'available_cash' to your actual cash")
    print("3. Set 'max_cash_per_position' to limit position size")
    print("4. Set 'reserve_cash' to keep some cash uninvested")
    print("5. Enable filtering: CASH_SECURED_PUT_SETTINGS['use_available_cash'] = True")


if __name__ == "__main__":
    main()
