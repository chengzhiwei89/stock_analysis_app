"""
Research and evaluate tickers for options income strategies
Analyzes: Metals, Tech, and S&P 500 stocks
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

# Candidate tickers by category
CANDIDATES = {
    'METALS': {
        'Precious Metals': ['GLD', 'SLV', 'GOLD', 'NEM', 'AEM', 'FNV', 'WPM'],
        'Industrial Metals': ['FCX', 'SCCO', 'TECK', 'AA', 'X', 'CLF', 'MT'],
        'Steel/Copper': ['STLD', 'NUE', 'RS', 'CMC'],
        'Mining': ['RIO', 'BHP', 'VALE', 'SCCO']
    },
    'TECH': {
        'Mega Cap': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
        'Semiconductors': ['AMD', 'INTC', 'QCOM', 'AVGO', 'MU', 'AMAT', 'LRCX', 'KLAC', 'MCHP', 'NXPI'],
        'Software': ['CRM', 'ORCL', 'ADBE', 'NOW', 'SNOW', 'PLTR', 'PANW', 'CRWD', 'DDOG'],
        'Cloud/SaaS': ['MSTR', 'COIN', 'SQ', 'PYPL', 'SHOP'],
        'Hardware': ['DELL', 'HPQ', 'WDC', 'STX'],
        'Networking': ['CSCO', 'ANET']
    },
    'SP500_HIGH_LIQUIDITY': {
        'Financials': ['JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'AXP', 'BLK', 'SCHW'],
        'Healthcare': ['UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'PFE', 'AMGN'],
        'Consumer': ['WMT', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX', 'COST'],
        'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'MPC', 'OXY'],
        'Industrials': ['BA', 'CAT', 'GE', 'RTX', 'LMT', 'UPS', 'HON', 'DE'],
        'Telecom/Media': ['T', 'VZ', 'TMUS', 'DIS', 'CMCSA', 'NFLX'],
        'ETFs': ['SPY', 'QQQ', 'IWM', 'DIA', 'XLF', 'XLE', 'XLK', 'GDX']
    }
}

def evaluate_ticker(ticker):
    """Evaluate a ticker for options income suitability"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Get basic info
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
        if current_price == 0:
            return None

        market_cap = info.get('marketCap', 0)
        volume = info.get('averageVolume', 0)
        beta = info.get('beta', 1.0)

        # Get options data
        try:
            expirations = stock.options
            if len(expirations) == 0:
                return None

            # Get near-term options (30-45 days out)
            target_date = datetime.now() + timedelta(days=35)
            closest_exp = min(expirations,
                            key=lambda x: abs((datetime.strptime(x, '%Y-%m-%d') - target_date).days))

            opts = stock.option_chain(closest_exp)
            puts = opts.puts

            # Find ATM/slightly OTM puts
            atm_puts = puts[
                (puts['strike'] >= current_price * 0.90) &
                (puts['strike'] <= current_price * 1.0)
            ]

            if atm_puts.empty:
                return None

            # Calculate metrics
            avg_volume = atm_puts['volume'].mean()
            avg_oi = atm_puts['openInterest'].mean()
            avg_iv = atm_puts['impliedVolatility'].mean()
            avg_bid = atm_puts['bid'].mean()

            # Premium potential (avg premium as % of strike)
            avg_premium_pct = (avg_bid / current_price * 100) if current_price > 0 else 0

            # Days to expiration
            dte = (datetime.strptime(closest_exp, '%Y-%m-%d') - datetime.now()).days

            # Annualized premium potential
            if dte > 0:
                annual_premium = avg_premium_pct * (365 / dte)
            else:
                annual_premium = 0

        except Exception as e:
            # print(f"  Options error for {ticker}: {e}")
            return None

        # Quality score (0-100)
        quality_score = 50

        # Market cap (larger = more stable)
        if market_cap > 100e9:  # > $100B
            quality_score += 20
        elif market_cap > 10e9:  # > $10B
            quality_score += 10

        # Options liquidity
        if avg_volume > 1000:
            quality_score += 15
        elif avg_volume > 100:
            quality_score += 10
        elif avg_volume > 10:
            quality_score += 5

        # Volatility (moderate is good for income)
        if 1.0 <= beta <= 1.5:
            quality_score += 10
        elif 0.7 <= beta <= 2.0:
            quality_score += 5

        # Premium potential
        if annual_premium > 25:
            quality_score += 15
        elif annual_premium > 15:
            quality_score += 10
        elif annual_premium > 10:
            quality_score += 5

        return {
            'ticker': ticker,
            'price': current_price,
            'market_cap_b': market_cap / 1e9,
            'avg_volume': volume,
            'beta': beta,
            'options_volume': avg_volume,
            'open_interest': avg_oi,
            'implied_vol': avg_iv * 100,
            'avg_premium_pct': avg_premium_pct,
            'annual_premium': annual_premium,
            'dte': dte,
            'quality_score': quality_score,
            'capital_per_contract': current_price * 100
        }

    except Exception as e:
        # print(f"Error evaluating {ticker}: {e}")
        return None

