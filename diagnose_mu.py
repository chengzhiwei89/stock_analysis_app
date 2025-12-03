"""
Diagnostic script to check why MU might not be showing up
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.option_extractor import OptionDataExtractor
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
import config
import pandas as pd

print("="*80)
print("DIAGNOSTIC: Checking MU (Micron) Options")
print("="*80)

# Fetch MU options only
extractor = OptionDataExtractor()
print("\nFetching MU options data...")
mu_data = extractor.fetch_and_store_options(['MU'], num_expirations=6)

if mu_data.empty:
    print("ERROR: No options data fetched for MU")
    sys.exit(1)

print(f"\nFetched {len(mu_data)} MU option chains")

# Filter for puts only
mu_puts = mu_data[mu_data['option_type'] == 'put'].copy()
print(f"Found {len(mu_puts)} put options")

if mu_puts.empty:
    print("ERROR: No put options found for MU")
    sys.exit(1)

# Show current MU stock price
current_price = mu_puts['current_stock_price'].iloc[0]
print(f"\nMU Current Stock Price: ${current_price:.2f}")

# Check filters one by one
print("\n" + "="*80)
print("FILTER ANALYSIS - Checking each criterion")
print("="*80)

settings = {
    'min_premium': config.CASH_SECURED_PUT_SETTINGS['min_premium'],
    'min_annual_return': config.CASH_SECURED_PUT_SETTINGS['min_annual_return'],
    'min_days': config.CASH_SECURED_PUT_SETTINGS['min_days'],
    'max_days': config.CASH_SECURED_PUT_SETTINGS['max_days'],
    'min_prob_otm': config.CASH_SECURED_PUT_ADVANCED['min_prob_otm'],
    'max_delta': config.CASH_SECURED_PUT_ADVANCED['max_delta'],
    'min_volume': config.CASH_SECURED_PUT_ADVANCED['min_volume'],
}

print(f"\nActive Filters:")
for key, value in settings.items():
    print(f"  {key}: {value}")

print(f"\nAvailable columns in MU data:")
print(mu_puts.columns.tolist())

# Apply filters step by step and show what gets filtered
original_count = len(mu_puts)
df = mu_puts.copy()

print(f"\n\nStarting with {original_count} MU put options...")

# Filter 1: Days to expiration
df_step = df[(df['days_to_expiration'] >= settings['min_days']) &
             (df['days_to_expiration'] <= settings['max_days'])]
print(f"\n1. After DTE filter ({settings['min_days']}-{settings['max_days']} days): {len(df_step)} options")
if len(df_step) < len(df):
    print(f"   FILTERED OUT: {len(df) - len(df_step)} options")
df = df_step

# Filter 2: Premium
if 'bid' in df.columns:
    df_step = df[df['bid'] >= settings['min_premium']]
    print(f"\n2. After premium filter (>=${settings['min_premium']}): {len(df_step)} options")
    if len(df_step) < len(df):
        print(f"   FILTERED OUT: {len(df) - len(df_step)} options")
        print(f"   Example premiums: {df['bid'].head(10).tolist()}")
    df = df_step

# Filter 3: Volume
if 'volume' in df.columns:
    df_step = df[df['volume'] >= settings['min_volume']]
    print(f"\n3. After volume filter (>={settings['min_volume']}): {len(df_step)} options")
    if len(df_step) < len(df):
        print(f"   FILTERED OUT: {len(df) - len(df_step)} options")
        print(f"   Volume distribution:")
        print(f"     Min: {df['volume'].min()}, Max: {df['volume'].max()}, Avg: {df['volume'].mean():.0f}")
    df = df_step

# Calculate annual return if not present
if 'annual_return' not in df.columns and 'bid' in df.columns:
    df['annual_return'] = (df['bid'] / df['strike']) * (365 / df['days_to_expiration']) * 100

# Filter 4: Annual return
if 'annual_return' in df.columns:
    df_step = df[df['annual_return'] >= settings['min_annual_return']]
    print(f"\n4. After annual return filter (>={settings['min_annual_return']}%): {len(df_step)} options")
    if len(df_step) < len(df):
        print(f"   FILTERED OUT: {len(df) - len(df_step)} options")
        print(f"   Annual return range: {df['annual_return'].min():.1f}% - {df['annual_return'].max():.1f}%")
    df = df_step

# Filter 5: Delta
if 'delta' in df.columns and settings['max_delta'] is not None:
    df_step = df[df['delta'] >= settings['max_delta']]
    print(f"\n5. After delta filter (>={settings['max_delta']}): {len(df_step)} options")
    if len(df_step) < len(df):
        print(f"   FILTERED OUT: {len(df) - len(df_step)} options")
        print(f"   Delta range: {df['delta'].min():.3f} - {df['delta'].max():.3f}")
    df = df_step

# Filter 6: Probability OTM
if 'prob_otm' in df.columns:
    df_step = df[df['prob_otm'] >= settings['min_prob_otm']]
    print(f"\n6. After prob OTM filter (>={settings['min_prob_otm']}%): {len(df_step)} options")
    if len(df_step) < len(df):
        print(f"   FILTERED OUT: {len(df) - len(df_step)} options")
        print(f"   Prob OTM range: {df['prob_otm'].min():.1f}% - {df['prob_otm'].max():.1f}%")
    df = df_step

# Filter 7: Capital requirement
max_cash_per_position = config.CAPITAL_SETTINGS['max_cash_per_position']
df['capital_required'] = df['strike'] * 100
df_step = df[df['capital_required'] <= max_cash_per_position]
print(f"\n7. After capital filter (<=${max_cash_per_position:,.0f}): {len(df_step)} options")
if len(df_step) < len(df):
    print(f"   FILTERED OUT: {len(df) - len(df_step)} options")
    print(f"   Capital required range: ${df['capital_required'].min():,.0f} - ${df['capital_required'].max():,.0f}")
df = df_step

print("\n" + "="*80)
print(f"FINAL RESULT: {len(df)} MU put options pass all filters")
print("="*80)

if len(df) > 0:
    print("\nSUCCESS: MU HAS OPTIONS THAT PASS! Showing top 5:")
    display_cols = ['strike', 'expiration', 'days_to_expiration', 'bid',
                   'volume', 'delta', 'prob_otm', 'annual_return']
    display_cols = [c for c in display_cols if c in df.columns]
    print(df[display_cols].head(5).to_string(index=False))
else:
    print("\nFAILURE: NO MU OPTIONS PASS ALL FILTERS")
    print("\nSuggestions to see MU in results:")
    print("  1. Lower min_prob_otm (currently 65%) in config.py")
    print("  2. Increase max_delta (currently -0.30, try -0.35 or -0.40) in config.py")
    print("  3. Lower min_volume (currently 100) in config.py")
    print("  4. Lower min_annual_return (currently 12%) in config.py")
    print("  5. Expand DTE range in config.py")

print("\n" + "="*80)
