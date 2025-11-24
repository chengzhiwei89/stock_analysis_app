# run_leaps_analysis.py

import pandas as pd
from datetime import datetime
import os

from src.analysis.leaps_analysis import find_leaps_opportunities
from src.visualization.html_generator import HTMLDashboardGenerator

# Configuration for the LEAPS analysis
config = {
    'days_to_expiration_min': 365,
    'max_ask_price': 5.00,
    'min_open_interest': 100,
    'min_volume': 50,
    'otm_percentage_min': 5,
}

# Watchlist of bullish stocks
# This could be loaded from a file in a future enhancement
watchlist = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'AMD']

def main():
    """
    Main function to run the LEAPS analysis and generate outputs.
    """
    print("Starting LEAPS Call Option Analysis...")
    
    # Find opportunities
    opportunities_df = find_leaps_opportunities(watchlist, config)

    if opportunities_df.empty:
        print("\nNo LEAPS opportunities found matching the criteria.")
        return

    print(f"\nFound {len(opportunities_df)} total opportunities across {len(watchlist)} stocks.")
    
    # --- Output Generation ---
    
    # 1. Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"leaps_calls_{timestamp}.csv"
    csv_path = os.path.join('output', csv_filename)
    os.makedirs('output', exist_ok=True)
    
    print(f"Saving results to {csv_path}")
    opportunities_df.to_csv(csv_path, index=False)

    # 2. Generate HTML Dashboard
    print("Generating HTML dashboard...")
    
    dashboard_generator = HTMLDashboardGenerator()
    html_path = dashboard_generator.generate(
        leaps_results=opportunities_df,
        metadata={'scan_type': 'LEAPS Call Bets'}
    )
    
    print(f"Dashboard saved to {html_path}")
    
    print("\nLEAPS Call Option Analysis finished.")

if __name__ == "__main__":
    main()
