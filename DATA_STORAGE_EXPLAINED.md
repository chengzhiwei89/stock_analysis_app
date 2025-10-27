# DataFrame Storage Explained

## Quick Answer

**Analysis results (CC/CSP/Wheel) are NOT automatically saved!**
They exist only in memory (RAM) when you run the analysis.

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ YOU RUN ANALYSIS                                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Fetch Options Data                                       │
│    extractor.fetch_and_store_options(['NVDA'])              │
└────────────────┬────────────────────────────────────────────┘
                 │
    ┌────────────┴─────────────┐
    │                          │
    ▼                          ▼
┌─────────────────┐    ┌──────────────────────────────┐
│ IN MEMORY       │    │ AUTO-SAVED TO DISK ✓         │
│ DataFrame       │    │ data/option_chains/          │
│ (Temporary)     │    │ options_data_20251025.csv    │
└────────┬────────┘    └──────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Run Analysis                                             │
│    results = analyzer.get_top_opportunities(options_data)   │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │ IN MEMORY     │
         │ DataFrame     │
         │ (Results)     │
         │               │
         │ NOT SAVED! ✗  │
         └───────┬───────┘
                 │
    ┌────────────┴─────────────┐
    │                          │
    ▼                          ▼
┌─────────────────┐    ┌──────────────────────────────┐
│ Lost when       │    │ MANUAL SAVE (Optional)       │
│ program ends    │    │ results.to_csv('my.csv')     │
└─────────────────┘    └──────────────────────────────┘
```

## What's Saved Automatically vs Not

| Data Type | Auto-Saved? | Location | Access Method |
|-----------|-------------|----------|---------------|
| **Raw Options Data** | ✅ YES | `data/option_chains/options_data_*.csv` | `extractor.load_latest_data()` |
| **Covered Call Results** | ❌ NO | Memory only | Run analysis function |
| **Cash Secured Put Results** | ❌ NO | Memory only | Run analysis function |
| **Wheel Strategy Results** | ❌ NO | Memory only | Run analysis function |
| **Portfolio Stocks** | ✅ YES | `data/portfolio/portfolio.json` | `portfolio.get_stocks_dataframe()` |
| **Portfolio Options** | ✅ YES | `data/portfolio/portfolio.json` | `portfolio.get_options_dataframe()` |

## How to Access Data

### Option 1: Run Fresh Analysis (Most Common)
```python
from src.data.option_extractor import OptionDataExtractor
from src.strategies.covered_call import CoveredCallAnalyzer

# Fetch and analyze
extractor = OptionDataExtractor()
options = extractor.fetch_and_store_options(['NVDA'])

analyzer = CoveredCallAnalyzer()
results = analyzer.get_top_opportunities(options, ...)

# Results is a DataFrame in memory - work with it now!
print(results.head())
results[results['annual_return'] > 30]

# Save if you want to keep it:
results.to_csv('my_results.csv')
```

### Option 2: Use Previously Fetched Data
```python
# Load from disk (faster, no API call)
options = extractor.load_latest_data()

# Analyze the loaded data
results = analyzer.get_top_opportunities(options, ...)
```

### Option 3: Load Saved Analysis Results
```python
import pandas as pd

# If you previously saved results:
results = pd.read_csv('my_cc_results.csv')
```

## Why Not Auto-Save Everything?

**Good reasons:**
1. **Speed** - No disk I/O overhead
2. **Flexibility** - You decide what to save
3. **No clutter** - Avoids hundreds of result files
4. **Fresh analysis** - Parameters change, you want new results

**Raw data IS saved because:**
- API calls are slow/rate-limited
- Data doesn't change (historical record)
- Useful for backtesting
- Can re-analyze without re-fetching

## Working with DataFrames

```python
# After running analysis, you have a DataFrame:
results = analyzer.get_top_opportunities(...)

# It's just a pandas DataFrame - do anything:
results.head()
results.describe()
results[results['ticker'] == 'NVDA']
results.sort_values('annual_return', ascending=False)
results.to_excel('results.xlsx')
results.to_csv('results.csv')

# Filter and save subsets:
nvda_only = results[results['ticker'] == 'NVDA']
nvda_only.to_csv('nvda_only.csv')

# Use in calculations:
avg_return = results['annual_return'].mean()
best_premium = results['premium_received'].max()
```

## Quick Examples

### Example 1: Analyze NVDA and Save Results
```python
# Run this
python quick_access_guide.py
```

### Example 2: Interactive Python
```python
from src.data.option_extractor import OptionDataExtractor
from src.strategies.covered_call import CoveredCallAnalyzer

extractor = OptionDataExtractor()
analyzer = CoveredCallAnalyzer()

# Get data
options = extractor.fetch_and_store_options(['NVDA'])

# Analyze
results = analyzer.get_top_opportunities(options, min_annual_return=20)

# Work with results
for idx, row in results.head(5).iterrows():
    print(f"${row['strike']}: {row['premium_received']} premium")

# Save if desired
results.to_csv('nvda_cc.csv')
```

### Example 3: Check Existing Data
```python
import glob
import pandas as pd

# See what raw data you have
files = glob.glob('data/option_chains/options_data_*.csv')
print(f"You have {len(files)} saved option data files")

# Load most recent
latest = sorted(files)[-1]
options = pd.read_csv(latest)
print(f"Loaded {len(options)} options")
```

## Files on Disk Right Now

Check these directories:

```bash
# Raw options data (auto-saved)
ls data/option_chains/

# Portfolio data (auto-saved)
ls data/portfolio/

# Your manually saved results (if any)
ls *.csv
ls *.xlsx
```

## Summary

**Remember:**
- ✅ Raw options data = AUTO-SAVED
- ✅ Portfolio = AUTO-SAVED
- ❌ Analysis results = IN MEMORY (save manually if needed)

**Best Practice:**
1. Run analysis when you need it (fast)
2. Work with DataFrame in memory (explore, filter, sort)
3. Save important results manually (`to_csv`, `to_excel`)
4. Use `load_latest_data()` to avoid re-fetching options

**For your NVDA position:**
```bash
# Quick analysis for your 120 shares:
python my_portfolio_setup.py

# Or interactive:
python quick_access_guide.py
```
