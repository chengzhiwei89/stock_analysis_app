import pandas as pd
from datetime import datetime

# Load the last scan data
df = pd.read_csv('data/option_chains/options_data_20251027_151152.csv')

# Current prices
stocks = {
    'AMD': 252.92,
    'NVDA': 186.26,
    'AAPL': 262.82,
    'MSFT': 523.61,
    'TSLA': 433.72
}

print('='*80)
print('WHEEL STRATEGY CANDIDATES - Based on Last Scan')
print('='*80)
print('\nCriteria for Wheel:')
print('  1. Strike below current price (5-10% discount)')
print('  2. High premiums for good income')
print('  3. Willing to own the stock at that price')
print('  4. 20-45 day expiration (monthly cycle)')
print('\nWARNING: Market is closed - lastPrice may be stale!')
print('         Verify prices when market opens!\n')

all_candidates = []

for ticker, current_price in stocks.items():
    puts = df[(df['ticker']==ticker) & (df['option_type']=='put')].copy()

    if puts.empty:
        continue

    # Calculate days to expiration
    puts['days'] = (pd.to_datetime(puts['expiration']) - datetime.now()).dt.days

    # Filter for wheel candidates
    # Strike 5-12% below current (good discount)
    # 20-45 days (monthly wheel cycle)
    # Premium > 1% of strike (good income)
    min_strike = current_price * 0.88
    max_strike = current_price * 0.95

    wheel = puts[
        (puts['strike'] >= min_strike) &
        (puts['strike'] <= max_strike) &
        (puts['days'] >= 20) &
        (puts['days'] <= 45) &
        (puts['lastPrice'] > 0.5)
    ].copy()

    if not wheel.empty:
        # Calculate wheel metrics
        wheel['discount_pct'] = ((current_price - wheel['strike']) / current_price * 100)
        wheel['net_entry'] = wheel['strike'] - wheel['lastPrice']
        wheel['total_discount_pct'] = ((current_price - wheel['net_entry']) / current_price * 100)
        wheel['annual_return'] = (wheel['lastPrice'] / wheel['strike']) * (365 / wheel['days']) * 100
        wheel['current_price'] = current_price

        wheel = wheel.sort_values('annual_return', ascending=False)

        print(f'\n{"="*80}')
        print(f'{ticker} - Current Price: ${current_price:.2f}')
        print(f'{"="*80}')

        for idx, row in wheel.head(3).iterrows():
            print(f'\n  Strike: ${row["strike"]:.0f} ({row["discount_pct"]:.1f}% below current)')
            print(f'  Expiration: {row["expiration"]} ({row["days"]:.0f} days)')
            print(f'  Premium: ${row["lastPrice"]:.2f} x 100 = ${row["lastPrice"]*100:.0f}')
            print(f'  Net Entry if Assigned: ${row["net_entry"]:.2f} ({row["total_discount_pct"]:.1f}% total discount)')
            print(f'  Annual Return (PUT phase): {row["annual_return"]:.1f}%')
            print(f'  Volume: {row["volume"]:.0f}')

            # Warning about stale data
            if row['bid'] == 0:
                print(f'  ** WARNING: Using lastPrice (market closed) - verify at open!')

        # Add top candidate to summary
        if len(wheel) > 0:
            top = wheel.iloc[0]
            all_candidates.append({
                'ticker': ticker,
                'current_price': current_price,
                'strike': top['strike'],
                'expiration': top['expiration'],
                'days': top['days'],
                'premium': top['lastPrice'],
                'discount_pct': top['discount_pct'],
                'total_discount_pct': top['total_discount_pct'],
                'annual_return': top['annual_return'],
                'volume': top['volume']
            })

# Summary table
if all_candidates:
    print('\n' + '='*80)
    print('TOP WHEEL OPPORTUNITIES - SUMMARY')
    print('='*80)
    print()

    summary_df = pd.DataFrame(all_candidates)
    summary_df = summary_df.sort_values('annual_return', ascending=False)

    for i, row in summary_df.iterrows():
        print(f"{row['ticker']:6} ${row['strike']:.0f} PUT ({row['expiration']}) - "
              f"${row['premium']:.2f} premium - "
              f"{row['annual_return']:.1f}% annual - "
              f"{row['total_discount_pct']:.1f}% entry discount")

print('\n' + '='*80)
print('WHEEL STRATEGY WORKFLOW')
print('='*80)
print('\n1. PHASE 1 - SELL PUT:')
print('   * Sell one of the puts above')
print('   * Collect premium immediately')
print('   * If NOT assigned: Keep premium, sell another put next month')
print('   * If ASSIGNED: Move to Phase 2')
print()
print('2. PHASE 2 - OWN STOCK:')
print('   * You now own 100 shares at strike price')
print('   * Your cost basis = Strike - Premium received')
print('   * Example: $240 strike - $11.97 premium = $228.03 effective cost')
print()
print('3. PHASE 3 - SELL COVERED CALL:')
print('   * Sell CALL at strike above your cost basis')
print('   * Collect more premium')
print('   * If NOT called away: Keep premium, sell another call')
print('   * If CALLED AWAY: Stock sold at profit, back to Phase 1!')
print()
print('4. Repeat monthly for consistent income!')

print('\n' + '='*80)
print()
