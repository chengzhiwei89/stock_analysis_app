"""
View and Manage Saved Recommendations
Browse your saved analysis results
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.data.recommendations_manager import RecommendationsManager
from tabulate import tabulate
import pandas as pd


def list_all_recommendations():
    """List all saved recommendations"""
    print("="*80)
    print("ALL SAVED RECOMMENDATIONS")
    print("="*80 + "\n")

    rec_manager = RecommendationsManager()
    recommendations = rec_manager.list_recommendations()

    if not recommendations:
        print("No saved recommendations found.")
        print("\nRun 'python quick_start.py' to generate some recommendations.")
        return

    # Group by strategy
    by_strategy = {}
    for rec in recommendations:
        strategy = rec.get('strategy', 'unknown')
        if strategy not in by_strategy:
            by_strategy[strategy] = []
        by_strategy[strategy].append(rec)

    # Display grouped
    for strategy, recs in by_strategy.items():
        print(f"\n{strategy.upper().replace('_', ' ')}:")
        print("-" * 80)

        table_data = []
        for rec in recs[:10]:  # Show last 10
            table_data.append([
                rec['timestamp'],
                ', '.join(rec['tickers'][:3]) + ('...' if len(rec['tickers']) > 3 else ''),
                rec['num_opportunities'],
                rec['csv_file']
            ])

        print(tabulate(table_data,
                      headers=['Timestamp', 'Tickers', 'Count', 'File'],
                      tablefmt='grid'))

        if len(recs) > 10:
            print(f"\n... and {len(recs) - 10} more {strategy} recommendations")

    # Summary
    print("\n" + "="*80)
    print(rec_manager.get_summary())


def view_latest_recommendations(strategy: str = None, ticker: str = None):
    """View the latest recommendations"""
    print("="*80)
    print(f"LATEST {strategy.upper() if strategy else 'ALL'} RECOMMENDATIONS")
    if ticker:
        print(f"Filtered for: {ticker}")
    print("="*80 + "\n")

    rec_manager = RecommendationsManager()

    if strategy:
        # Load specific strategy
        results = rec_manager.load_latest_recommendation(strategy, ticker)

        if results.empty:
            print(f"No {strategy} recommendations found.")
            return

        print(f"Loaded {len(results)} recommendations\n")

        # Display
        display_cols = [
            'ticker', 'strike', 'expiration', 'days_to_expiration',
            'premium_received', 'annual_return', 'monthly_return'
        ]

        # Add strategy-specific columns
        if strategy == 'cc':
            display_cols.extend(['downside_protection', 'distance_pct'])
        elif strategy in ['csp', 'wheel']:
            display_cols.extend(['net_purchase_price', 'discount_from_current'])
            if 'max_affordable_contracts' in results.columns:
                display_cols.extend(['max_affordable_contracts', 'total_premium_received'])

        # Filter to available columns
        display_cols = [col for col in display_cols if col in results.columns]

        print(tabulate(results[display_cols].head(20), headers='keys',
                      tablefmt='grid', showindex=False))

        print(f"\nShowing top 20 of {len(results)} total recommendations")
        print(f"Full data in: data/recommendations/")

    else:
        # Show latest from each strategy
        for strat in ['cc', 'csp', 'wheel']:
            print(f"\n{strat.upper()} - Latest Recommendations:")
            print("-" * 80)

            results = rec_manager.load_latest_recommendation(strat, ticker)
            if not results.empty:
                print(f"Found {len(results)} opportunities")
                print(results[['ticker', 'strike', 'annual_return']].head(5).to_string(index=False))
            else:
                print(f"No {strat} recommendations saved")


def search_recommendations(ticker: str):
    """Search recommendations for a specific ticker"""
    print("="*80)
    print(f"RECOMMENDATIONS FOR {ticker.upper()}")
    print("="*80 + "\n")

    rec_manager = RecommendationsManager()

    # Search across all strategies
    for strategy_name, strategy_code in [('Covered Calls', 'cc'),
                                          ('Cash Secured Puts', 'csp'),
                                          ('Wheel Strategy', 'wheel')]:
        print(f"\n{strategy_name}:")
        print("-" * 80)

        results = rec_manager.load_latest_recommendation(strategy_code, ticker)

        if not results.empty:
            # Filter for the specific ticker
            ticker_results = results[results['ticker'].str.upper() == ticker.upper()]

            if not ticker_results.empty:
                display_cols = [
                    'strike', 'expiration', 'days_to_expiration',
                    'premium_received', 'annual_return'
                ]
                display_cols = [col for col in display_cols if col in ticker_results.columns]

                print(tabulate(ticker_results[display_cols].head(10), headers='keys',
                              tablefmt='grid', showindex=False))
                print(f"Showing {min(10, len(ticker_results))} of {len(ticker_results)} opportunities")
            else:
                print(f"No {strategy_name.lower()} found for {ticker}")
        else:
            print(f"No {strategy_name.lower()} recommendations saved")


def export_recommendations(strategy: str = None, output_file: str = None):
    """Export recommendations to Excel"""
    rec_manager = RecommendationsManager()

    if strategy:
        results = rec_manager.load_latest_recommendation(strategy)
        if results.empty:
            print(f"No {strategy} recommendations found")
            return

        if not output_file:
            output_file = f"{strategy}_recommendations_export.xlsx"

        results.to_excel(output_file, index=False)
        print(f"Exported {len(results)} {strategy} recommendations to: {output_file}")
    else:
        # Export all
        if not output_file:
            output_file = "all_recommendations_export.xlsx"

        with pd.ExcelWriter(output_file) as writer:
            for strat in ['cc', 'csp', 'wheel']:
                results = rec_manager.load_latest_recommendation(strat)
                if not results.empty:
                    sheet_name = {'cc': 'Covered_Calls', 'csp': 'Cash_Secured_Puts', 'wheel': 'Wheel'}[strat]
                    results.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"Exported all recommendations to: {output_file}")


def cleanup_old_recommendations(days: int = 30):
    """Clean up old recommendation files"""
    print("="*80)
    print(f"CLEANING UP RECOMMENDATIONS OLDER THAN {days} DAYS")
    print("="*80 + "\n")

    rec_manager = RecommendationsManager()
    rec_manager.cleanup_old_recommendations(keep_days=days)

    print("\nDone!")


def main():
    """Main menu"""
    import argparse

    parser = argparse.ArgumentParser(description='View and manage saved recommendations')
    parser.add_argument('action', nargs='?', default='list',
                       choices=['list', 'view', 'search', 'export', 'cleanup'],
                       help='Action to perform')
    parser.add_argument('--strategy', '-s', choices=['cc', 'csp', 'wheel'],
                       help='Strategy to filter by')
    parser.add_argument('--ticker', '-t', help='Ticker to filter by')
    parser.add_argument('--output', '-o', help='Output file for export')
    parser.add_argument('--days', '-d', type=int, default=30,
                       help='Days to keep for cleanup')

    args = parser.parse_args()

    print("\n" + "#"*80)
    print("# RECOMMENDATIONS VIEWER")
    print("#"*80)

    if args.action == 'list':
        list_all_recommendations()

    elif args.action == 'view':
        view_latest_recommendations(args.strategy, args.ticker)

    elif args.action == 'search':
        if not args.ticker:
            print("Error: --ticker required for search")
            return
        search_recommendations(args.ticker)

    elif args.action == 'export':
        export_recommendations(args.strategy, args.output)

    elif args.action == 'cleanup':
        cleanup_old_recommendations(args.days)

    print("\n" + "#"*80)
    print("# Done!")
    print("#"*80)

    print("\nUsage examples:")
    print("  python view_recommendations.py list")
    print("  python view_recommendations.py view --strategy cc")
    print("  python view_recommendations.py search --ticker NVDA")
    print("  python view_recommendations.py export --strategy cc --output my_cc.xlsx")
    print("  python view_recommendations.py cleanup --days 30")


if __name__ == "__main__":
    # If no args, show list
    if len(sys.argv) == 1:
        list_all_recommendations()
    else:
        main()
