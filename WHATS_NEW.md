# What's New - Recommendations Auto-Save Feature

## 🎉 Major Update: All Recommendations Now Auto-Saved!

### What Changed

**Before:** Analysis results existed only in memory - lost when program closed

**Now:** All analysis recommendations are **automatically saved** to `data/recommendations/`

---

## ✨ Key Features

### 1. Automatic Saving
- ✅ All Covered Call opportunities → saved
- ✅ All Cash Secured Put opportunities → saved
- ✅ All Wheel Strategy candidates → saved
- ✅ Happens automatically - no extra steps needed

### 2. Multiple Formats
- **CSV files** - Open directly in Excel
- **JSON metadata** - Contains analysis criteria
- **Combined Excel** - All strategies in one workbook

### 3. Easy Access
```bash
# View your saved recommendations
python view_recommendations.py

# Search for NVDA recommendations
python view_recommendations.py search --ticker NVDA

# Export to Excel
python view_recommendations.py export --strategy cc
```

### 4. Your NVDA Position
When you run `python my_portfolio_setup.py`:
- ✓ Analyzes covered calls for your 120 NVDA shares
- ✓ **Automatically saves all opportunities** to `data/recommendations/cc_NVDA_{timestamp}.csv`
- ✓ Open in Excel to review and track

---

## 📁 Where Recommendations Are Stored

```
data/
└── recommendations/
    ├── cc_NVDA_20251025_143022.csv              # Your NVDA covered calls
    ├── cc_NVDA_20251025_143022_meta.json        # Metadata
    ├── csp_10tickers_20251025_143025.csv        # Cash secured puts
    ├── wheel_10tickers_20251025_143030.csv      # Wheel strategy
    └── all_strategies_multi_20251025.xlsx       # Combined Excel
```

---

## 🚀 How to Use

### Run Analysis (Auto-Saves)
```bash
# Run quick scan - saves CC, CSP, and Wheel recommendations
python quick_start.py

# Analyze your NVDA position - saves covered call opportunities
python my_portfolio_setup.py
```

### View Saved Recommendations
```bash
# List everything saved
python view_recommendations.py

# View latest covered calls
python view_recommendations.py view --strategy cc

# Search for your NVDA recommendations
python view_recommendations.py search --ticker NVDA
```

### Access in Python
```python
from src.data.recommendations_manager import RecommendationsManager

rec_manager = RecommendationsManager()

# Load latest covered calls
cc_results = rec_manager.load_latest_recommendation('cc')

# Load NVDA-specific recommendations
nvda_cc = rec_manager.load_latest_recommendation('cc', ticker='NVDA')

# View summary
print(rec_manager.get_summary())
```

---

## ⚙️ Configuration

Edit `config.py`:

```python
RECOMMENDATIONS_SETTINGS = {
    'auto_save': True,              # Enable/disable (True by default)
    'save_directory': 'data/recommendations',
    'save_excel': True,             # Also save Excel files
    'keep_days': 30,                # Auto-cleanup after 30 days
}
```

---

## 💡 Use Cases

### 1. Track Your NVDA Covered Calls
```bash
# Run analysis for your 120 shares
python my_portfolio_setup.py

# Open the saved CSV in Excel
# File: data/recommendations/cc_NVDA_{timestamp}.csv

# Review opportunities, pick the best one
# Track which trade you executed
```

### 2. Compare Opportunities Over Time
```python
import pandas as pd
import glob

# Load all NVDA analyses
files = sorted(glob.glob('data/recommendations/cc_NVDA_*.csv'))

for f in files[-5:]:  # Last 5 analyses
    df = pd.read_csv(f)
    avg_return = df['annual_return'].mean()
    print(f"{f}: {len(df)} opps, {avg_return:.1f}% avg return")
```

### 3. Build Your Trading Log
```python
# Load today's recommendations
today = pd.read_csv('data/recommendations/cc_NVDA_20251025_120000.csv')

# Mark which trade you executed
today['executed'] = False
today.loc[3, 'executed'] = True  # I executed opportunity #3

# Save your trading log
today.to_csv('my_trading_log.csv', index=False)
```

---

## 📚 Documentation

- **Quick Start:** `RECOMMENDATIONS_SUMMARY.txt`
- **Complete Guide:** `RECOMMENDATIONS_GUIDE.md`
- **Main README:** Updated with recommendations section

---

## 🎯 Benefits

### For Your NVDA Position
- ✓ Never lose analysis results for your 120 shares
- ✓ Compare different covered call strategies over time
- ✓ Track which opportunities you executed
- ✓ Build a trading journal

### General Benefits
- ✓ **Historical tracking** - See how opportunities change
- ✓ **No data loss** - All results permanently saved
- ✓ **Easy sharing** - Send CSV/Excel to others
- ✓ **Performance analysis** - Track what worked
- ✓ **Trading journal** - Document your trades

---

## 🔧 Command Reference

```bash
# View all saved recommendations
python view_recommendations.py list

# View latest covered calls
python view_recommendations.py view --strategy cc

# View latest cash secured puts
python view_recommendations.py view --strategy csp

# View latest wheel strategy
python view_recommendations.py view --strategy wheel

# Search for NVDA recommendations
python view_recommendations.py search --ticker NVDA

# Export covered calls to Excel
python view_recommendations.py export --strategy cc --output my_cc.xlsx

# Export all strategies to Excel
python view_recommendations.py export --output all_strategies.xlsx

# Cleanup old files (older than 30 days)
python view_recommendations.py cleanup --days 30
```

---

## ✅ Summary

**Everything is now automatically saved!**

When you run:
- `python quick_start.py` → Saves all CC/CSP/Wheel recommendations
- `python my_portfolio_setup.py` → Saves NVDA covered call analysis

Access saved recommendations:
- Command line: `python view_recommendations.py`
- Python: `RecommendationsManager().load_latest_recommendation('cc')`
- Excel: Open files from `data/recommendations/`

**Your NVDA covered call analysis (120 shares @ $100) is now saved every time you run it!**

---

## 🚦 Next Steps

1. ✅ **Run your NVDA analysis:**
   ```bash
   python my_portfolio_setup.py
   ```

2. ✅ **View saved recommendations:**
   ```bash
   python view_recommendations.py
   ```

3. ✅ **Open in Excel:**
   ```bash
   # Navigate to data/recommendations/
   # Open cc_NVDA_{timestamp}.csv
   ```

4. ✅ **Start building your trading log!**

---

Enjoy never losing your analysis results again! 🎉
