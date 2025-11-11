"""
Debug why no opportunities are found with the new filter
"""
import pandas as pd
from datetime import datetime

# Load data
df = pd.read_csv('data/option_chains/options_data_20251027_233300.csv')

# Focus on GOOGL puts
googl_puts = df[(df['ticker'] == 'GOOGL') & (df['option_type'] == 'put')].copy()

# Current price
current_price = 266.35

# Calculate days to expiration
googl_puts['days'] = (pd.to_datetime(googl_puts['expiration']) - datetime.now()).dt.days

# Calculate distance_pct manually (as greeks_calculator does)
googl_puts['distance_from_price'] = current_price - googl_puts['strike']
googl_puts['distance_pct'] = (googl_puts['distance_from_price'] / current_price) * 100

print("="*80)
print("DEBUGGING FILTER PIPELINE FOR GOOGL")
print("="*80)
print(f"\nCurrent GOOGL Price: ${current_price:.2f}")
print(f"\nTotal GOOGL puts: {len(googl_puts)}")

# Filter 1: Days 25-60
step1 = googl_puts[(googl_puts['days'] >= 25) & (googl_puts['days'] <= 60)]
print(f"\nAfter days filter (25-60): {len(step1)}")

# Filter 2: Bid >= 0.50
step2 = step1[step1['bid'] >= 0.50]
print(f"After bid >= $0.50: {len(step2)}")

# Filter 3: Volume >= 100
step3 = step2[step2['volume'] >= 100]
print(f"After volume >= 100: {len(step3)}")

# Filter 4: Distance >= 2%
step4 = step3[step3['distance_pct'] >= 2.0]
print(f"After distance >= 2%: {len(step4)}")

if len(step4) > 0:
    print("\n" + "="*80)
    print("OPPORTUNITIES THAT SHOULD PASS ALL FILTERS:")
    print("="*80)
    for idx, row in step4.head(5).iterrows():
        print(f"\nStrike ${row['strike']:.0f}:")
        print(f"  Distance: {row['distance_pct']:.2f}%")
        print(f"  Days: {row['days']:.0f}")
        print(f"  Bid: ${row['bid']:.2f}")
        print(f"  Volume: {row['volume']:.0f}")
else:
    print("\n" + "="*80)
    print("WHY ARE WE GETTING ZERO?")
    print("="*80)

    # Check what's in step3 before distance filter
    if len(step3) > 0:
        print(f"\nStep3 (before distance filter) has {len(step3)} options")
        print("\nClosest strikes in step3:")
        step3_sorted = step3.sort_values('distance_pct')
        for idx, row in step3_sorted.head(5).iterrows():
            print(f"  ${row['strike']:.0f}: distance={row['distance_pct']:.2f}%, bid=${row['bid']:.2f}, vol={row['volume']:.0f}")

        # Check if distance_pct might be calculated differently
        print(f"\nChecking distance_pct values:")
        print(f"  Min: {step3['distance_pct'].min():.2f}%")
        print(f"  Max: {step3['distance_pct'].max():.2f}%")
        print(f"  >= 2%: {len(step3[step3['distance_pct'] >= 2.0])}")
    else:
        print("\nStep3 is already empty! Volume filter is too strict.")
        if len(step2) > 0:
            print(f"\nBefore volume filter: {len(step2)} options")
            print("Volume distribution:")
            print(step2['volume'].describe())
