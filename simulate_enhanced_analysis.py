"""
Simulate enhanced analysis using lastPrice (since market is closed and bid=0)
This shows what you WOULD see during market hours
"""
import pandas as pd
import sys
sys.path.insert(0, '.')

from src.analysis.enhanced_probability import EnhancedProbabilityAnalyzer

# Read the options data
df = pd.read_csv('data/option_chains/options_data_20251027_145208.csv')

# Filter to puts only
puts = df[df['option_type'] == 'put'].copy()

# Use lastPrice instead of bid (since market is closed)
puts['bid'] = puts['lastPrice']

# Calculate days to expiration
from datetime import datetime
puts['days_to_expiration'] = (
    pd.to_datetime(puts['expiration']) - datetime.now()
).dt.days

# Filter by basic criteria
filtered = puts[
    (puts['bid'] >= 0.50) &
    (puts['days_to_expiration'] >= 20) &
    (puts['days_to_expiration'] <= 65) &
    (puts['volume'].notna()) &
    (puts['volume'] >= 50)
].copy()

print(f"Found {len(filtered)} options matching basic criteria")
print(f"(Using lastPrice since market is closed)\n")

# Pick top 10 for demo
sample = filtered.nlargest(10, 'volume')[['ticker', 'strike', 'expiration', 'bid',
                                           'volume', 'current_stock_price', 'days_to_expiration']]

print("="*80)
print("TOP 10 OPTIONS BY VOLUME (Market Closed - Using Last Price)")
print("="*80)
print(sample.to_string(index=False))

# Now run enhanced analysis on a few
print("\n" + "="*80)
print("ENHANCED ANALYSIS DEMO - TOP 3 OPTIONS")
print("="*80)

analyzer = EnhancedProbabilityAnalyzer()

for i, (idx, row) in enumerate(sample.head(3).iterrows(), 1):
    print(f"\n{i}. {row['ticker']} ${row['strike']:.0f} PUT - {row['days_to_expiration']} days")
    print(f"   {'='*76}")
    print(f"   Current Price: ${row['current_stock_price']:.2f}")
    print(f"   Strike: ${row['strike']:.0f}")
    print(f"   Premium (lastPrice): ${row['bid']:.2f}")
    print(f"   Volume: {row['volume']:.0f}")

    # Calculate enhanced probability (without BS prob since we don't have Greeks)
    result = analyzer.calculate_enhanced_probability(
        ticker=row['ticker'],
        strike=row['strike'],
        current_price=row['current_stock_price'],
        days_to_expiration=row['days_to_expiration'],
        option_type='put',
        black_scholes_prob=None  # We'll estimate this
    )

    print(f"\n   ENHANCED ANALYSIS SCORES:")
    print(f"   • Technical Score: {result['technical_score']:.0f}/100 ", end="")
    if result['technical_score'] > 70:
        print("(Strong - Uptrend)")
    elif result['technical_score'] > 55:
        print("(Good)")
    elif result['technical_score'] > 45:
        print("(Neutral)")
    else:
        print("(Weak - Downtrend)")

    print(f"   • Fundamental Score: {result['fundamental_score']:.0f}/100 ", end="")
    if result['fundamental_score'] > 70:
        print("(High Quality Company)")
    elif result['fundamental_score'] > 55:
        print("(Good Quality)")
    else:
        print("(Average Quality)")

    print(f"   • Sentiment Score: {result['sentiment_score']:.0f}/100 ", end="")
    if result['sentiment_score'] > 70:
        print("(Bullish)")
    elif result['sentiment_score'] > 55:
        print("(Positive)")
    elif result['sentiment_score'] > 45:
        print("(Neutral)")
    else:
        print("(Bearish)")

    print(f"   • Event Risk Score: {result['event_risk_score']:.0f}/100 ", end="")
    if result['event_risk_score'] > 70:
        print("(Low Risk - No earnings soon)")
    elif result['event_risk_score'] > 50:
        print("(Moderate Risk)")
    else:
        print("(HIGH RISK - Earnings imminent!)")

    print(f"\n   • COMPOSITE SCORE: {result['composite_score']:.0f}/100")

    # Give recommendation
    if result['composite_score'] > 70 and result['event_risk_score'] > 60:
        rec = "EXCELLENT - Strong across all factors"
    elif result['composite_score'] > 60:
        rec = "GOOD - Solid opportunity"
    elif result['composite_score'] > 50:
        rec = "FAIR - Acceptable"
    elif result['event_risk_score'] < 40:
        rec = "CAUTION - High event risk (earnings soon)"
    else:
        rec = "CAUTION - Weak factors"

    print(f"   • RECOMMENDATION: {rec}")

    print(f"\n   {'─'*76}")

print("\n" + "="*80)
print("NOTE: Market is currently CLOSED")
print("="*80)
print("\nTo see live bid/ask prices and run full analysis:")
print("  1. Run during market hours (9:30 AM - 4:00 PM ET)")
print("  2. Or accept that lastPrice is yesterday's closing price")
print("\nDuring market hours, you'll see:")
print("  • Live bid/ask spreads")
print("  • Real-time Black-Scholes probabilities")
print("  • Enhanced probabilities adjusted for technical/fundamental factors")
print("  • Complete comparison table")

print("\n" + "="*80)
print("WHAT THE ENHANCED ANALYSIS TELLS YOU")
print("="*80)
print("\nWithout enhanced analysis:")
print("  'This put has 68% probability OTM' - based only on volatility")
print("\nWith enhanced analysis:")
print("  'This put has 68% BS prob, BUT:")
print("    - Stock in strong uptrend (Technical: 85/100)")
print("    - High quality company (Fundamental: 82/100)")
print("    - Bullish sentiment (Sentiment: 74/100)")
print("    - No earnings for 30 days (Event Risk: 90/100)")
print("  → Enhanced prob: 75% (+7% safer!)'")
print("\nThis gives you an EDGE beyond basic Black-Scholes!")

print("\n" + "="*80 + "\n")
