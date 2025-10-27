# Cash Filtering for Cash Secured Puts - Quick Guide

## Overview

The app now includes **cash filtering** functionality that allows you to filter cash secured put opportunities based on your available capital. This ensures you only see opportunities you can actually afford to execute.

## Key Features

### 1. Capital Configuration
Set your available cash and position limits in `config.py`:

```python
CAPITAL_SETTINGS = {
    'available_cash': 50000.0,         # Your total cash available
    'max_cash_per_position': 10000.0,  # Maximum cash per single trade
    'reserve_cash': 5000.0,            # Keep this much uninvested
    'max_positions': 5,                # Max simultaneous positions
    'auto_calculate_contracts': True,  # Auto-calculate max contracts
}
```

### 2. Enable Cash Filtering
Turn on cash filtering in `config.py`:

```python
CASH_SECURED_PUT_SETTINGS = {
    'use_available_cash': True,    # Set to True to enable
    # ... other settings
}
```

### 3. New Output Columns
When cash filtering is enabled, results include:

- **`max_affordable_contracts`**: Number of contracts you can sell
- **`total_capital_required`**: Total cash needed for max contracts
- **`total_premium_received`**: Total premium income from max contracts

## Quick Start

### 1. Configure Your Cash
Edit `config.py` and set your capital amounts:
```python
CAPITAL_SETTINGS = {
    'available_cash': 50000.0,        # Your actual cash
    'max_cash_per_position': 10000.0, # Your position limit
    'reserve_cash': 5000.0,           # Keep some cash available
}
```

### 2. Enable Filtering
In `config.py`, set:
```python
CASH_SECURED_PUT_SETTINGS = {
    'use_available_cash': True,  # Enable it!
    # ...
}
```

### 3. Run Analysis
```bash
python quick_start.py
```

The CSP scan will now show:
- Available Cash: $45,000 (your $50k - $5k reserve)
- Max per position: $10,000
- Only opportunities you can afford
- How many contracts you can sell for each
- Total capital and premium for each trade

## Example Output

### Without Cash Filtering
```
Ticker  Strike  Premium  Annual Return
AAPL    150     2.50     22.5%
MSFT    350     5.00     18.2%
TSLA    200     4.50     28.1%
```
Shows all opportunities, even if you can't afford them.

### With Cash Filtering (Available Cash: $45,000, Max per position: $10,000)
```
Ticker  Strike  Premium  Contracts  Total Capital  Total Premium
AAPL    150     2.50     1          $15,000       $250
SPY     450     3.00     2          $90,000       $600          (filtered - too expensive!)
QQQ     380     2.80     2          $76,000       $560          (filtered - too expensive!)
```
Only shows AAPL because:
- AAPL: 1 contract = $15,000 (affordable, but limited by max per position)
- SPY: Would need $90k for 2 contracts (exceeds available cash)
- QQQ: Would need $76k for 2 contracts (exceeds available cash)

## How It Works

### Capital Calculation
```
Deployable Cash = available_cash - reserve_cash
                = $50,000 - $5,000
                = $45,000

Cash per Contract = strike_price × 100
                  = $450 × 100
                  = $45,000 per contract

Max Contracts = min(
    max_cash_per_position / cash_per_contract,
    deployable_cash / cash_per_contract
)
```

### Filtering Logic
1. Calculate cash required per contract (strike × 100)
2. Determine max contracts you can afford based on:
   - Your `max_cash_per_position` limit
   - Your total `deployable_cash`
3. Filter out opportunities where max_contracts < 1
4. Show remaining opportunities with contract counts

## Use Cases

### Conservative Trading
```python
CAPITAL_SETTINGS = {
    'available_cash': 100000.0,
    'max_cash_per_position': 5000.0,   # Small positions
    'reserve_cash': 20000.0,           # Large reserve
}
```
- Focus on lower-priced stocks
- Keep 20% uninvested
- Limit risk per trade

### Aggressive Trading
```python
CAPITAL_SETTINGS = {
    'available_cash': 100000.0,
    'max_cash_per_position': 25000.0,  # Larger positions
    'reserve_cash': 5000.0,            # Minimal reserve
}
```
- Can trade higher-priced stocks
- Deploy more capital
- Fewer but larger positions

## Helper Functions

### Check Deployable Cash
```python
import config
deployable = config.get_deployable_cash()
print(f"You can deploy: ${deployable:,.0f}")
```

### Calculate Max Contracts
```python
import config
strike = 450.00  # Example strike price
max_contracts = config.calculate_max_contracts(strike)
print(f"You can sell {max_contracts} contracts at ${strike}")
```

## Examples

### Run the Demonstration
```bash
python example_cash_filtering.py
```

This script demonstrates:
1. Analysis without cash filtering (all opportunities)
2. Analysis with cash filtering (only affordable ones)
3. Comparison at different cash levels ($10k, $25k, $50k, $100k)
4. How to configure the feature for your account

### Use in Your Code
```python
from src.data.option_extractor import OptionDataExtractor
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
import config

# Get options data
extractor = OptionDataExtractor()
analyzer = CashSecuredPutAnalyzer()
options_data = extractor.fetch_and_store_options(['AAPL', 'MSFT'])

# Analyze with cash filtering
deployable = config.get_deployable_cash()
max_per_pos = config.CAPITAL_SETTINGS['max_cash_per_position']

results = analyzer.get_top_opportunities(
    options_data,
    min_premium=0.5,
    min_annual_return=15.0,
    max_days=45,
    available_cash=deployable,
    max_cash_per_position=max_per_pos
)

# Results now show only affordable opportunities
for idx, row in results.iterrows():
    print(f"{row['ticker']} ${row['strike']}: "
          f"{row['max_affordable_contracts']} contracts, "
          f"${row['total_capital_required']:,.0f} capital")
```

## Important Notes

1. **Capital Required = Strike × 100 per contract**
   - $100 strike = $10,000 per contract
   - $500 strike = $50,000 per contract

2. **Reserve Cash is NOT Deployed**
   - Set aside for emergencies
   - Opportunities filter against (available - reserve)

3. **Position Limits Help Diversify**
   - Prevents over-concentration
   - Forces spreading across multiple trades

4. **Disable by Setting `use_available_cash = False`**
   - Shows all opportunities regardless of affordability
   - Useful for research and comparing tickers

## Troubleshooting

### "No affordable opportunities found"
- Your available cash may be too low
- Try lowering `max_cash_per_position`
- Reduce `reserve_cash` (carefully!)
- Look at lower-priced tickers

### "max_affordable_contracts always 1"
- Your `max_cash_per_position` is limiting you
- Increase it if you want larger positions
- Or stick with 1 contract per position for safety

### Columns not showing
- Make sure `use_available_cash = True` in config
- Check that you're passing `available_cash` parameter
- Verify the analyzer is getting the cash parameters

## Additional Resources

- **Full documentation**: See README.md
- **Code examples**: See example_cash_filtering.py
- **Configuration**: Edit config.py
- **Quick analysis**: Run quick_start.py

## Summary

Cash filtering helps you:
1. ✓ Only see opportunities you can afford
2. ✓ Know exactly how many contracts to sell
3. ✓ Calculate total capital deployment
4. ✓ Manage position sizing
5. ✓ Keep a cash reserve
6. ✓ Trade within your means

Configure it once in `config.py` and never waste time analyzing opportunities you can't afford!
