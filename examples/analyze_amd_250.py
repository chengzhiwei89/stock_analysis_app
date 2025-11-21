import pandas as pd
import yfinance as yf
from datetime import datetime

# Get current AMD data
amd = yf.Ticker('AMD')
info = amd.info
hist = amd.history(period='5d')

print('='*80)
print('AMD STOCK ANALYSIS')
print('='*80)
print(f'Current Price: ${info.get("currentPrice", "N/A")}')
print(f'Previous Close: ${info.get("previousClose", "N/A")}')
print(f'Regular Market Price: ${info.get("regularMarketPrice", "N/A")}')
print(f'52 Week High: ${info.get("fiftyTwoWeekHigh", "N/A")}')
print(f'52 Week Low: ${info.get("fiftyTwoWeekLow", "N/A")}')
print(f'\nRecent Price History (Last 5 Days):')
print(hist[['Close', 'Volume']].tail())

# Check implied volatility
print(f'\nVolatility Metrics:')
print(f'Beta: {info.get("beta", "N/A")}')

# Check the options data
df = pd.read_csv('data/option_chains/options_data_20251027_151152.csv')
amd_250 = df[(df['ticker']=='AMD') & (df['strike']==250.0) & (df['expiration']=='2025-11-21') & (df['option_type']=='put')]

print(f'\n' + '='*80)
print('AMD $250 PUT (Nov 21) - OPTIONS DATA FROM CSV')
print('='*80)
if not amd_250.empty:
    print(amd_250[['ticker', 'strike', 'expiration', 'current_stock_price', 'bid', 'ask', 'lastPrice', 'volume', 'openInterest', 'impliedVolatility']].to_string(index=False))

    row = amd_250.iloc[0]
    print(f'\n' + '='*80)
    print('DETAILED ANALYSIS')
    print('='*80)
    print(f'Current Stock Price: ${row["current_stock_price"]:.2f}')
    print(f'Strike Price: ${row["strike"]:.2f}')
    print(f'Distance: ${row["current_stock_price"] - row["strike"]:.2f} ({((row["current_stock_price"] - row["strike"]) / row["current_stock_price"] * 100):.2f}% OTM)')
    print(f'\nPremium: ${row["lastPrice"]:.2f}')
    print(f'Intrinsic Value: ${max(row["strike"] - row["current_stock_price"], 0):.2f}')
    print(f'Time Value: ${row["lastPrice"] - max(row["strike"] - row["current_stock_price"], 0):.2f}')
    print(f'\nImplied Volatility: {row["impliedVolatility"]*100:.1f}%')
    print(f'Volume: {row["volume"]:.0f}')
    print(f'Open Interest: {row["openInterest"]:.0f}')

    # Calculate what the premium represents
    print(f'\n' + '='*80)
    print('PREMIUM BREAKDOWN')
    print('='*80)
    print(f'Premium as % of Strike: {(row["lastPrice"] / row["strike"] * 100):.2f}%')
    print(f'Premium as % of Stock Price: {(row["lastPrice"] / row["current_stock_price"] * 100):.2f}%')

    # Check if this is actually ITM
    if row["current_stock_price"] < row["strike"]:
        print(f'\n⚠️  WARNING: This option is IN THE MONEY!')
        print(f'   Stock would need to rise ${row["strike"] - row["current_stock_price"]:.2f} to be at strike')

else:
    print('No data found for this option')

# Get fresh option chain from yfinance
print(f'\n' + '='*80)
print('FRESH DATA FROM YFINANCE (Current)')
print('='*80)
try:
    opts = amd.option_chain('2025-11-21')
    puts = opts.puts
    put_250 = puts[puts['strike'] == 250.0]
    if not put_250.empty:
        print('\nAMD $250 PUT (Nov 21) - LIVE DATA:')
        print(put_250[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']].to_string(index=False))
    else:
        print('Strike not found in live data')
except Exception as e:
    print(f'Could not fetch live data: {e}')

# Check for earnings or events
print(f'\n' + '='*80)
print('UPCOMING EVENTS')
print('='*80)
try:
    calendar = amd.calendar
    if calendar is not None and not calendar.empty:
        print('Earnings Calendar:')
        print(calendar)
    else:
        print('No calendar data available')
except:
    print('Could not fetch calendar')
