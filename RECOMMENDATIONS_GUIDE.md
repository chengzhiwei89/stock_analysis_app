# Recommendations Storage Guide

## Overview

All analysis recommendations (Covered Calls, Cash Secured Puts, Wheel Strategy) are now **automatically saved** to `data/recommendations/` for easy access and historical tracking.

## Features

✅ **Auto-save enabled by default** - All analysis results are saved automatically
✅ **CSV + JSON metadata** - Easy to open in Excel or analyze programmatically
✅ **Combined Excel files** - All strategies in one workbook
✅ **Searchable by ticker** - Find all recommendations for specific stocks
✅ **Timestamped** - Track when analysis was run
✅ **Auto-cleanup** - Remove old files after configurable days

## Directory Structure

```
data/
└── recommendations/
    ├── cc_NVDA_20251025_223456.csv           # Covered Call recommendations
    ├── cc_NVDA_20251025_223456_meta.json     # Metadata (criteria, tickers, etc.)
    ├── csp_10tickers_20251025_223500.csv     # Cash Secured Put recommendations
    ├── csp_10tickers_20251025_223500_meta.json
    ├── wheel_10tickers_20251025_223505.csv   # Wheel Strategy recommendations
    ├── wheel_10tickers_20251025_223505_meta.json
    └── all_strategies_multi_20251025_223510.xlsx  # Combined Excel file
```

## Configuration

### Enable/Disable Auto-save

Edit `config.py`:

```python
RECOMMENDATIONS_SETTINGS = {
    'auto_save': True,                      # Set to False to disable
    'save_directory': 'data/recommendations',
    'save_excel': True,                     # Also create Excel files
    'keep_days': 30,                        # Auto-cleanup after 30 days (0 = never)
}
```

## File Formats

### CSV Files
- One row per opportunity
- All columns from analysis (strike, premium, returns, Greeks, etc.)
- Can be opened directly in Excel

### Metadata JSON Files
```json
{
  "timestamp": "20251025_223456",
  "strategy": "covered_call",
  "tickers": ["NVDA", "AAPL", "MSFT"],
  "num_opportunities": 45,
  "criteria": {
    "min_premium": 1.0,
    "min_annual_return": 20.0,
    "max_days": 45
  },
  "notes": "Quick scan of 10 tickers"
}
```

### Excel Files (Combined)
- Multiple sheets: "Covered_Calls", "Cash_Secured_Puts", "Wheel_Strategy"
- All formatting preserved
- Easy to share or email

## Viewing Recommendations

### Method 1: Command Line Tool

```bash
# List all saved recommendations
python view_recommendations.py list

# View latest covered calls
python view_recommendations.py view --strategy cc

# View latest cash secured puts
python view_recommendations.py view --strategy csp

# View latest wheel strategy
python view_recommendations.py view --strategy wheel

# Search for specific ticker
python view_recommendations.py search --ticker NVDA

# Export to Excel
python view_recommendations.py export --strategy cc --output my_cc.xlsx

# Cleanup old files (older than 30 days)
python view_recommendations.py cleanup --days 30
```

### Method 2: Python Code

```python
from src.data.recommendations_manager import RecommendationsManager

# Initialize
rec_manager = RecommendationsManager()

# List all recommendations
recommendations = rec_manager.list_recommendations()

# Load latest covered calls
cc_results = rec_manager.load_latest_recommendation('cc')

# Load latest CSPs for specific ticker
nvda_puts = rec_manager.load_latest_recommendation('csp', ticker='NVDA')

# Get summary
print(rec_manager.get_summary())
```

### Method 3: Direct File Access

```python
import pandas as pd

# Open the CSV directly
results = pd.read_csv('data/recommendations/cc_NVDA_20251025_223456.csv')

# Or open Excel with all sheets
excel_data = pd.read_excel('data/recommendations/all_strategies_multi_20251025.xlsx',
                           sheet_name=None)  # Load all sheets
```

## Automatic Saving

### When Running Quick Start

```bash
python quick_start.py
```

Automatically saves:
- ✓ Covered call recommendations
- ✓ Cash secured put recommendations
- ✓ Wheel strategy recommendations
- ✓ Combined Excel file

### When Analyzing Your Portfolio

```bash
python my_portfolio_setup.py
```

Automatically saves:
- ✓ NVDA covered call opportunities for your 120 shares

### Custom Analysis

```python
from src.data.option_extractor import OptionDataExtractor
from src.strategies.covered_call import CoveredCallAnalyzer
from src.data.recommendations_manager import RecommendationsManager

# Run analysis
extractor = OptionDataExtractor()
analyzer = CoveredCallAnalyzer()
options = extractor.fetch_and_store_options(['NVDA'])
results = analyzer.get_top_opportunities(options, min_annual_return=20)

# Save recommendations
rec_manager = RecommendationsManager()
rec_manager.save_covered_call_recommendations(
    results,
    tickers=['NVDA'],
    criteria={'min_annual_return': 20},
    notes='Custom NVDA analysis'
)
```

## File Naming Convention

### Format
```
{strategy}_{tickers}_{YYYYMMDD}_{HHMMSS}.{ext}
```

