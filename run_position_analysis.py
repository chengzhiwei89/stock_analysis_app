"""
Position Analysis Script
Analyze existing option positions and generate management recommendations
"""
import sys
import os
import argparse
import webbrowser
from datetime import datetime
from typing import List, Dict

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.portfolio.portfolio_manager import PortfolioManager
from src.portfolio.capital_calculator import CapitalCalculator
from src.portfolio.position_analyzer import PositionAnalyzer, PositionRecommendation
from src.strategies.rolling_optimizer import RollingOpportunityFinder
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
from src.data.option_extractor import OptionDataExtractor
from src.utils.market_hours import get_market_status
import config


def run_position_analysis(
    generate_html: bool = False,
    open_browser: bool = True,
    scan_new_opportunities: bool = True,
    output_dir: str = 'output/position_analysis'
) -> List[PositionRecommendation]:
    """
    Run comprehensive position analysis

    Args:
        generate_html: Generate HTML dashboard
        open_browser: Automatically open browser
        scan_new_opportunities: Scan for new opportunities with available capital
        output_dir: Output directory for reports

    Returns:
        List of PositionRecommendation objects
    """
    print("\n" + "="*80)
    print("POSITION ANALYSIS & MANAGEMENT")
    print("Analyzing existing positions with current market data")
    print("="*80)

    # Initialize components
    portfolio = PortfolioManager()
    capital_calc = CapitalCalculator()
    position_analyzer = PositionAnalyzer()
    rolling_finder = RollingOpportunityFinder()

    # Check market status
    market_status, market_description = get_market_status()
    print(f"\nMarket Status: {market_status}")
    print(f"  {market_description}")

    # ========================================================================
    # STEP 1: LOAD PORTFOLIO & CALCULATE CAPITAL
    # ========================================================================
    print("\n" + "="*80)
    print("[1/4] PORTFOLIO & CAPITAL ANALYSIS")
    print("="*80)

    # Display capital summary
    print(capital_calc.get_capital_summary_string(portfolio))

    deployed_info = capital_calc.calculate_deployed_capital(portfolio)
    capital_info = capital_calc.calculate_available_capital(portfolio)

    # ========================================================================
    # STEP 2: ANALYZE EXISTING POSITIONS
    # ========================================================================
    print("="*80)
    print("[2/4] ANALYZING OPEN POSITIONS")
    print("="*80)

    open_positions = portfolio.get_options_dataframe(status='open')

    if open_positions.empty:
        print("\nNo open positions to analyze.")
        print("\nTo add positions, use:")
        print("  from src.portfolio.portfolio_manager import PortfolioManager")
        print("  portfolio = PortfolioManager()")
        print("  portfolio.add_option_position(...)")
        return []

    print(f"\nAnalyzing {len(open_positions)} open position(s)...")
    print("(Fetching current market data and running analysis...)\n")

    recommendations = []
    for idx, position in open_positions.iterrows():
        try:
            recommendation = position_analyzer.analyze_option_position(position, idx)
            recommendations.append(recommendation)

            # Find rolling opportunities if action is ROLL
            if recommendation.action == "ROLL":
                rolls = rolling_finder.find_roll_opportunities(
                    position.to_dict(),
                    max_candidates=3
                )
                if rolls:
                    # Convert to RollingOpportunity and attach to recommendation
                    from src.portfolio.position_analyzer import RollingOpportunity
                    best_roll = rolls[0]
                    recommendation.roll_recommendation = RollingOpportunity(**best_roll)

            print(f"  ✓ Analyzed {recommendation.ticker} ${recommendation.strike} {recommendation.option_type.upper()}")

        except Exception as e:
            print(f"  ✗ Error analyzing position {idx}: {e}")
            continue

    print(f"\nAnalysis complete! {len(recommendations)} position(s) analyzed.")

    # ========================================================================
    # STEP 3: SCAN NEW OPPORTUNITIES (if capital available)
    # ========================================================================
    new_opportunities = None

    if scan_new_opportunities and capital_info['remaining_for_new'] > 0:
        print("\n" + "="*80)
        print("[3/4] SCANNING NEW OPPORTUNITIES")
        print("="*80)

        print(f"\nAvailable capital for new positions: ${capital_info['remaining_for_new']:,.0f}")
        print(f"Position slots available: {capital_info['positions_available']}")
        print("\nScanning for CSP opportunities with available capital...")

        try:
            option_extractor = OptionDataExtractor()
            csp_analyzer = CashSecuredPutAnalyzer()

            # Fetch options data for watchlist
            tickers = config.WATCHLIST[:10]  # Limit to first 10 for speed
            print(f"Fetching data for {len(tickers)} tickers...")

            options_data = option_extractor.fetch_and_store_options(
                tickers,
                num_expirations=3  # Reduced for faster scanning
            )

            if not options_data.empty:
                # Run CSP analysis with capital constraint
                new_opportunities = csp_analyzer.get_top_opportunities(
                    options_data,
                    min_premium=config.CASH_SECURED_PUT_SETTINGS['min_premium'],
                    min_annual_return=config.CASH_SECURED_PUT_SETTINGS['min_annual_return'],
                    min_days=config.CASH_SECURED_PUT_SETTINGS['min_days'],
                    max_days=config.CASH_SECURED_PUT_SETTINGS['max_days'],
                    min_prob_otm=config.CASH_SECURED_PUT_ADVANCED.get('min_prob_otm'),
                    min_volume=config.CASH_SECURED_PUT_ADVANCED.get('min_volume'),
                    top_n=10,
                    available_cash=capital_info['remaining_for_new'],
                    max_cash_per_position=capital_info['max_per_position']
                )

                print(f"Found {len(new_opportunities)} new opportunities")
            else:
                print("No options data available")

        except Exception as e:
            print(f"Error scanning new opportunities: {e}")
            new_opportunities = None

    else:
        if not scan_new_opportunities:
            print("\n" + "="*80)
            print("[3/4] SKIPPING NEW OPPORTUNITIES SCAN")
            print("="*80)
            print("\n(Use --scan-new flag to include new opportunity scanning)")
        else:
            print("\n" + "="*80)
            print("[3/4] NO CAPITAL AVAILABLE FOR NEW POSITIONS")
            print("="*80)
            print(f"\nAll capital deployed (${deployed_info['total_deployed']:,.0f})")
            print("Close existing positions to free capital for new opportunities")

    # ========================================================================
    # STEP 4: GENERATE REPORTS
    # ========================================================================
    print("\n" + "="*80)
    print("[4/4] GENERATING RECOMMENDATIONS")
    print("="*80)

    # Console output
    print_position_recommendations(recommendations, new_opportunities, capital_info)

    # HTML dashboard (optional)
    if generate_html:
        print("\n" + "="*80)
        print("GENERATING HTML DASHBOARD")
        print("="*80)
        print("\nCreating interactive HTML dashboard...")

        try:
            # Import here to avoid circular dependencies
            from src.visualization.position_dashboard_generator import PositionDashboardGenerator

            generator = PositionDashboardGenerator(output_dir=output_dir)

            metadata = {
                'scan_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'market_status': market_status,
                'capital_deployed': deployed_info['total_deployed'],
                'capital_available': capital_info['remaining_for_new'],
                'open_positions': len(recommendations),
                'position_slots_available': capital_info['positions_available']
            }

            output_path = generator.generate(
                recommendations=recommendations,
                new_opportunities=new_opportunities,
                portfolio_summary=deployed_info,
                capital_info=capital_info,
                metadata=metadata
            )

            print(f"\n[SUCCESS] Dashboard generated!")
            print(f"  Location: {output_path}")
            print(f"  Size: {os.path.getsize(output_path) / 1024:.1f} KB")

            if open_browser:
                print(f"\n  Opening dashboard in browser...")
                webbrowser.open(f'file:///{os.path.abspath(output_path)}')

            print("\n" + "="*80 + "\n")

        except Exception as e:
            print(f"\n[ERROR] Error generating dashboard: {e}")
            import traceback
            traceback.print_exc()
            print("  Continuing without HTML output...")

    return recommendations


