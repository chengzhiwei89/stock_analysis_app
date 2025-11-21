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
# GETTING STARTED WITH EARLY CLOSE STRATEGY

## Quick Start Guide - Start Making 50%+ Returns TODAY!

This guide will walk you through implementing the early close strategy step-by-step.

---

## Step 1: Find Opportunities (5 minutes)

### Run the Early Close Scanner:
```bash
python run_early_close_scan.py
```

This will show you 45-60 day options perfect for early closing.

### What You'll See:
```
TOP 20 EARLY CLOSE OPPORTUNITIES

ticker | strike | days | premium | target_50% | target_75% | prob_otm | volume
AAPL   | $180   | 52   | $5.50   | $2.75      | $1.38      | 68.5%    | 1,245
MSFT   | $420   | 48   | $8.20   | $4.10      | $2.05      | 71.2%    | 982
...
```

### Pick Your Trade:
Choose 1-2 positions that:
- ✓ You can afford (capital < $22,000)
- ✓ Stock you'd want to own
- ✓ High volume (500+)
- ✓ Good prob_otm (65%+)

---

## Step 2: Calculate Your Targets (2 minutes)

### Use the Calculator:
```bash
python early_close_calculator.py
```

Select option **7** (Quick Calculator)

### Example:
```
Premium received: 5.50
Number of contracts: 1

50% PROFIT TARGET:
  Close when option = $2.75
  Profit = $275

75% PROFIT TARGET:
  Close when option = $1.38
  Profit = $412
```

Write these numbers down!

---

## Step 3: Open the Trade in Your Broker (5 minutes)

### In Your Brokerage Account:

1. **Navigate to Options Trading**
2. **Select the stock** (e.g., AAPL)
3. **Choose the expiration** (e.g., Dec 15, 2024)
4. **Find the strike** (e.g., $180 PUT)
5. **Action**: **Sell to Open** (STO)
6. **Quantity**: 1 contract
7. **Order Type**: Limit order at BID price or slightly above
8. **Review**:
   - You receive: $550 (premium)
   - Capital required: $18,000 (secured cash)
9. **Submit Order**

### Wait for Fill
- Should fill within minutes if liquid
- If not filling, raise limit price by $0.05

---

## Step 4: Set Profit Target Alerts (5 minutes)

**CRITICAL STEP** - This is how you capture profits automatically!

### In Your Broker's Alert System:

#### Alert 1: 50% Profit Target
```
Symbol: AAPL 180 PUT Dec 15
Condition: Last Price <= $2.75
Action: Email/SMS me
Message: "AAPL PUT at 50% profit - CLOSE NOW!"
```

#### Alert 2: 75% Profit Target
```
Symbol: AAPL 180 PUT Dec 15
Condition: Last Price <= $1.38
Action: Email/SMS me
Message: "AAPL PUT at 75% profit - CLOSE NOW!"
```

#### Alert 3: Force Close Reminder (Calendar Alert)
```
Date: 21 days from expiration (e.g., Nov 24)
Message: "Force close AAPL PUT at 21 DTE - Close regardless of profit!"
```

---

## Step 5: Track the Position (30 seconds)

### Add to Your Tracker:
```bash
python early_close_calculator.py
```

Select option **1** (Add new position)

```
Ticker: AAPL
Strike price: 180
Expiration: 2024-12-15
Premium received per share: 5.50
Number of contracts: 1
Days to expiration when opened: 52
```

The tracker will show:
```
✓ Position added: AAPL $180 PUT
  Premium: $5.50 × 1 = $550
  50% target: Close at $2.75 for $275 profit
  75% target: Close at $1.38 for $412 profit
```

---

## Step 6: Wait for Alerts (10-20 days)

### What Happens Now:

**Best Case (5-15 days):**
- Stock moves up
- Option drops to $1.38
- Alert triggers: "75% profit!"
- You close for $412 profit (75% of max)

**Good Case (10-20 days):**
- Stock stays flat or rises slightly
- Option drops to $2.75
- Alert triggers: "50% profit!"
- You close for $275 profit (50% of max)

**Neutral Case (21+ days):
- No alert by day 21 DTE
- Close anyway (force close rule)
- Profit: Whatever % achieved (maybe 25-40%)

**Worst Case:**
- Stock drops significantly
- Option increases in value
- Hold until assignment or close at loss
- Get assigned: Own 100 shares at strike price

---

## Step 7: Close the Position (2 minutes)

### When Alert Triggers:

1. **Log into broker immediately**
2. **Find the open position**
3. **Action**: **Buy to Close** (BTC)
4. **Quantity**: 1 contract
5. **Order Type**: Market order (you want to close NOW)
6. **Submit**