### Examples
- `cc_NVDA_20251025_143022.csv` - Single ticker
- `csp_AAPL_MSFT_GOOGL_20251025_143025.csv` - Multiple tickers (3 or fewer)
- `wheel_10tickers_20251025_143030.csv` - More than 3 tickers
- `all_strategies_multi_20251025_143035.xlsx` - Combined file

## What Gets Saved

### Covered Calls
All columns including:
- ticker, strike, expiration, days_to_expiration
- premium_received, bid, ask
- annual_return, monthly_return
- downside_protection, max_profit_pct
- delta, gamma, theta, impliedVolatility
- prob_otm, distance_pct, moneyness_class
- volume, openInterest

### Cash Secured Puts
All columns including:
- ticker, strike, expiration, days_to_expiration
- premium_received, bid, ask
- annual_return, monthly_return
- net_purchase_price, discount_from_current
- cushion, capital_required
- **max_affordable_contracts** (if cash filtering enabled)
- **total_capital_required** (if cash filtering enabled)
- **total_premium_received** (if cash filtering enabled)
- delta, impliedVolatility, prob_otm
- volume, openInterest

### Wheel Strategy
All CSP columns plus:
- wheel_score (composite metric)

## Managing Saved Files

### List Files
```bash
# Windows
dir data\recommendations

# Mac/Linux
ls -lh data/recommendations/
```

### Cleanup Old Files

```bash
# Remove files older than 30 days
python view_recommendations.py cleanup --days 30

# Remove files older than 7 days
python view_recommendations.py cleanup --days 7
```

Or programmatically:
```python
rec_manager = RecommendationsManager()
rec_manager.cleanup_old_recommendations(keep_days=30)
```

### Manual Cleanup
Just delete files from `data/recommendations/` - they're independent CSVs.

## Use Cases

### 1. Track Performance Over Time
```python
import glob
import pandas as pd

# Load all NVDA covered calls over time
files = glob.glob('data/recommendations/cc_NVDA_*.csv')

for f in sorted(files):
    df = pd.read_csv(f)
    print(f"{f}: {len(df)} opportunities, avg return: {df['annual_return'].mean():.1f}%")
```

### 2. Compare Different Days
```python
# Load today's recommendations
today = rec_manager.load_latest_recommendation('cc')

# Load older file
yesterday = pd.read_csv('data/recommendations/cc_NVDA_20251024_120000.csv')

# Compare
print(f"Today: {today['annual_return'].mean():.1f}% avg return")
print(f"Yesterday: {yesterday['annual_return'].mean():.1f}% avg return")
```

### 3. Export for External Analysis
```bash
# Export latest CC opportunities to Excel
python view_recommendations.py export --strategy cc --output my_analysis.xlsx

# Open in Excel, Google Sheets, or other tools
```

### 4. Build Trading Log
Keep all recommendations and track which trades you executed:
```python
# Load recommendations
cc_opps = pd.read_csv('data/recommendations/cc_NVDA_20251025_120000.csv')

# Mark which one you traded
cc_opps['traded'] = False
cc_opps.loc[5, 'traded'] = True  # Mark trade #5 as executed

# Save your trading log
cc_opps.to_csv('my_trading_log.csv', index=False)
```

## Integration with Other Tools

### Import into Excel
1. Open Excel
2. File → Open → Browse to `data/recommendations/`
3. Select CSV or XLSX file
4. Use filters, pivot tables, charts, etc.

### Import into Google Sheets
1. Open Google Sheets
2. File → Import → Upload
3. Select CSV from `data/recommendations/`

### Import into Trading Journal
Most trading journal software accepts CSV imports:
1. Export recommendations: `python view_recommendations.py export ...`
2. Import CSV into your trading journal
3. Track actual vs planned trades

## Tips

1. **Keep auto-save enabled** - You'll thank yourself later when comparing historical opportunities

2. **Use the metadata** - JSON metadata files contain the exact criteria used, helpful for reproducing results

3. **Search by ticker** - `python view_recommendations.py search --ticker NVDA` shows all saved recommendations for NVDA

4. **Regular cleanup** - Set `keep_days` in config to automatically remove old files

5. **Version control** - Add `data/recommendations/` to `.gitignore` (already done) - these are data files, not code

6. **Backup important files** - Copy special analyses to another location if you want to keep them long-term

## Troubleshooting

### No files in data/recommendations/
- Check `config.py` - ensure `RECOMMENDATIONS_SETTINGS['auto_save'] = True`
- Run `python quick_start.py` to generate recommendations

### Files not loading
- Check file path - use `python view_recommendations.py list` to see available files
- Verify CSV format - open in text editor to check

### Too many files
- Run cleanup: `python view_recommendations.py cleanup --days 7`
- Or manually delete old files from `data/recommendations/`

## Summary

**Recommendations are now automatically saved!**

- ✅ Run any analysis → recommendations saved automatically
- ✅ View with `python view_recommendations.py`
- ✅ Access programmatically with `RecommendationsManager`
- ✅ Open CSV files directly in Excel
- ✅ Historical tracking for performance analysis

**Your NVDA analysis recommendations will be saved whenever you run `my_portfolio_setup.py`!**
