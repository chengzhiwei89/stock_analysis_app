"""
Check for near-ATM options that might slip through filters
"""
import pandas as pd

# Load the latest options data
df = pd.read_csv('data/option_chains/options_data_20251027_225840.csv')

# Focus on GOOGL puts
googl_puts = df[(df['ticker'] == 'GOOGL') & (df['option_type'] == 'put')].copy()

# Current price
current_price = 265.75

# Calculate distance from current
googl_puts['distance_pct'] = ((current_price - googl_puts['strike']) / current_price * 100)

# Filter for options close to ATM (OTM but within 0-3% below current)
# Positive distance_pct = OTM, Negative = ITM
near_atm = googl_puts[
    (googl_puts['distance_pct'] >= 0) &
    (googl_puts['distance_pct'] <= 3.0)
].sort_values('distance_pct')

print("="*80)
print("NEAR-ATM GOOGL PUT OPTIONS (within 2% of current price)")
print("="*80)
print(f"\nCurrent GOOGL Price: ${current_price:.2f}\n")

for idx, row in near_atm.head(10).iterrows():
    distance = current_price - row['strike']
    distance_pct = row['distance_pct']

    print(f"Strike ${row['strike']:.0f}:")
    print(f"  Distance: ${distance:.2f} below current ({distance_pct:.2f}%)")
    print(f"  Expiration: {row['expiration']}")
    print(f"  Bid: ${row['bid']:.2f}")
    print(f"  In The Money: {row['inTheMoney']}")
    print(f"  -> RISK: {'HIGH - Too close to ATM!' if distance_pct < 1.0 else 'MODERATE - Marginal cushion' if distance_pct < 2.0 else 'OK'}")
    print()

print("="*80)
print("RECOMMENDATION")
print("="*80)
print("\nProblem: Options within 1% of current price have:")
print("  - Very high assignment risk")
print("  - Minimal safety cushion")
print("  - Near 50/50 probability")
print("\nSolution: Add minimum discount filter to config.py")
print("  - Require strikes at least 2-3% below current")
print("  - This ensures meaningful safety margin")
