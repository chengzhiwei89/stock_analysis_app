"""
Quick test for the full table generator
"""
import pandas as pd
from src.visualization.full_table_generator import FullTableGenerator

# Create sample data
data = {
    'ticker': ['AAPL', 'MSFT', 'NVDA', 'AMD', 'TSLA'],
    'strike': [175.0, 400.0, 850.0, 140.0, 240.0],
    'days_to_expiration': [30, 35, 40, 32, 38],
    'premium_received': [2.50, 5.75, 12.30, 3.45, 6.80],
    'annual_return': [25.5, 30.2, 35.8, 28.4, 32.1],
    'prob_otm': [75.5, 78.2, 82.1, 76.8, 79.3],
    'volume': [1500, 2300, 3100, 1800, 2500],
    'current_stock_price': [180.50, 410.25, 865.40, 145.30, 248.75]
}

df = pd.DataFrame(data)

# Generate table
generator = FullTableGenerator(output_dir='output/tables')

metadata = {
    'scan_timestamp': '2025-12-02 10:30:00',
    'market_status': 'OPEN',
    'tickers': ['AAPL', 'MSFT', 'NVDA', 'AMD', 'TSLA'],
    'scan_type': 'Test Scan',
    'criteria': {
        'min_days': 30,
        'max_days': 45,
        'min_premium': 1.0,
        'min_annual_return': 20.0
    }
}

try:
    output_path = generator.generate(
        df=df,
        title="Test Full Table",
        metadata=metadata
    )
    print(f"SUCCESS! Table generated at: {output_path}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
