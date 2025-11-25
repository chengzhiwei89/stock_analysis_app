"""
Quick Start Script
Run this for a fast analysis using settings from config.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.data.option_extractor import OptionDataExtractor
from src.data.recommendations_manager import RecommendationsManager
from src.strategies.covered_call import CoveredCallAnalyzer
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
from tabulate import tabulate
import config


def quick_covered_call_scan():
    """Quick scan for covered call opportunities"""
    print("\n" + "="*80)
    print("QUICK COVERED CALL SCAN")
    print("="*80)

    # Initialize
    extractor = OptionDataExtractor()
    analyzer = CoveredCallAnalyzer()

    # Use settings from config
    tickers = config.WATCHLIST
    settings = config.COVERED_CALL_SETTINGS

    print(f"\nScanning {len(tickers)} tickers: {', '.join(tickers)}")
    print(f"Criteria: Min ${settings['min_premium']} premium, "
          f"{settings['min_annual_return']}% annual return, "
          f"{settings['max_days']} max days\n")

    # Fetch data
    print("Fetching options data...")
    options_data = extractor.fetch_and_store_options(
        tickers,
        num_expirations=config.NUM_EXPIRATIONS
    )

    if options_data.empty:
        print("No data available.")
        return

    # Analyze
    print("\nAnalyzing opportunities...")
    results = analyzer.get_top_opportunities(
        options_data,
        min_premium=settings['min_premium'],
        min_annual_return=settings['min_annual_return'],
        max_days=settings['max_days'],
        top_n=settings['top_n']
    )

    if results.empty:
        print("No opportunities found matching criteria.")
        return

    # Display results
    print(f"\n{'='*80}")
    print(f"TOP {settings['top_n']} COVERED CALL OPPORTUNITIES")
    print(f"{'='*80}\n")

    display_cols = [
        'ticker', 'current_stock_price', 'strike', 'expiration',
        'days_to_expiration', 'premium_received', 'annual_return',
        'monthly_return', 'downside_protection', 'distance_pct', 'volume'
    ]

    display_cols = [col for col in display_cols if col in results.columns]
    display_df = results[display_cols].copy()

    # Format
    display_df['current_stock_price'] = display_df['current_stock_price'].apply(lambda x: f"${x:.2f}")
    display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
    display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
    display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")
    display_df['monthly_return'] = display_df['monthly_return'].apply(lambda x: f"{x:.1f}%")
    display_df['downside_protection'] = display_df['downside_protection'].apply(lambda x: f"{x:.1f}%")
    display_df['distance_pct'] = display_df['distance_pct'].apply(lambda x: f"{x:.1f}%")

    print(tabulate(display_df, headers='keys', tablefmt=config.DISPLAY_SETTINGS['table_format'],
                   showindex=False, maxcolwidths=15))

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY BY TICKER")
    print(f"{'='*80}\n")

    summary = analyzer.summarize_by_ticker(results)
    print(tabulate(summary, headers='keys', tablefmt=config.DISPLAY_SETTINGS['table_format']))

    # Auto-save recommendations
    if config.RECOMMENDATIONS_SETTINGS['auto_save']:
        rec_manager = RecommendationsManager(config.RECOMMENDATIONS_SETTINGS['save_directory'])
        criteria = {
            'min_premium': settings['min_premium'],
            'min_annual_return': settings['min_annual_return'],
            'max_days': settings['max_days'],
        }
        rec_manager.save_covered_call_recommendations(
            results,
            tickers=tickers,
            criteria=criteria,
            notes=f"Quick scan of {len(tickers)} tickers"
        )

    return results


def quick_cash_secured_put_scan():
    """Quick scan for cash secured put opportunities"""
    print("\n" + "="*80)
    print("QUICK CASH SECURED PUT SCAN")
    print("="*80)

    # Initialize
    extractor = OptionDataExtractor()
    analyzer = CashSecuredPutAnalyzer()

    # Use settings from config
    tickers = config.WATCHLIST
    settings = config.CASH_SECURED_PUT_SETTINGS

    print(f"\nScanning {len(tickers)} tickers: {', '.join(tickers)}")
    print(f"Criteria: Min ${settings['min_premium']} premium, "
          f"{settings['min_annual_return']}% annual return, "
          f"{settings['min_days']}-{settings['max_days']} days")

    # Get advanced settings
    advanced = config.CASH_SECURED_PUT_ADVANCED

    # Display additional filters
    if advanced.get('min_prob_otm'):
        print(f"          Min {advanced['min_prob_otm']}% probability OTM (safer trades)")
    if advanced.get('min_volume'):
        print(f"          Min {advanced['min_volume']} volume (better liquidity)")
    if advanced.get('quality_tickers_only'):
        print(f"          Quality tickers only: {len(config.CSP_QUALITY_TICKERS)} stocks")

    # Get cash settings
    available_cash = None
    max_cash_per_position = None
    if settings.get('use_available_cash', False):
        available_cash = config.get_deployable_cash()
        max_cash_per_position = config.CAPITAL_SETTINGS['max_cash_per_position']
        print(f"Available Cash: ${available_cash:,.0f}, Max per position: ${max_cash_per_position:,.0f}\n")
    else:
        print()

    # Fetch data
    print("Fetching options data...")
    options_data = extractor.fetch_and_store_options(
        tickers,
        num_expirations=config.NUM_EXPIRATIONS
    )

    if options_data.empty:
        print("No data available.")
        return

    # Analyze
    print("\nAnalyzing opportunities...")

    # Determine quality tickers filter
    quality_tickers = None
    if advanced.get('quality_tickers_only', False):
        quality_tickers = config.CSP_QUALITY_TICKERS

    results = analyzer.get_top_opportunities(
        options_data,
        min_premium=settings['min_premium'],
        min_annual_return=settings['min_annual_return'],
        min_days=settings.get('min_days', 0),
        max_days=settings['max_days'],
        min_prob_otm=advanced.get('min_prob_otm'),
        min_volume=advanced.get('min_volume'),
        quality_tickers=quality_tickers,
        min_delta=advanced.get('min_delta'),
        max_delta=advanced.get('max_delta'),
        top_n=settings['top_n'],
        available_cash=available_cash,
        max_cash_per_position=max_cash_per_position
    )

    if results.empty:
        print("No opportunities found matching criteria.")
        return

    # Display results
    print(f"\n{'='*80}")
    print(f"TOP {settings['top_n']} CASH SECURED PUT OPPORTUNITIES")
    print(f"{'='*80}\n")

    display_cols = [
        'ticker', 'current_stock_price', 'strike', 'expiration',
        'days_to_expiration', 'premium_received', 'annual_return',
        'monthly_return', 'net_purchase_price', 'discount_from_current'
    ]

    # Add probability and delta if available (important for new filtering)
    if 'prob_otm' in results.columns:
        display_cols.append('prob_otm')
    if 'delta' in results.columns:
        display_cols.append('delta')

    # Add cash-related columns if available
    if 'max_affordable_contracts' in results.columns:
        display_cols.extend(['max_affordable_contracts', 'total_capital_required', 'total_premium_received'])

    display_cols.append('volume')

    display_cols = [col for col in display_cols if col in results.columns]
    display_df = results[display_cols].copy()

    # Format
    display_df['current_stock_price'] = display_df['current_stock_price'].apply(lambda x: f"${x:.2f}")
    display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
    display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
    display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")
    display_df['monthly_return'] = display_df['monthly_return'].apply(lambda x: f"{x:.1f}%")
    display_df['net_purchase_price'] = display_df['net_purchase_price'].apply(lambda x: f"${x:.2f}")
    display_df['discount_from_current'] = display_df['discount_from_current'].apply(lambda x: f"{x:.1f}%")

    # Format probability and delta if they exist
    if 'prob_otm' in display_df.columns:
        display_df['prob_otm'] = display_df['prob_otm'].apply(lambda x: f"{x:.1f}%")
    if 'delta' in display_df.columns:
        display_df['delta'] = display_df['delta'].apply(lambda x: f"{x:.3f}")

    # Format cash columns if they exist
    if 'total_capital_required' in display_df.columns:
        display_df['total_capital_required'] = display_df['total_capital_required'].apply(lambda x: f"${x:,.0f}")
    if 'total_premium_received' in display_df.columns:
        display_df['total_premium_received'] = display_df['total_premium_received'].apply(lambda x: f"${x:,.0f}")

    print(tabulate(display_df, headers='keys', tablefmt=config.DISPLAY_SETTINGS['table_format'],
                   showindex=False, maxcolwidths=15))

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY BY TICKER")
    print(f"{'='*80}\n")

    summary = analyzer.summarize_by_ticker(results)
    print(tabulate(summary, headers='keys', tablefmt=config.DISPLAY_SETTINGS['table_format']))

    # Auto-save recommendations
    if config.RECOMMENDATIONS_SETTINGS['auto_save']:
        rec_manager = RecommendationsManager(config.RECOMMENDATIONS_SETTINGS['save_directory'])
        criteria = {
            'min_premium': settings['min_premium'],
            'min_annual_return': settings['min_annual_return'],
            'min_days': settings.get('min_days', 0),
            'max_days': settings['max_days'],
            'min_prob_otm': settings.get('min_prob_otm'),
            'min_volume': advanced.get('min_volume'),
            'min_delta': settings.get('min_delta'),
            'max_delta': settings.get('max_delta'),
            'quality_tickers_only': advanced.get('quality_tickers_only', False),
            'available_cash': available_cash,
            'max_cash_per_position': max_cash_per_position,
        }

        notes_parts = [f"Quick scan of {len(tickers)} tickers"]
        if advanced.get('quality_tickers_only'):
            notes_parts.append(f"Quality stocks only ({len(config.CSP_QUALITY_TICKERS)} tickers)")
        if settings.get('min_prob_otm'):
            notes_parts.append(f"Min {settings['min_prob_otm']}% prob OTM")
        if available_cash:
            notes_parts.append(f"${available_cash:,.0f} available cash")

        rec_manager.save_cash_secured_put_recommendations(
            results,
            tickers=tickers,
            criteria=criteria,
            notes=" | ".join(notes_parts)
        )

    return results


def quick_wheel_scan():
    """Quick scan for Wheel strategy candidates"""
    print("\n" + "="*80)
    print("WHEEL STRATEGY SCAN")
    print("="*80)

    # Initialize
    extractor = OptionDataExtractor()
    analyzer = CashSecuredPutAnalyzer()

    # Use settings from config
    tickers = config.WATCHLIST
    settings = config.WHEEL_SETTINGS

    print(f"\nScanning {len(tickers)} tickers for Wheel strategy candidates")
    print(f"Target entry discount: {settings['target_entry_discount']}%")
    print(f"Min annual return: {settings['min_annual_return']}%")

    # Get cash settings
    available_cash = None
    max_cash_per_position = None
    if config.CASH_SECURED_PUT_SETTINGS.get('use_available_cash', False):
        available_cash = config.get_deployable_cash()
        max_cash_per_position = config.CAPITAL_SETTINGS['max_cash_per_position']
        print(f"Available Cash: ${available_cash:,.0f}, Max per position: ${max_cash_per_position:,.0f}\n")
    else:
        print()

    # Fetch data
    print("Fetching options data...")
    options_data = extractor.fetch_and_store_options(
        tickers,
        num_expirations=config.NUM_EXPIRATIONS
    )

    if options_data.empty:
        print("No data available.")
        return

    # Analyze
    print("\nAnalyzing Wheel candidates...")
    results = analyzer.find_wheel_candidates(
        options_data,
        target_entry_discount=settings['target_entry_discount'],
        min_annual_return=settings['min_annual_return'],
        max_days=settings['max_days'],
        available_cash=available_cash,
        max_cash_per_position=max_cash_per_position
    )

    if results.empty:
        print("No Wheel candidates found matching criteria.")
        return

    # Display results
    print(f"\n{'='*80}")
    print("TOP WHEEL STRATEGY CANDIDATES")
    print(f"{'='*80}\n")

    display_cols = [
        'ticker', 'current_stock_price', 'strike', 'expiration',
        'days_to_expiration', 'premium_received', 'annual_return',
        'net_purchase_price', 'discount_from_current', 'wheel_score'
    ]

    display_cols = [col for col in display_cols if col in results.columns]
    display_df = results[display_cols].head(15).copy()

    # Format
    display_df['current_stock_price'] = display_df['current_stock_price'].apply(lambda x: f"${x:.2f}")
    display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.2f}")
    display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
    display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")
    display_df['net_purchase_price'] = display_df['net_purchase_price'].apply(lambda x: f"${x:.2f}")
    display_df['discount_from_current'] = display_df['discount_from_current'].apply(lambda x: f"{x:.1f}%")
    display_df['wheel_score'] = display_df['wheel_score'].apply(lambda x: f"{x:.1f}")

    print(tabulate(display_df, headers='keys', tablefmt=config.DISPLAY_SETTINGS['table_format'],
                   showindex=False, maxcolwidths=15))

    # Auto-save recommendations
    if config.RECOMMENDATIONS_SETTINGS['auto_save']:
        rec_manager = RecommendationsManager(config.RECOMMENDATIONS_SETTINGS['save_directory'])
        criteria = {
            'target_entry_discount': settings['target_entry_discount'],
            'min_annual_return': settings['min_annual_return'],
            'max_days': settings['max_days'],
            'available_cash': available_cash,
            'max_cash_per_position': max_cash_per_position,
        }
        rec_manager.save_wheel_recommendations(
            results,
            tickers=tickers,
            criteria=criteria,
            notes=f"Wheel strategy scan of {len(tickers)} tickers"
        )

    return results


def main():
    """Main quick start function"""
    print("\n" + "#"*80)
    print("# Stock Options Quick Start")
    print("# Configure settings in config.py")
    print("#"*80)

    # Run scans
    print("\n[1/3] Running Covered Call scan...")
    cc_results = quick_covered_call_scan()

    print("\n[2/3] Running Cash Secured Put scan...")
    csp_results = quick_cash_secured_put_scan()

    print("\n[3/3] Running Wheel Strategy scan...")
    wheel_results = quick_wheel_scan()

    # Final summary
    print("\n" + "#"*80)
    print("# Scan Complete!")
    print("#"*80)

    if cc_results is not None and not cc_results.empty:
        print(f"\nCovered Calls: Found {len(cc_results)} opportunities")
    if csp_results is not None and not csp_results.empty:
        print(f"Cash Secured Puts: Found {len(csp_results)} opportunities")
    if wheel_results is not None and not wheel_results.empty:
        print(f"Wheel Strategy: Found {len(wheel_results)} candidates")

    print("\nData saved to:")
    print("  - Raw options data: data/option_chains/")
    if config.RECOMMENDATIONS_SETTINGS['auto_save']:
        print("  - Recommendations: data/recommendations/")

    print("\nTips:")
    print("- Modify config.py to customize your scans")
    print("- Use example_portfolio.py to manage your positions")
    print("- Check data/recommendations/ for saved recommendations")
    print("- Check README.md for detailed documentation")


if __name__ == "__main__":
    main()
