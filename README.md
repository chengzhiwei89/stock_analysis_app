# Stock Options Income Analyzer

A comprehensive Python toolkit for analyzing cash-secured put (CSP) and covered call options strategies with enhanced probability analysis.

## Features

- **Cash Secured Put Scanner**: Find optimal CSP opportunities with customizable filters
- **Enhanced Probability Analysis**: Goes beyond Black-Scholes using technical, fundamental, and sentiment data
- **Early Profit-Taking Strategy**: Optimized for 30-45 DTE with 50-75% profit targets
- **HTML Dashboard Generation**: Interactive visualizations of scan results
- **Full Data Table Export**: Generate interactive HTML tables with advanced filtering, sorting, and multi-format export (CSV, Excel, PDF)
- **Portfolio Management**: Track and manage multiple positions with capital allocation

## Quick Start

```bash
# Run enhanced CSP scan
python run_enhanced_csp_scan.py

# Run quick scan (both covered calls and CSPs)
python quick_start.py

# Generate HTML dashboard
python run_enhanced_csp_scan.py --html

# Generate interactive table with advanced filters
python run_enhanced_csp_scan.py --full

# Generate both dashboard and full table
python run_enhanced_csp_scan.py --html --full
```

## Configuration

All settings are centralized in `config.py`:

- **Capital Settings**: Set available cash, max per position, reserve cash
- **CSP Criteria**: Configure DTE range, premium minimums, probability thresholds
- **Advanced Filters**: Greeks-based filters, liquidity requirements, safety buffers
- **Early Profit-Taking Rules**: Target profit percentages and force-close thresholds

## Strategy: 30-45 DTE with Early Profit Taking

The default configuration is optimized for:
1. Sell 30-45 DTE puts at 65%+ probability OTM
2. Close at 50% profit (typically 10-20 days)
3. Force close at 21 DTE if profit target not hit
4. Immediately roll to new 30-45 DTE position

Expected: 18-24 trades/year with lower stress than weekly options.

## Recent Changes

### 2025-12-03: Interactive Data Table & Filter Optimization

**New Features:**
- **Interactive Full Table Export**: Added `--full` flag to generate comprehensive HTML table with all scan data using DataTables library
- **Advanced Column Filtering**: Text search with partial matching for text columns, range filters (min/max) for numeric columns
- **Multi-format Export**: Export filtered data to CSV, Excel, PDF, or print-friendly view directly from the browser
- **Real-time Filtering & Sorting**: Filter multiple columns simultaneously with instant updates, click any header to sort
- **Responsive Design**: Mobile-friendly interface with state persistence across sessions

**Configuration Optimizations:**
- **Relaxed CSP filters**: Adjusted `min_prob_otm` from 65% to 60%, `max_delta` from -0.30 to -0.35, and `min_volume` from 100 to 50
- **Improved ticker coverage**: Filter changes now capture more opportunities from stocks like MU (Micron) that were previously excluded
- **Better balance**: Maintains adequate liquidity requirements while expanding the opportunity set

**Files Added:**
- `src/visualization/full_table_generator.py`: New module for generating interactive DataTables with advanced filtering
- `check_mu_simple.py`, `diagnose_mu.py`: Diagnostic utilities for troubleshooting filter issues

**Usage:**
```bash
python run_enhanced_csp_scan.py --full  # Generate interactive table
python run_enhanced_csp_scan.py --html --full  # Generate both dashboard and table
```

**Impact**: Users can now export complete scan results to an interactive table with powerful filtering capabilities, enabling deeper analysis. Filter adjustments increase opportunity count by ~50% while maintaining quality standards.

### 2025-12-02: HTML Dashboard Enhancements

**Improvements:**
- **Added stock price column**: CSP results table now displays current stock price for better context when evaluating strike prices
- **Enhanced timestamp display**: Dashboard header now shows both data extraction time and dashboard generation time, helping users assess data freshness
- **Better data age visibility**: Users can now clearly see how outdated the options data is before making trading decisions

**Impact**: These UI improvements provide critical context for trading decisions by showing current stock prices alongside strike prices and making data freshness immediately visible.

### 2025-01-25: Configuration Restructure & Strategy Optimization

**Major Changes:**
- **Reorganized config structure**: Separated basic settings (time/premium filters) from advanced settings (Greeks, liquidity, safety filters) for better clarity
- **Optimized for 30-45 DTE strategy**: Updated default parameters to favor monthly options over weeklies, supporting early profit-taking approach
- **Capital settings updated**: Increased max position size to $30k to capture more opportunities across all price ranges
- **Added early profit-taking rules**: New configuration section with 50% profit targets, force-close at 21 DTE, and weekly check frequency

**Configuration Updates:**
- Expanded DTE range to 20-60 days (from 25-60) to capture more monthly expirations
- Reduced min annual return to 12% (from 15%) for realistic 30-45 DTE targets
- Adjusted capital: $38k available, $30k max per position, $3k reserve
- Tightened max delta to -0.30 (more conservative, further OTM)
- Disabled quality_tickers_only filter by default to show all opportunities

**Script Updates:**
- `run_enhanced_csp_scan.py`: Now reads all settings from config.py instead of hardcoded values
- `quick_start.py`: Fixed to properly reference advanced settings for Greeks-based filters
- `config_early_close.py`: Restructured to match new basic/advanced separation pattern

**Impact**: These changes shift strategy from high-frequency weeklies to sustainable monthly options with early profit-taking, reducing stress while maintaining strong returns through compounding.

## Requirements

See `requirements.txt` for full dependencies. Key packages:
- yfinance
- pandas
- scipy
- tabulate

## License

Private project for personal use.