print("="*80)
print("OPTIONS INCOME WATCHLIST RESEARCH")
print("="*80)
print("\nEvaluating tickers for:")
print("  * Options liquidity (volume, open interest)")
print("  * Premium potential (implied volatility)")
print("  * Quality (market cap, stability)")
print("  * Capital efficiency")
print("\nThis will take 2-3 minutes...")

results = []
total_tickers = sum(len(tickers) for category in CANDIDATES.values() for tickers in category.values())
processed = 0

for category, subcategories in CANDIDATES.items():
    print(f"\n{'='*80}")
    print(f"Evaluating {category}")
    print(f"{'='*80}")

    for subcategory, tickers in subcategories.items():
        print(f"\n{subcategory}: {', '.join(tickers)}")

        for ticker in tickers:
            processed += 1
            print(f"  [{processed}/{total_tickers}] {ticker}...", end=" ")

            result = evaluate_ticker(ticker)
            if result:
                result['category'] = category
                result['subcategory'] = subcategory
                results.append(result)
                print(f"OK (Score: {result['quality_score']}, Annual: {result['annual_premium']:.1f}%)")
            else:
                print("SKIP (No options data or illiquid)")

            time.sleep(0.5)  # Rate limiting

# Create DataFrame
df = pd.DataFrame(results)

if df.empty:
    print("\nNo suitable tickers found!")
    exit()

# Sort by quality score
df = df.sort_values('quality_score', ascending=False)

print("\n" + "="*80)
print("TOP 50 TICKERS FOR OPTIONS INCOME (by Quality Score)")
print("="*80)

top_50 = df.head(50)
print(top_50[['ticker', 'category', 'price', 'quality_score', 'annual_premium',
              'options_volume', 'open_interest', 'implied_vol']].to_string(index=False))

# Summary by category
print("\n" + "="*80)
print("SUMMARY BY CATEGORY")
print("="*80)

for category in ['METALS', 'TECH', 'SP500_HIGH_LIQUIDITY']:
    cat_data = df[df['category'] == category]
    if not cat_data.empty:
        print(f"\n{category}:")
        print(f"  Total evaluated: {len(cat_data)}")
        print(f"  Avg quality score: {cat_data['quality_score'].mean():.1f}")
        print(f"  Avg annual premium: {cat_data['annual_premium'].mean():.1f}%")
        print(f"  Top 5: {', '.join(cat_data.head(5)['ticker'].tolist())}")

# Generate recommended watchlist
print("\n" + "="*80)
print("RECOMMENDED WATCHLIST (Top 30 by Quality Score)")
print("="*80)

recommended = df.head(30)

# Group by category
metals = recommended[recommended['category'] == 'METALS']['ticker'].tolist()
tech = recommended[recommended['category'] == 'TECH']['ticker'].tolist()
sp500 = recommended[recommended['category'] == 'SP500_HIGH_LIQUIDITY']['ticker'].tolist()

print(f"\nMetals ({len(metals)}): {', '.join(metals)}")
print(f"\nTech ({len(tech)}): {', '.join(tech)}")
print(f"\nS&P 500 ({len(sp500)}): {', '.join(sp500)}")

# Generate Python list for config.py
print("\n" + "="*80)
print("COPY TO config.py")
print("="*80)
print("\n# Recommended watchlist for options income")
print("WATCHLIST = [")

for ticker in recommended['ticker'].tolist():
    cat = recommended[recommended['ticker'] == ticker]['subcategory'].iloc[0]
    score = recommended[recommended['ticker'] == ticker]['quality_score'].iloc[0]
    annual = recommended[recommended['ticker'] == ticker]['annual_premium'].iloc[0]
    print(f"    '{ticker}',  # {cat} - Score: {score:.0f}, Annual: {annual:.1f}%")

print("]")

# Save full results
output_file = 'watchlist_research_results.csv'
df.to_csv(output_file, index=False)
print(f"\nFull results saved to: {output_file}")

# Category breakdown
print("\n" + "="*80)
print("TIER BREAKDOWN")
print("="*80)

tier_a = df[df['quality_score'] >= 80]
tier_b = df[(df['quality_score'] >= 65) & (df['quality_score'] < 80)]
tier_c = df[df['quality_score'] < 65]

print(f"\nTIER A (Score 80+): {len(tier_a)} tickers - EXCELLENT for income")
if not tier_a.empty:
    print(f"  {', '.join(tier_a['ticker'].tolist())}")

print(f"\nTIER B (Score 65-79): {len(tier_b)} tickers - GOOD for income")
if not tier_b.empty:
    print(f"  {', '.join(tier_b['ticker'].tolist())}")

print(f"\nTIER C (Score <65): {len(tier_c)} tickers - ACCEPTABLE but lower quality")
if not tier_c.empty:
    print(f"  {', '.join(tier_c.head(10)['ticker'].tolist())} (showing first 10)")

print("\n" + "="*80)
print()
