"""
Enhanced CSP Scanner
Uses technical and fundamental factors to improve probability estimates
"""
import sys
import os
import argparse
import webbrowser
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.option_extractor import OptionDataExtractor
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
from src.analysis.enhanced_probability import EnhancedProbabilityAnalyzer
from src.visualization.html_generator import HTMLDashboardGenerator
import config
from tabulate import tabulate


def run_enhanced_scan(generate_html=False, open_browser=True, output_dir='output/dashboards'):
    """Run CSP scan with enhanced probability analysis

    Args:
        generate_html: If True, generate HTML dashboard
        open_browser: If True, automatically open dashboard in browser
        output_dir: Directory to save HTML dashboard

    Returns:
        DataFrame with enhanced results
    """

    print("\n" + "="*80)
    print("ENHANCED CSP SCANNER")
    print("Using Technical + Fundamental + Sentiment Analysis")
    print("="*80)

    # Initialize analyzers
    option_extractor = OptionDataExtractor()
    csp_analyzer = CashSecuredPutAnalyzer()
    prob_analyzer = EnhancedProbabilityAnalyzer()

    # Settings - Load from config.py
    tickers = config.WATCHLIST
    settings = {
        # Basic settings
        'min_premium': config.CASH_SECURED_PUT_SETTINGS['min_premium'],
        'min_annual_return': config.CASH_SECURED_PUT_SETTINGS['min_annual_return'],
        'min_days': config.CASH_SECURED_PUT_SETTINGS['min_days'],
        'max_days': config.CASH_SECURED_PUT_SETTINGS['max_days'],
        # Advanced settings
        'min_prob_otm': config.CASH_SECURED_PUT_ADVANCED['min_prob_otm'],
        'min_delta': config.CASH_SECURED_PUT_ADVANCED['min_delta'],
        'max_delta': config.CASH_SECURED_PUT_ADVANCED['max_delta'],
        'min_volume': config.CASH_SECURED_PUT_ADVANCED['min_volume'],
    }

    print(f"\nScanning {len(tickers)} tickers: {', '.join(tickers)}")
    print(f"Criteria: {settings['min_days']}-{settings['max_days']} days, ")
    print(f"          {settings['min_prob_otm']}%+ prob OTM, ")
    print(f"          ${settings['min_premium']}+ premium, ")
    print(f"          {settings['min_volume']}+ volume, ")
    print(f"          {settings['min_annual_return']}%+ annual return")

    print("\nNOTE: If market is closed, using lastPrice as fallback for bid=0")
    print("      During market hours, actual bid prices will be used")

    # Fetch options data
    print("\n[1/3] Fetching options data...")
    options_data = option_extractor.fetch_and_store_options(
        tickers,
        num_expirations=config.NUM_EXPIRATIONS
    )

    if options_data.empty:
        print("No data available.")
        return

    print(f"Fetched {len(options_data)} option chains")

    # Run standard CSP analysis
    print("\n[2/3] Running standard CSP analysis...")
    available_cash = config.get_deployable_cash()
    max_cash_per_position = config.CAPITAL_SETTINGS['max_cash_per_position']

    results = csp_analyzer.get_top_opportunities(
        options_data,
        min_premium=settings['min_premium'],
        min_annual_return=settings['min_annual_return'],
        min_days=settings.get('min_days', 0),
        max_days=settings['max_days'],
        min_prob_otm=settings.get('min_prob_otm'),
        min_volume=settings.get('min_volume'),
        quality_tickers=None,  # Don't filter by quality for demo
        min_delta=settings.get('min_delta'),
        max_delta=settings.get('max_delta'),
        top_n=20,
        available_cash=available_cash,
        max_cash_per_position=max_cash_per_position
    )

    if results.empty:
        print("No opportunities found matching criteria.")
        return

    print(f"Found {len(results)} opportunities")

    # Add enhanced probability analysis
    print("\n[3/3] Calculating enhanced probabilities...")
    print("(Fetching technical, fundamental, and sentiment data...)")

    # Ensure option_type column exists for enhanced analysis
    if 'option_type' not in results.columns:
        results['option_type'] = 'put'

    results_enhanced = prob_analyzer.enrich_options_dataframe(results)

    print("Enhanced analysis complete!")

    # Check market status
    market_closed_count = (results_enhanced['price_source'] == 'lastPrice').sum()
    if market_closed_count > 0:
        print(f"\nMARKET STATUS: Closed (using lastPrice for {market_closed_count} options)")
        print("NOTE: Prices shown are estimates based on last traded price")
        print("      Actual bid prices may differ when market opens")
    else:
        print(f"\nMARKET STATUS: Open (using live bid prices)")

    # Display comparison
    print("\n" + "="*80)
    print("COMPARISON: STANDARD vs ENHANCED PROBABILITY")
    print("="*80 + "\n")

    display_cols = [
        'ticker', 'strike', 'days_to_expiration', 'premium_received',
        'price_source', 'prob_otm', 'enhanced_prob_otm', 'prob_adjustment',
        'annual_return'
    ]

    display_cols = [col for col in display_cols if col in results_enhanced.columns]
    display_df = results_enhanced[display_cols].head(15).copy()

    # Format
    display_df['strike'] = display_df['strike'].apply(lambda x: f"${x:.0f}")
    display_df['premium_received'] = display_df['premium_received'].apply(lambda x: f"${x:.2f}")
    display_df['prob_otm'] = display_df['prob_otm'].apply(lambda x: f"{x:.1f}%")
    display_df['enhanced_prob_otm'] = display_df['enhanced_prob_otm'].apply(lambda x: f"{x:.1f}%")
    display_df['prob_adjustment'] = display_df['prob_adjustment'].apply(lambda x: f"{x:+.1f}%")
    display_df['annual_return'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%")

    print(tabulate(display_df, headers='keys', tablefmt='grid', showindex=False, maxcolwidths=12))

    # Detailed analysis of top 5
    print("\n" + "="*80)
    print("DETAILED ENHANCED ANALYSIS - TOP 5 OPPORTUNITIES")
    print("="*80)

    for i, (_, row) in enumerate(results_enhanced.head(5).iterrows(), 1):
        print(f"\n{i}. {row['ticker']} ${row['strike']:.0f} PUT - {row['days_to_expiration']} days")
        print(f"   {'='*76}")

        print(f"\n   PROBABILITY ANALYSIS:")
        print(f"   * Standard (Black-Scholes): {row['prob_otm']:.1f}%")
        print(f"   * Enhanced (w/ Technical/Fundamental): {row['enhanced_prob_otm']:.1f}%")
        print(f"   * Adjustment: {row['prob_adjustment']:+.1f}% {'SAFER' if row['prob_adjustment'] > 0 else 'RISKIER' if row['prob_adjustment'] < 0 else 'NEUTRAL'}")

        print(f"\n   FACTOR SCORES (0-100):")
        print(f"   * Technical Score: {row['technical_score']:.0f} ", end="")
        print("(Strong)" if row['technical_score'] > 70 else "(Good)" if row['technical_score'] > 55 else "(Neutral)" if row['technical_score'] > 45 else "(Weak)")

        print(f"   * Fundamental Score: {row['fundamental_score']:.0f} ", end="")
        print("(Strong)" if row['fundamental_score'] > 70 else "(Good)" if row['fundamental_score'] > 55 else "(Neutral)" if row['fundamental_score'] > 45 else "(Weak)")

        print(f"   * Sentiment Score: {row['sentiment_score']:.0f} ", end="")
        print("(Bullish)" if row['sentiment_score'] > 70 else "(Positive)" if row['sentiment_score'] > 55 else "(Neutral)" if row['sentiment_score'] > 45 else "(Bearish)")

        print(f"   * Event Risk Score: {row['event_risk_score']:.0f} ", end="")
        print("(Low Risk)" if row['event_risk_score'] > 70 else "(Moderate Risk)" if row['event_risk_score'] > 50 else "(HIGH RISK)")

        print(f"   * Composite Score: {row['composite_score']:.0f}/100")

        print(f"\n   RECOMMENDATION:")
        if row['enhanced_prob_otm'] > 75 and row['composite_score'] > 60:
            recommendation = "EXCELLENT - High probability with strong fundamentals"
        elif row['enhanced_prob_otm'] > 70:
            recommendation = "GOOD - Solid probability"
        elif row['enhanced_prob_otm'] > 65:
            recommendation = "FAIR - Acceptable risk"
        elif row['enhanced_prob_otm'] < 60:
            recommendation = "CAUTION - Enhanced analysis shows higher risk"
        else:
            recommendation = "MODERATE - Standard risk level"

        print(f"   {recommendation}")

        print(f"\n   TRADE DETAILS:")
        print(f"   * Premium: ${row['premium_received']:.2f} x 100 = ${row['premium_received'] * 100:.0f}")

        # Show price breakdown if available
        if 'original_bid' in row and 'original_ask' in row and 'original_lastPrice' in row:
            print(f"   * Price Details:")
            print(f"     - Bid: ${row['original_bid']:.2f} {'(USED)' if row.get('price_source') == 'bid' else ''}")
            print(f"     - Ask: ${row['original_ask']:.2f}")
            print(f"     - Last: ${row['original_lastPrice']:.2f} {'(USED - Market Closed)' if row.get('price_source') == 'lastPrice' else ''}")

        print(f"   * Capital Required: ${row['strike'] * 100:,.0f}")
        print(f"   * Annual Return: {row['annual_return']:.1f}%")

        print(f"\n   {'-'*76}")

    # Summary statistics
    print("\n" + "="*80)
    print("ENHANCED ANALYSIS SUMMARY")
    print("="*80)

    print(f"\nTop {len(results_enhanced)} Opportunities:")
    print(f"  Average BS Probability: {results_enhanced['prob_otm'].mean():.1f}%")
    print(f"  Average Enhanced Probability: {results_enhanced['enhanced_prob_otm'].mean():.1f}%")
    print(f"  Average Adjustment: {results_enhanced['prob_adjustment'].mean():+.1f}%")

    safer_count = (results_enhanced['prob_adjustment'] > 0).sum()
    riskier_count = (results_enhanced['prob_adjustment'] < 0).sum()

    print(f"\n  Opportunities Made SAFER by Analysis: {safer_count} ({safer_count/len(results_enhanced)*100:.0f}%)")
    print(f"  Opportunities Made RISKIER by Analysis: {riskier_count} ({riskier_count/len(results_enhanced)*100:.0f}%)")

    print(f"\n  Average Component Scores:")
    print(f"    Technical: {results_enhanced['technical_score'].mean():.0f}/100")
    print(f"    Fundamental: {results_enhanced['fundamental_score'].mean():.0f}/100")
    print(f"    Sentiment: {results_enhanced['sentiment_score'].mean():.0f}/100")
    print(f"    Event Risk: {results_enhanced['event_risk_score'].mean():.0f}/100")

    # Show opportunities with biggest adjustments
    print("\n" + "="*80)
    print("BIGGEST ADJUSTMENTS (Most Changed by Enhanced Analysis)")
    print("="*80)

    biggest_changes = results_enhanced.nlargest(5, 'prob_adjustment')[
        ['ticker', 'strike', 'prob_otm', 'enhanced_prob_otm', 'prob_adjustment', 'composite_score']
    ]

    print("\nMost SAFER than BS predicts:")
    for _, row in biggest_changes.iterrows():
        print(f"  {row['ticker']:6} ${row['strike']:.0f}: {row['prob_otm']:.1f}% -> {row['enhanced_prob_otm']:.1f}% ({row['prob_adjustment']:+.1f}%) [Score: {row['composite_score']:.0f}]")

    smallest_changes = results_enhanced.nsmallest(5, 'prob_adjustment')[
        ['ticker', 'strike', 'prob_otm', 'enhanced_prob_otm', 'prob_adjustment', 'composite_score']
    ]

    print("\nMost RISKIER than BS predicts:")
    for _, row in smallest_changes.iterrows():
        print(f"  {row['ticker']:6} ${row['strike']:.0f}: {row['prob_otm']:.1f}% -> {row['enhanced_prob_otm']:.1f}% ({row['prob_adjustment']:+.1f}%) [Score: {row['composite_score']:.0f}]")

    print("\n" + "="*80)
    print("KEY INSIGHTS")
    print("="*80)

    print("\nThe Enhanced Analysis:")
    print("  * Uses technical indicators (trends, momentum, support/resistance)")
    print("  * Incorporates fundamental strength (valuation, growth, profitability)")
    print("  * Considers analyst sentiment (ratings, price targets)")
    print("  * Accounts for event risk (earnings dates)")
    print("\nThis gives you an 'edge' beyond simple Black-Scholes probability!")

    print("\n" + "="*80 + "\n")

    # Generate HTML dashboard if requested
    if generate_html:
        print("="*80)
        print("GENERATING HTML DASHBOARD")
        print("="*80)
        print("\nCreating interactive HTML visualization...")

        # Determine market status
        market_status = 'CLOSED' if market_closed_count > 0 else 'OPEN'

        # Prepare metadata
        metadata = {
            'scan_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'market_status': market_status,
            'tickers': tickers,
            'scan_type': 'Enhanced CSP Scan',
            'criteria': {
                'min_days': settings['min_days'],
                'max_days': settings['max_days'],
                'min_prob_otm': settings['min_prob_otm'],
                'min_premium': settings['min_premium'],
                'min_annual_return': settings['min_annual_return']
            }
        }

        # Initialize generator
        generator = HTMLDashboardGenerator(config={
            'theme': 'light',
            'max_opportunities': 50,
            'output_dir': output_dir
        })

        # Generate dashboard (only CSP results for now)
        try:
            output_path = generator.generate(
                csp_results=results_enhanced,
                cc_results=None,  # Not available in this scan
                wheel_results=None,  # Not available in this scan
                metadata=metadata
            )

            print(f"\n[SUCCESS] Dashboard generated successfully!")
            print(f"  Location: {output_path}")
            print(f"  Size: {os.path.getsize(output_path) / 1024:.1f} KB")

            # Open in browser if requested
            if open_browser:
                print(f"\n  Opening dashboard in browser...")
                webbrowser.open(f'file:///{os.path.abspath(output_path)}')
                print(f"  [OK] Dashboard opened")

            print("\n" + "="*80 + "\n")

        except Exception as e:
            print(f"\n[ERROR] Error generating dashboard: {e}")
            print("  Continuing without HTML output...")
            print("\n" + "="*80 + "\n")

    return results_enhanced


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Enhanced CSP Scanner with Technical + Fundamental Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run scan with console output only
  python run_enhanced_csp_scan.py

  # Generate HTML dashboard and open in browser
  python run_enhanced_csp_scan.py --html

  # Generate HTML dashboard without opening browser
  python run_enhanced_csp_scan.py --html --no-browser

  # Generate HTML dashboard in custom directory
  python run_enhanced_csp_scan.py --html --output-dir custom/path
        """
    )

    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate interactive HTML dashboard'
    )

    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='Do not automatically open browser (only with --html)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output/dashboards',
        help='Output directory for HTML dashboard (default: output/dashboards)'
    )

    args = parser.parse_args()

    # Run scan with specified options
    results = run_enhanced_scan(
        generate_html=args.html,
        open_browser=not args.no_browser,
        output_dir=args.output_dir
    )
