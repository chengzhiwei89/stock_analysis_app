"""
Simple check: Does MU show up in CSP scan results?
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data.option_extractor import OptionDataExtractor
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
import config

print("="*80)
print("CHECKING: Does MU appear in CSP scan results?")
print("="*80)

# Fetch options for a small set including MU
test_tickers = ['MU', 'AAPL', 'MSFT', 'AMD', 'NVDA']
print(f"\nFetching options for: {', '.join(test_tickers)}")

extractor = OptionDataExtractor()
options_data = extractor.fetch_and_store_options(test_tickers, num_expirations=6)

if options_data.empty:
    print("ERROR: No options data fetched")
    sys.exit(1)

print(f"Fetched {len(options_data)} option chains")

# Run CSP analysis with current config settings
analyzer = CashSecuredPutAnalyzer()
settings = {
    'min_premium': config.CASH_SECURED_PUT_SETTINGS['min_premium'],
    'min_annual_return': config.CASH_SECURED_PUT_SETTINGS['min_annual_return'],
    'min_days': config.CASH_SECURED_PUT_SETTINGS['min_days'],
    'max_days': config.CASH_SECURED_PUT_SETTINGS['max_days'],
    'min_prob_otm': config.CASH_SECURED_PUT_ADVANCED['min_prob_otm'],
    'min_delta': config.CASH_SECURED_PUT_ADVANCED['min_delta'],
    'max_delta': config.CASH_SECURED_PUT_ADVANCED['max_delta'],
    'min_volume': config.CASH_SECURED_PUT_ADVANCED['min_volume'],
}

print(f"\nRunning CSP analysis with filters:")
print(f"  Days: {settings['min_days']}-{settings['max_days']}")
print(f"  Min premium: ${settings['min_premium']}")
print(f"  Min annual return: {settings['min_annual_return']}%")
print(f"  Min prob OTM: {settings['min_prob_otm']}%")
print(f"  Max delta: {settings['max_delta']}")
print(f"  Min volume: {settings['min_volume']}")

results = analyzer.get_top_opportunities(
    options_data,
    min_premium=settings['min_premium'],
    min_annual_return=settings['min_annual_return'],
    min_days=settings['min_days'],
    max_days=settings['max_days'],
    min_prob_otm=settings['min_prob_otm'],
    min_delta=settings['min_delta'],
    max_delta=settings['max_delta'],
    min_volume=settings['min_volume'],
    top_n=100,
    available_cash=config.get_deployable_cash(),
    max_cash_per_position=config.CAPITAL_SETTINGS['max_cash_per_position']
)

print(f"\nTotal opportunities found: {len(results)}")

# Check which tickers made it
if not results.empty:
    tickers_found = results['ticker'].unique()
    print(f"\nTickers in results: {', '.join(sorted(tickers_found))}")

    if 'MU' in tickers_found:
        print(f"\nSUCCESS: MU found! ({len(results[results['ticker'] == 'MU'])} options)")
        print("\nMU opportunities:")
        mu_results = results[results['ticker'] == 'MU'].head(10)
        print(mu_results[['ticker', 'strike', 'days_to_expiration', 'premium_received',
                          'annual_return', 'prob_otm', 'delta', 'volume']].to_string(index=False))
    else:
        print(f"\nFAILURE: MU NOT in results")
        print(f"\nTickers that DID pass filters:")
        for ticker in tickers_found:
            count = len(results[results['ticker'] == ticker])
            print(f"  {ticker}: {count} options")

        print("\n" + "="*80)
        print("SUGGESTION: Try relaxing filters in config.py")
        print("="*80)
        print("Current filters may be too strict for MU. Try:")
        print("  1. Lower min_prob_otm from 65% to 60%")
        print("  2. Change max_delta from -0.30 to -0.35 or -0.40")
        print("  3. Lower min_volume from 100 to 50")
        print("  4. Lower min_annual_return from 12% to 10%")
else:
    print("\nNo opportunities found for ANY ticker with current filters")

print("\n" + "="*80)