def print_position_recommendations(
    recommendations: List[PositionRecommendation],
    new_opportunities,
    capital_info: Dict
):
    """Print formatted position recommendations to console"""

    # Group by urgency
    critical = [r for r in recommendations if r.urgency >= 4]
    moderate = [r for r in recommendations if r.urgency == 3]
    low = [r for r in recommendations if r.urgency <= 2]

    # Print by urgency
    if critical:
        print("\n" + "="*80)
        print(f"CRITICAL ACTIONS REQUIRED ({len(critical)})")
        print("="*80)

        for i, rec in enumerate(critical, 1):
            print(f"\n{i}. {rec.ticker} ${rec.strike:.0f} {rec.option_type.upper()} (expires {rec.expiration}, {rec.days_remaining} days)")
            print(f"   Current P&L: ${rec.unrealized_pnl:.2f} ({rec.unrealized_pnl_pct:.1f}%)")
            print(f"   Health: {rec.health_score:.0f}/100 ({rec.health_status})")
            print(f"\n   RECOMMENDATION: {rec.action} ⚠️")
            print(f"   Urgency: {rec.urgency}/5 (CRITICAL)")
            print(f"   Reason: {rec.primary_reason}")

            if rec.supporting_reasons:
                print(f"   Details:")
                for reason in rec.supporting_reasons:
                    print(f"     • {reason}")

            if rec.action == "CLOSE_EARLY" and rec.suggested_close_price:
                print(f"\n   → Close at market: ${rec.suggested_close_price:.2f}")
                print(f"      Realize profit: ${rec.unrealized_pnl:.2f}")

            if rec.action == "ROLL" and rec.roll_recommendation:
                roll = rec.roll_recommendation
                print(f"\n   → Roll to: ${roll.new_strike:.0f} (exp {roll.new_expiration})")
                print(f"      Net Credit: ${roll.net_credit:.2f}")
                print(f"      Type: {roll.roll_type}")

    if moderate:
        print("\n" + "="*80)
        print(f"MODERATE PRIORITY ACTIONS ({len(moderate)})")
        print("="*80)

        for i, rec in enumerate(moderate, 1):
            print(f"\n{i}. {rec.ticker} ${rec.strike:.0f} {rec.option_type.upper()}")
            print(f"   P&L: ${rec.unrealized_pnl:.2f} ({rec.unrealized_pnl_pct:.1f}%) | {rec.days_remaining} days left")
            print(f"   RECOMMENDATION: {rec.action}")
            print(f"   {rec.primary_reason}")

    if low:
        print("\n" + "="*80)
        print(f"POSITIONS TO MONITOR ({len(low)})")
        print("="*80)

        for i, rec in enumerate(low, 1):
            print(f"\n{i}. {rec.ticker} ${rec.strike:.0f} {rec.option_type.upper()}")
            print(f"   P&L: ${rec.unrealized_pnl:.2f} ({rec.unrealized_pnl_pct:.1f}%) | Health: {rec.health_score:.0f}/100")
            print(f"   {rec.primary_reason}")

    # New opportunities summary
    if new_opportunities is not None and not new_opportunities.empty:
        print("\n" + "="*80)
        print(f"NEW OPPORTUNITIES (${capital_info['remaining_for_new']:,.0f} available)")
        print("="*80)

        print(f"\nTop {min(5, len(new_opportunities))} opportunities with available capital:\n")

        for i, (_, opp) in enumerate(new_opportunities.head(5).iterrows(), 1):
            affordable = opp['total_capital_required'] <= capital_info['remaining_for_new']
            status = "✓ AFFORDABLE" if affordable else f"✗ Need ${opp['total_capital_required'] - capital_info['remaining_for_new']:,.0f} more"

            print(f"{i}. {opp['ticker']} ${opp['strike']:.0f} PUT (exp {opp['expiration']}, {opp['days_to_expiration']} days)")
            print(f"   Annual Return: {opp['annual_return']:.1f}% | Prob OTM: {opp['prob_otm']:.0f}%")
            print(f"   Premium: ${opp['premium_received']:.2f} | Capital: ${opp['total_capital_required']:,.0f}")
            print(f"   {status}\n")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Analyze existing option positions and generate recommendations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis (console output only)
  python run_position_analysis.py

  # Generate HTML dashboard
  python run_position_analysis.py --html

  # Skip new opportunity scanning
  python run_position_analysis.py --no-scan-new

  # Generate HTML without opening browser
  python run_position_analysis.py --html --no-browser

  # Custom output directory
  python run_position_analysis.py --html --output-dir custom/path
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
        '--no-scan-new',
        action='store_true',
        help='Skip scanning for new opportunities'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output/position_analysis',
        help='Output directory for HTML dashboard (default: output/position_analysis)'
    )

    args = parser.parse_args()

    # Run analysis
    recommendations = run_position_analysis(
        generate_html=args.html,
        open_browser=not args.no_browser,
        scan_new_opportunities=not args.no_scan_new,
        output_dir=args.output_dir
    )
