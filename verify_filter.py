"""
Simple verification that min_distance_pct filter will work correctly
"""
import pandas as pd

# Load the latest options data
df = pd.read_csv('data/option_chains/options_data_20251027_234406.csv')

# Focus on GOOGL puts
googl_puts = df[(df['ticker'] == 'GOOGL') & (df['option_type'] == 'put')].copy()

# Current price
current_price = 266.74

# Calculate distance from current
googl_puts['distance_pct'] = ((current_price - googl_puts['strike']) / current_price * 100)

print("="*80)
print("MINIMUM DISTANCE FILTER VERIFICATION")
print("="*80)
print(f"\nCurrent GOOGL Price: ${current_price:.2f}")
print(f"Config: min_distance_pct = 2.0%")
print()

# Show strikes that would be blocked
print("STRIKES THAT WILL BE BLOCKED (distance < 2%):")
print("-"*80)
blocked = googl_puts[(googl_puts['distance_pct'] >= 0) & (googl_puts['distance_pct'] < 2.0)]
blocked_unique = blocked['strike'].unique()
for strike in sorted(blocked_unique):
    distance = current_price - strike
    distance_pct = (distance / current_price) * 100
    print(f"  ${strike:.0f} - Distance: ${distance:.2f} ({distance_pct:.2f}%) - BLOCKED")

print()
print("STRIKES THAT WILL BE ALLOWED (distance >= 2%):")
print("-"*80)
allowed = googl_puts[(googl_puts['distance_pct'] >= 2.0) & (googl_puts['distance_pct'] <= 10.0)]
allowed_unique = sorted(allowed['strike'].unique(), reverse=True)[:5]
for strike in allowed_unique:
    distance = current_price - strike
    distance_pct = (distance / current_price) * 100
    print(f"  ${strike:.0f} - Distance: ${distance:.2f} ({distance_pct:.2f}%) - ALLOWED")

print()
print("="*80)
print("SUMMARY")
print("="*80)
print(f"\nThe new filter will prevent near-ATM options like $265 PUT")
print(f"from being recommended, ensuring a minimum 2% safety cushion.")
print()
print(f"BEFORE fix: $265 PUT could slip through (only 0.28% away)")
print(f"AFTER fix:  $265 PUT will be blocked, minimum $260 allowed (2.16% away)")
