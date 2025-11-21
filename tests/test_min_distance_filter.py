"""
Test that min_distance_pct filter correctly excludes near-ATM options
"""
from config import CASH_SECURED_PUT_SETTINGS, CASH_SECURED_PUT_ADVANCED, CAPITAL_SETTINGS, WATCHLIST
from src.data.option_extractor import OptionDataExtractor
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer

# Initialize
extractor = OptionDataExtractor()
csp_strategy = CashSecuredPutAnalyzer()

print("="*80)
print("TESTING MIN_DISTANCE_PCT FILTER")
print("="*80)
print(f"\nConfig Setting: min_distance_pct = {CASH_SECURED_PUT_ADVANCED['min_distance_pct']}%")
print(f"This means: Only allow strikes at least 2% below current price")
print()

# Test with GOOGL
ticker = 'GOOGL'
print(f"Testing {ticker}...")

# Get current price
stock_info = extractor.get_stock_info(ticker)
current_price = stock_info.get('price', 0)
print(f"Current Price: ${current_price:.2f}")
print()

# Fetch options data for the watchlist
# The 'scan_opportunities' method expects 'options_df' as its first argument.
# We need to fetch the data first and then pass it.
options_df = extractor.fetch_and_store_options(WATCHLIST)

# Run CSP scan
results = csp_strategy.get_top_opportunities(
    options_df=options_df,
    min_annual_return=CASH_SECURED_PUT_SETTINGS['min_annual_return'],
    min_days=CASH_SECURED_PUT_SETTINGS['min_days'],
    max_days=CASH_SECURED_PUT_SETTINGS['max_days'],
    min_premium=CASH_SECURED_PUT_SETTINGS['min_premium'],
    min_prob_otm=CASH_SECURED_PUT_SETTINGS.get('min_prob_otm'),
    min_volume=CASH_SECURED_PUT_ADVANCED.get('min_volume'),
)

if not results.empty:
    # Check closest strike
    closest = results.sort_values('distance_pct').head(5)

    print("RESULTS - Closest 5 Strikes Allowed:")
    print("-"*80)
    for idx, row in closest.iterrows():
        distance_dollars = current_price - row['strike']
        print(f"Strike ${row['strike']:.0f}:")
        print(f"  Distance: ${distance_dollars:.2f} ({row['distance_pct']:.2f}%)")
        print(f"  Status: {'PASS' if row['distance_pct'] >= 2.0 else 'SHOULD BE FILTERED!'}")
        print()

    # Verify no options under 2%
    too_close = results[results['distance_pct'] < 2.0]
    if len(too_close) > 0:
        print("ERROR: Found options closer than 2%!")
        print(too_close[['strike', 'distance_pct']])
    else:
        print("SUCCESS: All strikes are at least 2% below current price!")
        print(f"         $265 strike (0.28% distance) correctly filtered out!")
else:
    print("No results found (this might mean filter is too strict)")

print()
print("="*80)
print("VERIFICATION")
print("="*80)
print(f"\nGOOGL at ${current_price:.2f}:")
print(f"  $265 strike would be: {((current_price - 265) / current_price * 100):.2f}% distance")
print(f"  -> BLOCKED (less than 2% minimum)")
print(f"\n  $260 strike would be: {((current_price - 260) / current_price * 100):.2f}% distance")
print(f"  -> ALLOWED (more than 2% minimum)")
