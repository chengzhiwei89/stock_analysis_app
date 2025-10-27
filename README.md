# Stock Options Analysis App

A comprehensive Python application for analyzing stock options opportunities with **Enhanced Probability Analysis**. Designed for **Covered Call**, **Cash Secured Put**, and **Wheel** strategies. Features technical/fundamental analysis integration, intelligent market-closed handling, and automated watchlist research.

## 🚀 Key Features

### ✨ Enhanced Probability Analysis (NEW!)
- **Goes Beyond Black-Scholes**: Incorporates technical indicators, fundamental metrics, and analyst sentiment
- **Technical Score**: Trend analysis, moving averages, 52-week range, volume patterns
- **Fundamental Score**: Valuation (PE ratios), profitability (margins, ROE), growth, debt ratios
- **Sentiment Score**: Analyst ratings, price targets, recommendation consensus
- **Event Risk Score**: Earnings calendar, dividend dates
- **Composite Score**: Weighted combination adjusts BS probability ±15%
- **Confidence Levels**: High/Medium/Low based on data availability

### 💰 Options Strategies

#### Cash Secured Puts (CSP)
- Identify attractive entry points at a discount
- Calculate effective purchase price after premium
- **Smart pricing**: Automatic bid/lastPrice/ask fallback (market closed handling)
- **Market status detection**: Clear warnings when using stale prices
- **Wheel strategy candidates**: Find optimal stocks for wheel rotation
- Filter by premium, return, probability, and volume
- Capital management with position sizing

#### Covered Calls
- Find optimal strike prices and expirations
- Calculate annualized and monthly returns
- Analyze downside protection and max profit
- Risk/reward scoring
- Filter by premium, return, days, and delta

#### Wheel Strategy
- **Automated candidate finder**: Identifies stocks 5-10% below current price
- **Entry discount calculator**: Shows net entry price after premium
- **Phase tracking**: PUT → Assignment → CALL → Repeat
- **Quality scoring**: Ranks opportunities by return + discount + fundamentals

### 📊 Market Intelligence

#### Watchlist Research Tool (NEW!)
- **Automated evaluation**: Scans 100+ tickers across Metals, Tech, S&P 500
- **Liquidity scoring**: Options volume, open interest, market cap
- **Premium potential**: Implied volatility, annualized returns
- **Quality tiers**: A/B/C ratings (80+/65-79/<65)
- **CSV export**: Full results for further analysis

#### Early Close Calculator
- **Profit-taking optimization**: When to close positions early
- **Breakeven analysis**: Days/price scenarios
- **Greeks decay tracking**: Time value erosion
- **Strategy comparison**: Hold to expiration vs early close

### 📈 Data & Analysis

#### Options Data Extraction
- Fetch option chains from Yahoo Finance (`yfinance`)
- Multiple expiration dates per ticker
- Real-time stock prices and company info
- Automatic local storage for historical tracking

#### Greeks and Metrics
- Days to expiration, implied volatility
- Delta, gamma, theta calculations
- Bid-ask spread analysis
- Moneyness classification (ITM/OTM/ATM)
- Probability calculations (Black-Scholes + Enhanced)

#### Portfolio Management
- Track stock positions with cost basis
- Track option positions (calls, puts, spreads)
- Identify covered call opportunities
- Calculate gains/losses with current prices
- Export to CSV/Excel

## 📦 Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Dependencies
- `yfinance>=0.2.32` - Yahoo Finance data
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `scipy>=1.10.0` - Statistical functions (Black-Scholes)
- `python-dateutil>=2.8.2` - Date handling
- `openpyxl>=3.1.0` - Excel export
- `tabulate>=0.9.0` - Table formatting

### Verification
```bash
python test_installation.py
```

## 🎯 Quick Start

### 1. Enhanced CSP Scan (Recommended)
```bash
python run_enhanced_csp_scan.py
```

**What it does:**
- Scans configured watchlist (default: AAPL, MSFT, NVDA, AMD, TSLA)
- Fetches options data and current stock prices
- Runs standard Black-Scholes probability analysis
- **Enhances probabilities** with technical/fundamental/sentiment data
- Shows comparison: BS prob vs Enhanced prob
- Displays detailed factor scores (Technical, Fundamental, Sentiment, Event Risk)
- Identifies opportunities made SAFER or RISKIER by analysis

**Output includes:**
- Market status (open/closed with price source indicators)
- Top opportunities table with prob adjustments
- Detailed analysis of top 5 with all scores
- Summary statistics by category
- Biggest probability adjustments

### 2. Standard CSP Scan (Faster)
```bash
python run_csp_only.py
```

Basic Black-Scholes probability without enhanced analysis. Faster for quick scans.

### 3. Research New Watchlist
```bash
python research_watchlist.py
```