### Update Your Tracker:
```bash
python early_close_calculator.py
```

Select option **2** (Close position)

```
Select position: 1 (AAPL $180 PUT)
Close price per share: 2.75
```

Results:
```
✓ Position closed: AAPL $180 PUT
  Opened: $5.50 × 1
  Closed: $2.75 × 1
  Profit: $275.00 (50.0%)
  Days held: 14
  Annualized return: 319%!
  ✓ GOOD! Hit 50% target!
```

---

## Step 8: Repeat Immediately!

**Don't wait!** Immediately start Step 1 again:

```bash
python run_early_close_scan.py
```

Find another 45-60 DTE option and repeat the cycle!

---

## Real Example: First 60 Days

### Trade 1: AAPL $180 PUT
```
Day 0: Sell for $5.50 (52 DTE)
Day 14: Close at $2.75 (50% profit)
Profit: $275 in 14 days
Annualized: 319%
```

### Trade 2: MSFT $420 PUT (Same $18,000 capital!)
```
Day 14: Sell for $8.00 (48 DTE)
Day 26: Close at $2.00 (75% profit)
Profit: $600 in 12 days
Annualized: 372%
```

### Trade 3: NVDA $175 PUT
```
Day 26: Sell for $4.50 (55 DTE)
Day 42: Close at $2.25 (50% profit)
Profit: $225 in 16 days
Annualized: 256%
```

### Trade 4: AAPL $185 PUT
```
Day 42: Sell for $6.20 (49 DTE)
Day 60: Close at $3.10 (50% profit)
Profit: $310 in 18 days
Annualized: 313%
```

**Total in 60 days: $1,410 profit on $18,000 capital = 7.8% in 2 months = 47% annualized!**

And you only had 4 positions to manage over 60 days!

---

## Tools You Have

### 1. run_early_close_scan.py
- Finds 45-60 DTE opportunities
- Shows profit targets
- Filters for high liquidity

### 2. early_close_calculator.py
- Track all positions
- Calculate profit targets
- View statistics
- Print broker alerts

### 3. config_early_close.py
- Pre-configured settings
- Helper functions
- Example usage

---

## Important Rules

### The 3 Rules of Early Close:

1. **ALWAYS close at 50-75% profit**
   - Don't get greedy!
   - The last 25-50% takes the most time and risk

2. **Force close at 21 DTE**
   - Even if below 50% profit
   - Gamma risk increases after 21 DTE

3. **Never hold last 7 days**
   - Highest risk period
   - Close or roll before final week

---

## Tracking Your Performance

### View Your Stats:
```bash
python early_close_calculator.py
```

Select option **5** (Print summary)

You'll see:
```
STATISTICS:
  Total Profit: $1,410
  Average Profit %: 58.3%
  Average Days Held: 15.0
  Average Annualized Return: 315%
  Win Rate: 100%

TARGET HIT RATE:
  75% Target: 1/4 (25%)
  50% Target: 4/4 (100%)
```

---

## Troubleshooting

### "My option isn't reaching 50% profit after 20 days"

**Solution:** Follow the 21 DTE rule:
- If you opened a 45 DTE option
- Day 24 = 21 DTE remaining
- Close regardless of profit %
- Move on to next opportunity

### "Stock dropped and my option increased in value"

**Options:**

1. **Close at small loss** - Move on, not every trade wins
2. **Hold to assignment** - Own stock at strike price
3. **Roll down and out** - Close and sell new put at lower strike, later date

### "I can't find any 45-60 DTE options"

**Solution:** Adjust settings in run_early_close_scan.py:
- Lower min_volume to 250
- Expand days to 35-70
- Lower min_premium to 0.75

---

## Expected Results

### Conservative Estimate:
- Target: 50% profit in 15 days average
- Trades per year: 24
- Win rate: 75%
- Annual return: 35-40%

### Aggressive Estimate:
- Target: 60% profit in 12 days average
- Trades per year: 30
- Win rate: 80%
- Annual return: 50-60%

### Your $22,000:
- Conservative: $7,700 - $8,800 annual profit
- Aggressive: $11,000 - $13,200 annual profit

**Much better than holding to expiration!**

---

## Weekly Routine (15 minutes)

### Monday Morning:
1. Check tracker for open positions
2. Review any positions approaching 21 DTE
3. Check if any positions need force close

### Wednesday Evening:
1. Check for any triggered alerts
2. Close profitable positions
3. Open new positions with freed capital

### Friday Afternoon:
1. Review week's performance
2. Plan trades for next week
3. Update tracker

---

## Your First Trade Checklist

