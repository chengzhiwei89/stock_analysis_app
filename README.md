# Stock Options Income Analyzer

A comprehensive Python toolkit for analyzing cash-secured put (CSP) and covered call options strategies with enhanced probability analysis.

## Features

- **Cash Secured Put Scanner**: Find optimal CSP opportunities with customizable filters
- **Enhanced Probability Analysis**: Goes beyond Black-Scholes using technical, fundamental, and sentiment data
- **Early Profit-Taking Strategy**: Optimized for 30-45 DTE with 50-75% profit targets
- **HTML Dashboard Generation**: Interactive visualizations of scan results
- **Portfolio Management**: Track and manage multiple positions with capital allocation

## Quick Start

```bash
# Run enhanced CSP scan
python run_enhanced_csp_scan.py

# Run quick scan (both covered calls and CSPs)
python quick_start.py

# Generate HTML dashboard
python run_enhanced_csp_scan.py --html
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