**Evaluates 100+ tickers for:**
- Options liquidity (volume, open interest)
- Premium potential (IV, annual returns)
- Quality metrics (market cap, beta)
- Capital efficiency

**Generates:**
- Top 50 ranked opportunities
- Tier A/B/C breakdown
- Category summaries (Metals, Tech, S&P 500)
- Ready-to-use `WATCHLIST` for `config.py`
- CSV with full results

### 4. Wheel Strategy Opportunities
```bash
python analyze_wheel_opportunities.py
```

Finds stocks 5-10% below current price with high premiums, ideal for wheel rotation.

### 5. Portfolio Management
```bash
python example_portfolio.py
```

Demonstrates portfolio tracking, covered call opportunities, and position management.

## ⚙️ Configuration

### Capital Settings (`config.py`)
```python
CAPITAL_SETTINGS = {
    'available_cash': 50000.0,         # Total cash available
    'max_cash_per_position': 10000.0,  # Max per single position
    'reserve_cash': 5000.0,            # Cash to keep in reserve
    'max_positions': 5,                # Max simultaneous positions
    'auto_calculate_contracts': True,  # Auto-calc max contracts
}
```

### Watchlist (`config.py`)
```python
WATCHLIST = [
    # Core Tech
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'AMD', 'TSLA',

    # Semiconductors
    'INTC', 'AVGO', 'MU', 'QCOM',

    # Metals
    'SCCO', 'FCX', 'NEM', 'GLD',

    # Financials
    'JPM', 'BAC', 'GS',

    # ETFs (Best liquidity)
    'SPY', 'QQQ',
]
```

Use `research_watchlist.py` to generate optimized watchlists!

### Strategy Settings (`config.py`)
```python
CASH_SECURED_PUT_SETTINGS = {
    'min_premium': 0.50,
    'min_annual_return': 15.0,
    'min_days': 20,
    'max_days': 60,
    'min_prob_otm': 65.0,  # Standard BS probability
    'max_delta': -0.35,
    'min_volume': 100,
    'use_available_cash': True,  # Enable capital filtering
}
```

## 📊 Understanding Enhanced Analysis

### Probability Comparison
```
Standard Black-Scholes: 68% prob OTM
  Based only on: Current price, strike, volatility, time

Enhanced Probability: 75% prob OTM (+7% SAFER)
  Also considers:
  - Technical: Stock in strong uptrend (85/100)
  - Fundamental: High-quality company (82/100)
  - Sentiment: Bullish analyst ratings (74/100)
  - Event Risk: No earnings for 30 days (90/100)
  → Composite Score: 81/100
```

### Factor Scores (0-100)

**Technical Score:**
- Trend: Price vs 20/50/200-day SMA
- Momentum: Distance from moving averages
- Range: Position in 52-week high/low
- Volume: Average vs recent activity

**Fundamental Score:**
- Valuation: PE ratios (forward/trailing)
- Profitability: Margins, ROE, ROA
- Growth: Revenue/earnings growth
- Financial Health: Debt ratios, current ratio

**Sentiment Score:**
- Analyst Ratings: Buy/Hold/Sell consensus
- Price Targets: Upside/downside potential
- Coverage: Number of analysts following
- Recent Changes: Upgrades/downgrades

**Event Risk Score:**
- Earnings Dates: Days until next earnings
- Dividend Dates: Ex-dividend timing
- High Score = Low Risk (no events near expiration)

### Probability Adjustment Formula
```
Enhanced Prob = BS Prob + Adjustment
Adjustment = (Composite Score - 50) * 0.3

Example:
Composite Score: 80/100
Adjustment: (80 - 50) * 0.3 = +9%
BS Prob: 68%
Enhanced Prob: 77%
```

## 🔍 Market Closed Handling

### Smart Price Selection
When market is closed (bid = 0), the app automatically:

