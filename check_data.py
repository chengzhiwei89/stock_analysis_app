import pandas as pd

df = pd.read_csv('data/option_chains/options_data_20251027_145208.csv')
puts = df[df['option_type']=='put']

print(f'Total puts: {len(puts)}')
print(f'Puts with bid > 0: {(puts["bid"] > 0).sum()}')
print(f'Puts with lastPrice > 0: {(puts["lastPrice"] > 0).sum()}')
print(f'\nUsing lastPrice instead:')

good_puts = puts[puts['lastPrice'] > 0.5]
print(f'Puts with lastPrice > 0.5: {len(good_puts)}')

if len(good_puts) > 0:
    print('\nSample options with lastPrice > 0.5:')
    print(good_puts[['ticker', 'strike', 'expiration', 'lastPrice', 'volume', 'current_stock_price']].head(20))