- [ ] Run early_close_scan.py
- [ ] Pick 1 position (start with just 1!)
- [ ] Calculate targets with calculator
- [ ] Open trade in broker
- [ ] Set 50% and 75% alerts
- [ ] Add to position tracker
- [ ] Set calendar reminder for 21 DTE
- [ ] Wait for alert
- [ ] Close at profit target
- [ ] Update tracker
- [ ] Open next position
- [ ] Repeat!

---

## Support

If you need help:

1. Read EARLY_PROFIT_TAKING_STRATEGY.md for full details
2. Read SHORT_VS_LONG_OPTIONS_EXPLAINED.md for why this works
3. Check your tracker: `python early_close_calculator.py`
4. Review your closed positions to learn

---

## Ready to Start?

```bash
# Step 1: Find opportunities
python run_early_close_scan.py

# Step 2: After you open a trade, track it
python early_close_calculator.py
```

**Good luck! Remember: Take profits early, don't get greedy, and repeat often!**

🎯 Target: 50% profit in ~15 days
📈 Expected annual return: 35-60%
✓ Much better than hold-to-expiration!
# Quick Interpretation Guide

This guide for Cash Secured Put (CSP) recommendations focuses on key option metrics like ticker, strike, premium, annual return, probability OTM, delta, days to expiration, and capital required. It provides a decision-making framework for selecting trades based on affordability, stock desirability, return goals, risk (probability OTM, delta), and liquidity (volume, open interest).

The guide differentiates between conservative, aggressive, and wheel strategy approaches, specifying ideal metrics for each. It also outlines how to use CSV output for analysis (sorting, filtering in Excel) and stresses the crucial question: "Am I okay owning this stock at the net purchase price?". Common pitfalls such as high premium with low probability OTM, low volume, in-the-money (ITM) strikes, and trading undesired stocks are highlighted. Finally, it offers quick action steps for trade execution and references additional resources.

# Cash Filtering for Cash Secured Puts - Quick Guide

This guide details the cash filtering functionality for Cash Secured Put (CSP) opportunities, ensuring users only see affordable trades. Key features include configuring capital settings (`available_cash`, `max_cash_per_position`, `reserve_cash`) in `config.py` and enabling `use_available_cash` in `CASH_SECURED_PUT_SETTINGS`. When enabled, new output columns display `max_affordable_contracts`, `total_capital_required`, and `total_premium_received`. The guide explains how the system calculates deployable cash and max contracts, filters out unaffordable opportunities, and demonstrates different use cases for conservative vs. aggressive trading styles. It also provides helper functions (`get_deployable_cash`, `calculate_max_contracts`) and troubleshooting tips for common issues like finding no affordable opportunities or `max_affordable_contracts` always being one. The primary benefit is to streamline analysis by showing only relevant opportunities, managing position sizing, and ensuring a cash reserve.

# Recommendations Storage Guide

This guide details the automatic saving of analysis recommendations (Covered Calls, Cash Secured Puts, Wheel Strategy) to `data/recommendations/`. Key features include auto-save by default, CSV and JSON metadata formats, combined Excel files, searchable by ticker, timestamped records, and auto-cleanup of old files based on a configurable `keep_days` setting in `config.py`. It details the directory structure, file formats, and multiple methods for viewing and managing recommendations, including a command-line tool (`view_recommendations.py`), Python programmatic access (`RecommendationsManager`), and direct file access. The document also provides use cases like tracking performance over time, comparing different days' recommendations, exporting for external analysis, and building a trading log. It offers integration tips for Excel and Google Sheets, important notes on capital management, and troubleshooting advice. The main benefit is robust historical tracking and easier access to analysis results.

# How to Access and Save DataFrames

This script serves as a comprehensive guide and demonstration for accessing and saving data within the stock options analysis application. It outlines six methods for data interaction:

1. **Fresh Analysis**: Running analyses (Covered Calls, Cash Secured Puts) to get results directly as pandas DataFrames in memory.
2. **Load Previously Fetched Raw Data**: Loading the most recent raw options data saved to disk (`data/option_chains/options_data_YYYYMMDD_HHMMSS.csv`) for re-analysis.
3. **Save Analysis Results**: Manually saving analysis results (DataFrames) to CSV or Excel files.
4. **Load Previously Saved Analysis Results**: Loading these manually saved CSV/Excel files back into DataFrames.
5. **Working with DataFrames Directly**: Demonstrating common pandas DataFrame operations like filtering, sorting, and calculating custom metrics.
6. **Interactive Python Access**: Providing examples for interactive use in a Python console or Jupyter notebook.

The script emphasizes that analysis results are temporary (in memory) unless explicitly saved, while raw options data and portfolio data are automatically saved. It concludes with best practices for data management and a quick reference for common data access and saving commands.