1. **Primary**: Use `bid` if > 0 (live market price)
2. **Fallback**: Use `lastPrice` if > 0 (yesterday's close)
3. **Conservative**: Use `ask/2` if > 0 (very conservative estimate)

### Price Transparency
```
Premium: $16.50
Price Details:
  - Bid: $0.00
  - Ask: $0.00
  - Last: $16.50 (USED - Market Closed)

⚠️ WARNING: Market closed - verify prices at open!
```

### Important Notes
- **lastPrice can be stale** after big moves (see AMD $250 PUT example)
- Always verify prices during market hours (9:30 AM - 4:00 PM ET)
- Check for recent stock price changes (earnings, news)
- Use `analyze_amd_250.py` to see detailed price analysis

## 📁 Project Structure

```
Stock Options App/
├── README.md                             # This file
├── requirements.txt                      # Python dependencies
├── config.py                             # Global configuration
├── .gitignore                            # Git ignore rules
│
├── Main Scanners
├── run_enhanced_csp_scan.py              # Enhanced CSP with prob analysis
├── run_csp_only.py                       # Standard CSP (fast)
├── run_early_close_scan.py               # Early close calculator
│
├── Research & Analysis Tools
├── research_watchlist.py                 # Watchlist research (100+ tickers)
├── analyze_wheel_opportunities.py        # Wheel strategy finder
├── analyze_amd_250.py                    # Price analysis example
├── explore_yfinance_data.py              # Data availability explorer
│
├── Portfolio & Examples
├── main.py                               # Original main app
├── example_portfolio.py                  # Portfolio management demo
├── quick_start.py                        # Quick start guide
│
├── Documentation
├── ENHANCED_PROBABILITY_GUIDE.md         # Enhanced analysis explained
├── YFINANCE_DATA_SUMMARY.md              # Available data summary
├── STRATEGY_COMPARISON.md                # Strategy comparisons
├── EARLY_PROFIT_TAKING_STRATEGY.md       # Early close guide
├── RECOMMENDATIONS_GUIDE.md              # Saved recommendations
├── CASH_FILTERING_GUIDE.md               # Capital management
│
├── Core Library (src/)
├── src/
│   ├── data/
│   │   ├── option_extractor.py           # Options data extraction
│   │   └── greeks_calculator.py          # Greeks & Black-Scholes
│   ├── strategies/
│   │   ├── covered_call.py               # Covered call analysis
│   │   ├── cash_secured_put.py           # CSP analysis (enhanced!)
│   │   └── wheel_strategy.py             # Wheel finder
│   ├── analysis/
│   │   └── enhanced_probability.py       # Enhanced prob calculator (NEW!)
│   └── portfolio/
│       └── portfolio_manager.py          # Portfolio tracking
│
└── Data Storage (data/)
    ├── option_chains/                    # Raw options data (CSV)
    ├── portfolio/                        # Portfolio files (JSON/CSV)
    └── recommendations/                  # Saved analysis results
```

## 🎓 Key Concepts

### Cash Secured Put (CSP)
Sell a put option and set aside cash to buy 100 shares if assigned.

**Example:**
- Stock: AMD at $253
- Sell: $240 PUT (5% below current)
- Premium: $12
- Net Entry if Assigned: $228 ($240 - $12)
- Capital Required: $24,000 ($240 × 100)

**Outcomes:**
- Stock > $240: Keep $1,200 premium, repeat next month
- Stock < $240: Buy 100 shares at $228 effective cost (10% below current!)

### Wheel Strategy
Complete cycle combining puts and calls:

1. **Sell PUT** → Collect premium
2. **Get Assigned** → Own stock at discount
3. **Sell CALL** → Collect more premium
4. **Called Away** → Stock sold at profit, back to step 1

**Benefits:** Consistent monthly income, lower entry prices, defined risk

### Enhanced vs Standard Probability

**Standard (Black-Scholes):**
- Pure mathematical model
- Inputs: Price, strike, volatility, time
- Assumes random walk, no drift
- Same for all stocks

**Enhanced:**
- Incorporates real-world factors
- Technical: Is stock trending up/down?
- Fundamental: Is company high quality?
- Sentiment: What do analysts think?
- Event Risk: Any catalysts upcoming?
- **Gives you an edge!**

## 📋 Common Use Cases

### 1. Weekly Income Strategy
```bash
# Find opportunities expiring in 7-14 days
python run_enhanced_csp_scan.py
# In config.py: min_days=7, max_days=14
```

### 2. Monthly Wheel Rotation
```bash
# Find wheel candidates (20-45 days)
python analyze_wheel_opportunities.py
```

### 3. Build Custom Watchlist
```bash
# Research best tickers for your style
python research_watchlist.py
# Copy results to config.py WATCHLIST
```

### 4. Earnings Avoidance
```bash
# Enhanced scan shows Event Risk Score
# Score < 40 = Earnings within option period!
python run_enhanced_csp_scan.py
# Look for Event Risk Score > 70
```

### 5. Quality Filtering
```bash
# Enhanced scan shows Composite Score
# Score > 70 = High quality opportunity
# Score 60-70 = Good quality
# Score < 60 = Risky
```

## ⚠️ Important Warnings

### Market Closed (lastPrice) Issues
**Problem:** After market close, bid/ask = $0, scanner uses `lastPrice`

**Risk:** lastPrice can be stale if stock moved significantly intraday

**Example:** AMD jumped +$18 (+7.6%) in one day
- Yesterday close: $235 → $250 PUT was ITM → lastPrice $16.50
- Today: $253 → $250 PUT is OTM → Real value ~$3-5, not $16.50!

**Solution:**
✅ Run scans during market hours (9:30 AM - 4:00 PM ET)
✅ Check recent price history (`analyze_amd_250.py`)
✅ Verify earnings/news events
✅ Use enhanced analysis Event Risk Score

### Enhanced Analysis Limitations
- Requires data availability (some stocks have limited coverage)
- Small caps may have poor analyst coverage
- International stocks may have less data
- Technical indicators lag (use recent data)
- Earnings surprises can override all factors

### General Options Risks
- **Capital intensive**: CSP requires $10k-50k per contract
- **Assignment risk**: You WILL own stock eventually
- **Volatility risk**: IV can drop after earnings (vol crush)
- **Opportunity cost**: Stock might moon while you're in puts
- **Margin calls**: If using margin (not recommended for beginners)

## 🚀 Advanced Usage

### Programmatic Access
```python
from src.analysis.enhanced_probability import EnhancedProbabilityAnalyzer

analyzer = EnhancedProbabilityAnalyzer()

result = analyzer.calculate_enhanced_probability(
    ticker='AAPL',
    strike=250,
    current_price=260,
    days_to_expiration=45,
    option_type='put',
    black_scholes_prob=75.0
)

print(f"BS Prob: {result['black_scholes_prob_otm']:.1f}%")
print(f"Enhanced Prob: {result['enhanced_prob_otm']:.1f}%")
print(f"Adjustment: {result['adjustment']:+.1f}%")
print(f"Technical Score: {result['technical_score']}/100")
print(f"Composite Score: {result['composite_score']}/100")
```

### Custom Watchlist Research
```python
# Edit research_watchlist.py to add your tickers
CANDIDATES = {
    'MY_SECTOR': {
        'Tech': ['TICKER1', 'TICKER2'],
        'Finance': ['TICKER3', 'TICKER4'],
    }
}
```

### Batch Analysis
```python
from src.data.option_extractor import OptionDataExtractor
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer

extractor = OptionDataExtractor()
analyzer = CashSecuredPutAnalyzer()

# Fetch 50 tickers
big_watchlist = ['AAPL', 'MSFT', ...]  # 50 tickers
data = extractor.fetch_and_store_options(big_watchlist, num_expirations=3)

# Analyze all
results = analyzer.get_top_opportunities(data, top_n=100)
results.to_csv('all_opportunities.csv')
```

## 📚 Additional Documentation

- **`ENHANCED_PROBABILITY_GUIDE.md`**: Complete guide to enhanced analysis
- **`YFINANCE_DATA_SUMMARY.md`**: All available data from yfinance
- **`STRATEGY_COMPARISON.md`**: Compare different strategies
- **`EARLY_PROFIT_TAKING_STRATEGY.md`**: When to close positions early
- **`CASH_FILTERING_GUIDE.md`**: Capital management explained
- **`RECOMMENDATIONS_GUIDE.md`**: Viewing saved analysis

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Additional strategies (iron condors, butterflies, etc.)
- Real-time monitoring and alerts
- Backtesting framework
- Broker API integration
- Machine learning models
- Mobile app interface

## 📄 License

Open source for personal use. Not for commercial redistribution.

## ⚖️ Disclaimer

**This application is for educational purposes only.**

- Not financial advice
- Options trading involves substantial risk
- Past performance does not guarantee future results
- Always do your own research
- Consider consulting a financial advisor
- The authors assume no liability for trading losses

**Use at your own risk. Trade responsibly.**

## 📞 Support

For issues or questions:
1. Check documentation in project root
2. Review examples in scanner scripts
3. Read docstrings in source code
4. Verify dependencies are installed
5. Ensure internet connection for data fetching
6. Run during market hours for best results

## 📌 Version

**Current Version:** 2.0.0
**Last Updated:** October 27, 2025
**Major Changes:**
- ✨ Enhanced probability analysis (technical/fundamental/sentiment)
- 🔄 Smart market-closed handling (bid/lastPrice/ask)
- 🎯 Wheel strategy finder
- 📊 Watchlist research tool (100+ tickers)
- ⚡ Early close calculator
- 🛡️ Event risk detection (earnings calendar)

---

## 🎯 Quick Command Reference

```bash
# Core Scanners
python run_enhanced_csp_scan.py          # Enhanced CSP scan ⭐
python run_csp_only.py                   # Standard CSP scan (fast)
python run_early_close_scan.py           # Early close calculator

# Research Tools
python research_watchlist.py             # Research 100+ tickers
python analyze_wheel_opportunities.py    # Wheel strategy finder
python analyze_amd_250.py                # Price analysis example

# Portfolio & Examples
python example_portfolio.py              # Portfolio demo
python quick_start.py                    # Quick start guide
python main.py                           # Original main app

# Data Exploration
python explore_yfinance_data.py          # See all available data
python how_to_access_data.py             # Data access guide
```

---

**Ready to get started?**

```bash
pip install -r requirements.txt
python run_enhanced_csp_scan.py
```

**Happy Trading! 📈💰**
