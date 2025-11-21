"""
Test script for HTML Dashboard Generator
Creates a dashboard with sample data to verify functionality
"""

import pandas as pd
from datetime import datetime, timedelta
from src.visualization.html_generator import HTMLDashboardGenerator

# Sample CSP data
csp_sample_data = [
    {
        'ticker': 'GOOGL',
        'strike': 260,
        'current_stock_price': 266.35,
        'expiration': (datetime.now() + timedelta(days=24)).strftime('%Y-%m-%d'),
        'days_to_expiration': 24,
        'premium_received': 8.20,
        'annual_return': 48.0,
        'prob_otm': 61.7,
        'enhanced_prob_otm': 71.1,
        'prob_adjustment': 9.4,
        'distance_pct': -2.5,
        'volume': 1200,
        'openInterest': 3400,
        'price_source': 'bid'
    },
    {
        'ticker': 'GOOGL',
        'strike': 255,
        'current_stock_price': 266.35,
        'expiration': (datetime.now() + timedelta(days=24)).strftime('%Y-%m-%d'),
        'days_to_expiration': 24,
        'premium_received': 6.25,
        'annual_return': 37.3,
        'prob_otm': 68.5,
        'enhanced_prob_otm': 78.0,
        'prob_adjustment': 9.5,
        'distance_pct': -4.2,
        'volume': 980,
        'openInterest': 2800
    },
    {
        'ticker': 'AAPL',
        'strike': 260,
        'current_stock_price': 265.69,
        'expiration': (datetime.now() + timedelta(days=24)).strftime('%Y-%m-%d'),
        'days_to_expiration': 24,
        'premium_received': 5.10,
        'annual_return': 29.8,
        'prob_otm': 63.2,
        'enhanced_prob_otm': 68.7,
        'prob_adjustment': 5.5,
        'distance_pct': -2.1,
        'volume': 1500,
        'openInterest': 4200
    },
    {
        'ticker': 'MSFT',
        'strike': 520,
        'current_stock_price': 532.65,
        'expiration': (datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d'),
        'days_to_expiration': 31,
        'premium_received': 12.50,
        'annual_return': 27.5,
        'prob_otm': 65.8,
        'enhanced_prob_otm': 72.3,
        'prob_adjustment': 6.5,
        'distance_pct': -2.4,
        'volume': 2100,
        'openInterest': 5600
    },
    {
        'ticker': 'SPY',
        'strike': 670,
        'current_stock_price': 683.49,
        'expiration': (datetime.now() + timedelta(days=17)).strftime('%Y-%m-%d'),
        'days_to_expiration': 17,
        'premium_received': 15.75,
        'annual_return': 35.2,
        'prob_otm': 69.5,
        'enhanced_prob_otm': 76.8,
        'prob_adjustment': 7.3,
        'distance_pct': -2.0,
        'volume': 8500,
        'openInterest': 15200
    }
]

# Sample CC data
cc_sample_data = [
    {
        'ticker': 'AAPL',
        'current_stock_price': 265.69,
        'strike': 270,
        'expiration': (datetime.now() + timedelta(days=24)).strftime('%Y-%m-%d'),
        'days_to_expiration': 24,
        'premium_received': 3.85,
        'annual_return': 22.1,
        'downside_protection': 3.85,
        'downside_protection_pct': 1.45,
        'distance_pct': 1.6,
        'prob_otm': 58.2,
        'volume': 1800,
        'openInterest': 4500
    },
    {
        'ticker': 'MSFT',
        'current_stock_price': 532.65,
        'strike': 540,
        'expiration': (datetime.now() + timedelta(days=24)).strftime('%Y-%m-%d'),
        'days_to_expiration': 24,
        'premium_received': 8.90,
        'annual_return': 24.5,
        'downside_protection': 8.90,
        'downside_protection_pct': 1.67,
        'distance_pct': 1.4,
        'prob_otm': 55.8,
        'volume': 2200,
        'openInterest': 6100
    },
    {
        'ticker': 'GOOGL',
        'current_stock_price': 266.35,
        'strike': 270,
        'expiration': (datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d'),
        'days_to_expiration': 31,
        'premium_received': 5.20,
        'annual_return': 23.0,
        'downside_protection': 5.20,
        'downside_protection_pct': 1.95,
        'distance_pct': 1.4,
        'prob_otm': 60.5,
        'volume': 1100,
        'openInterest': 3200
    }
]

# Sample Wheel data
wheel_sample_data = [
    {
        'ticker': 'AMD',
        'current_price': 252.92,
        'strike': 240,
        'expiration': (datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d'),
        'days': 31,
        'premium': 11.97,
        'discount_pct': 5.1,
        'net_entry': 228.03,
        'total_discount_pct': 9.8,
        'annual_return': 58.6,
        'volume': 1450,
        'prob_assignment': 28.5
    },
    {
        'ticker': 'NVDA',
        'current_price': 186.26,
        'strike': 175,
        'expiration': (datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d'),
        'days': 31,
        'premium': 8.25,
        'discount_pct': 6.0,
        'net_entry': 166.75,
        'total_discount_pct': 10.5,
        'annual_return': 55.2,
        'volume': 2100,
        'prob_assignment': 31.2
    },
    {
        'ticker': 'TSLA',
        'current_price': 433.72,
        'strike': 410,
        'expiration': (datetime.now() + timedelta(days=24)).strftime('%Y-%m-%d'),
        'days': 24,
        'premium': 18.50,
        'discount_pct': 5.5,
        'net_entry': 391.50,
        'total_discount_pct': 9.7,
        'annual_return': 67.8,
        'volume': 3200,
        'prob_assignment': 29.8
    }
]

# Create DataFrames
csp_df = pd.DataFrame(csp_sample_data)
cc_df = pd.DataFrame(cc_sample_data)
wheel_df = pd.DataFrame(wheel_sample_data)

# Metadata
metadata = {
    'scan_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'market_status': 'OPEN',
    'tickers': ['GOOGL', 'AAPL', 'MSFT', 'AMD', 'NVDA', 'TSLA', 'SPY']
}

print("=" * 80)
print("TESTING HTML DASHBOARD GENERATOR")
print("=" * 80)
print()
print("Creating sample data...")
print(f"  CSP opportunities: {len(csp_df)}")
print(f"  CC opportunities: {len(cc_df)}")
print(f"  Wheel opportunities: {len(wheel_df)}")
print()

# Generate dashboard
print("Generating HTML dashboard...")
generator = HTMLDashboardGenerator(config={
    'theme': 'light',
    'max_opportunities': 20,
    'output_dir': 'output/dashboards'
})

output_path = generator.generate(
    csp_results=csp_df,
    cc_results=cc_df,
    wheel_results=wheel_df,
    metadata=metadata
)

print(f"SUCCESS! Dashboard generated: {output_path}")
print()
print("=" * 80)
print("To view the dashboard:")
print("=" * 80)
print(f"1. Open your browser")
print(f"2. Navigate to: file:///{output_path.replace(chr(92), '/')}")
print("   OR")
print(f"   Open the file directly: {output_path}")
print()
print("The dashboard should display:")
print("  - Summary cards with totals and averages")
print("  - CSP opportunities table (5 rows)")
print("  - CC opportunities table (3 rows)")
print("  - Wheel opportunities table (3 rows)")
print("  - Interactive sorting (click column headers)")
print("  - Copy buttons for each trade")
print()
print("=" * 80)
