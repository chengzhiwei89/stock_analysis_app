import pandas as pd
from src.data.greeks_calculator import GreeksCalculator

# Load data
df = pd.read_csv('data/option_chains/options_data_20251027_233300.csv')

# Get GOOGL $245 PUT
googl = df[(df['ticker']=='GOOGL') & (df['strike']==245) & (df['option_type']=='put')].copy()

# Enrich with greeks
gc = GreeksCalculator()
googl = gc.enrich_option_data(googl)

print("GOOGL $245 PUT - Delta Analysis")
print("="*60)
print(f"Columns available: {googl.columns.tolist()}")
print()
if 'delta' in googl.columns:
    print(googl[['expiration','strike','bid','delta']].to_string(index=False))
else:
    print("ERROR: Delta column not calculated!")
    print(googl[['expiration','strike','bid']].to_string(index=False))

print("\n" + "="*60)
print("FILTER ANALYSIS")
print("="*60)
print(f"Config: max_delta = -0.35")
print(f"Filter logic: delta <= -0.35 (more negative = closer to ATM)")
print()

for idx, row in googl.iterrows():
    if row['bid'] == 3.90:  # Nov 28 expiration
        print(f"Nov 28 expiration:")
        print(f"  Delta: {row['delta']:.3f}")
        print(f"  Passes filter (delta <= -0.35)? {row['delta'] <= -0.35}")
        if row['delta'] > -0.35:
            print(f"  REJECTED: Delta {row['delta']:.3f} is > -0.35 (too far OTM)")
