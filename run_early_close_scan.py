"""
Run CSP Scan Optimized for Early Close Strategy
Finds 45-60 DTE options perfect for closing at 50-75% profit
"""
from src.data.option_data_extractor import OptionDataExtractor
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
from src.data.recommendations_manager import RecommendationsManager
import config
from tabulate import tabulate


def run_early_close_scan():
    """Run CSP scan optimized for early close strategy"""
    print("\n" + "="*80)
    print("EARLY CLOSE STRATEGY - CSP SCAN")
    print("Target: 45-60 DTE options for closing at 50-75% profit")
    print("="*80)

    # Initialize
    extractor = OptionDataExtractor()
    analyzer = CashSecuredPutAnalyzer()

    # Early close optimized settings
    tickers = config.WATCHLIST
    settings = {
        'min_premium': 1.00,           # Higher premiums
        'min_annual_return': 12.0,     # Lower threshold (we'll beat this)
        'min_days': 40,                # 45-60 day sweet spot
        'max_days': 65,
        'min_prob_otm': 65.0,          # Moderate
        'max_delta': -0.35,
        'min_volume': 500,             # CRITICAL for closing
    }

    # Get cash settings
    available_cash = config.get_deployable_cash()
    max_cash_per_position = config.CAPITAL_SETTINGS['max_cash_per_position']

    print(f"\nScanning {len(tickers)} tickers: {', '.join(tickers)}")
    print(f"\nCRITERIA (Optimized for Early Close):")
    print(f"  Days to Expiration: {settings['min_days']}-{settings['max_days']} (target 45-60 DTE)")
    print(f"  Min Premium: ${settings['min_premium']:.2f} (bigger premiums = better targets)")
    print(f"  Min Volume: {settings['min_volume']} (MUST HAVE for easy closing)")
    print(f"  Min Prob OTM: {settings['min_prob_otm']}% (moderate - you'll close early)")
    print(f"  Max Delta: {settings['max_delta']} (will improve as you wait)")
    print(f"  Available Cash: ${available_cash:,.0f}")

    print("\nSTRATEGY:")
    print("  ✓ Sell these 45-60 DTE options")
    print("  ✓ Close at 50% profit (typically 10-20 days)")
    print("  ✓ Close at 75% profit (if achieved quickly)")
    print("  ✓ Force close at 21 DTE if targets not hit")
    print("  ✓ Immediately roll to new position")

    # Fetch data
    print("\nFetching options data...")
    options_data = extractor.fetch_and_store_options(
        tickers,
        num_expirations=8  # More expirations to find 45-60 DTE range
    )

    if options_data.empty:
        print("No data available.")
        return

    # Analyze
    print("\nAnalyzing opportunities...")

    # Use quality tickers
    quality_tickers = config.CSP_QUALITY_TICKERS

    results = analyzer.get_top_opportunities(
        options_data,
        min_premium=settings['min_premium'],
        min_annual_return=settings['min_annual_return'],
        min_days=settings['min_days'],
        max_days=settings['max_days'],
        min_prob_otm=settings['min_prob_otm'],
        min_volume=settings['min_volume'],
        quality_tickers=quality_tickers,
        max_delta=settings['max_delta'],
        top_n=20,
        available_cash=available_cash,
        max_cash_per_position=max_cash_per_position
    )

    if results.empty:
        print("\nNo opportunities found matching criteria.")
        print("\nTry adjusting settings:")
        print("  - Lower min_volume to 250")
        print("  - Expand days range to 35-70")
        print("  - Lower min_premium to 0.75")
        return

    # Add early close targets to results
    results['target_50%'] = (results['premium_received'] * 0.50).round(2)
    results['target_75%'] = (results['premium_received'] * 0.25).round(2)
    results['profit_50%'] = (results['premium_received'] * 0.50 * 100).round(0)
    results['profit_75%'] = (results['premium_received'] * 0.75 * 100).round(0)

    # Display results
    print(f"\n{'='*80}")
    print(f"TOP 20 EARLY CLOSE OPPORTUNITIES")
    print(f"{'='*80}\n")

    display_cols = [
        'ticker', 'current_stock_price', 'strike', 'expiration',
        'days_to_expiration', 'premium_received', 'target_50%', 'target_75%',
        'prob_otm', 'delta', 'volume'
    ]

    display_cols = [col for col in display_cols if col in results.columns]
    display_df = results[display_cols].copy()

    # Format
    display_df['current_stock_price'] = display_df['current_stock_price'].apply(lambda x: f"${x:.2f}")
    display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
    display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
    display_df['target_50%'] = display_df['target_50%'].apply(lambda x: f"${x:.2f}")
    display_df['target_75%'] = display_df['target_75%'].apply(lambda x: f"${x:.2f}")

    if 'prob_otm' in display_df.columns:
        display_df['prob_otm'] = display_df['prob_otm'].apply(lambda x: f"{x:.1f}%")
    if 'delta' in display_df.columns:
        display_df['delta'] = display_df['delta'].apply(lambda x: f"{x:.3f}")

    print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False, maxcolwidths=15))

    # Detailed recommendations
    print(f"\n{'='*80}")
    print("DETAILED EARLY CLOSE ANALYSIS - TOP 5")
    print(f"{'='*80}\n")

    for i, (_, row) in enumerate(results.head(5).iterrows(), 1):
        print(f"\n{i}. {row['ticker']} ${row['strike']:.0f} PUT - Expires {row['expiration']}")
        print(f"   {'─'*76}")
        print(f"   Current Stock: ${row['current_stock_price']:.2f} | Strike: ${row['strike']:.0f} | Days: {row['days_to_expiration']}")
        print(f"   Premium: ${row['premium_received']:.2f} × 1 = ${row['premium_received'] * 100:.0f}")

        print(f"\n   PROFIT TARGETS:")
        print(f"   • 50% Profit: Close when option = ${row['target_50%']:.2f} → Profit ${row['profit_50%']:.0f}")
        print(f"   • 75% Profit: Close when option = ${row['target_75%']:.2f} → Profit ${row['profit_75%']:.0f}")

        print(f"\n   TRADE PLAN:")
        print(f"   1. Sell put for ${row['premium_received']:.2f}")
        print(f"   2. Set alerts at ${row['target_50%']:.2f} (50%) and ${row['target_75%']:.2f} (75%)")
        print(f"   3. Close immediately when either alert triggers")
        print(f"   4. Expected hold: 10-20 days to hit 50% profit")
        print(f"   5. Force close at day {int(row['days_to_expiration']) - 21} (21 DTE rule)")

        print(f"\n   RISK METRICS:")
        print(f"   • Prob OTM: {row['prob_otm']:.1f}% (chance of expiring worthless)")
        print(f"   • Delta: {row['delta']:.3f} (~{abs(row['delta'])*100:.0f}% assignment probability)")
        print(f"   • Volume: {row['volume']:.0f} (good for closing)")

        capital = row['strike'] * 100
        if capital <= max_cash_per_position:
            print(f"   • Capital: ${capital:,.0f} ✓ (you can afford)")
        else:
            print(f"   • Capital: ${capital:,.0f} ⚠️ (above your max ${max_cash_per_position:,.0f})")

        # Expected performance
        expected_days = 15  # Average days to 50% profit
        expected_profit = row['premium_received'] * 0.50 * 100
        expected_annual = (expected_profit / capital) * (365 / expected_days) * 100

        print(f"\n   EXPECTED PERFORMANCE (if closed at 50% in ~15 days):")
        print(f"   • Expected profit: ${expected_profit:.0f} in 15 days")
        print(f"   • Expected annualized return: {expected_annual:.1f}%")
        print(f"   • Trades per year: ~24 (every 15 days)")

        print(f"\n   {'─'*76}")

    # Save recommendations
    if config.RECOMMENDATIONS_SETTINGS['auto_save']:
        rec_manager = RecommendationsManager(config.RECOMMENDATIONS_SETTINGS['save_directory'])
        criteria = {
            **settings,
            'strategy': 'early_close',
            'target_profit': '50-75%',
            'force_close_dte': 21,
            'available_cash': available_cash,
        }

        rec_manager.save_cash_secured_put_recommendations(
            results,
            tickers=tickers,
            criteria=criteria,
            notes=f"Early Close Strategy | Target 45-60 DTE | Close at 50-75% profit | Volume 500+"
        )

    # Summary
    print(f"\n{'='*80}")
    print("NEXT STEPS")
    print(f"{'='*80}")
    print("\n1. Choose 1-2 positions from above")
    print("2. Open your broker and sell the puts")
    print("3. Use early_close_calculator.py to track positions:")
    print("   python early_close_calculator.py")
    print("\n4. Set profit target alerts in your broker:")
    print("   - Alert at 50% target price")
    print("   - Alert at 75% target price")
    print("\n5. Close immediately when alerts trigger")
    print("6. Repeat!")

    print(f"\n{'='*80}\n")

    return results


if __name__ == "__main__":
    run_early_close_scan()
