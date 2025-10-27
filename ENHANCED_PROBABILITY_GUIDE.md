

# Enhanced Probability Analysis Guide

## What Is This?

The standard CSP scanner uses **Black-Scholes probability** which assumes:
- Constant volatility
- Log-normal distribution
- No trends or patterns
- No fundamentals or sentiment

**This is limiting!** Real stocks have:
- ✓ Trends (uptrends, downtrends)
- ✓ Support/resistance levels
- ✓ Fundamental strength/weakness
- ✓ Analyst sentiment
- ✓ Upcoming earnings events

The **Enhanced Probability Analyzer** uses yfinance data to incorporate ALL these factors!

---

## What Data Does yfinance Provide?

### 1. **Technical Indicators** (from historical price data)
```python
✓ Price trends (20, 50, 200-day moving averages)
✓ 52-week high/low (support/resistance)
✓ Volume analysis
✓ Historical volatility
✓ Momentum indicators
```

### 2. **Fundamental Metrics** (from company info)
```python
✓ Valuation ratios (PE, PB, PS)
✓ Profitability (profit margins, ROE)
✓ Growth rates (revenue, earnings)
✓ Financial health (debt ratios)
✓ Beta (volatility vs market)
```

### 3. **Sentiment Factors** (from analyst data)
```python
✓ Analyst ratings (buy, hold, sell)
✓ Price targets
✓ Consensus recommendations
✓ Number of analysts covering stock
```

### 4. **Event Risk** (from earnings calendar)
```python
✓ Next earnings date
✓ Dividend dates
✓ Ex-dividend dates
```

---

## How the Enhanced Analyzer Works

### Step 1: Fetch Comprehensive Data

For each ticker, we fetch:
- 6 months historical prices
- Company fundamentals
- Analyst recommendations
- Earnings calendar

### Step 2: Calculate Component Scores (0-100)

#### A. Technical Score (35% weight)
**Measures: Trend strength and momentum**

Factors:
- SMA positions (current vs 20/50/200 day)
- Distance from support
- 52-week range position
- Volume patterns
- Strike-specific adjustment

Example:
```
AAPL at $262, selling $250 put, 45 DTE

Technical Factors:
- Price above 20-day SMA ($255) ✓ +15 points (uptrend)
- Price 7.7% above 50-day SMA ✓ +10 points (well supported)
- In upper 52-week range (95th percentile) ✓ +5 points
- Strike 5% below current (OTM) ✓ +3 points
- Normal volume ✓ +0 points

Technical Score: 83/100 (Strong)
```

#### B. Fundamental Score (25% weight)
**Measures: Company quality and stability**

Factors:
- Valuation (PE ratios)
- Profitability (margins, ROE)
- Growth (revenue, earnings)
- Financial health (debt levels)
- Beta (volatility)

Example:
```
AAPL Fundamentals:

- Forward PE: 31.6 (reasonable) ✓ +5 points
- Profit margins: 24.3% (excellent) ✓ +10 points
- ROE: 149.8% (exceptional) ✓ +5 points
- Revenue growth: 9.6% (good) ✓ +3 points
- Earnings growth: 12.1% (strong) ✓ +5 points
- Debt-to-equity: 154% (moderate) ✓ +5 points
- Beta: 1.09 (market-like) ✓ +5 points

Fundamental Score: 88/100 (Strong)
```

#### C. Sentiment Score (20% weight)
**Measures: Analyst and market sentiment**

Factors:
- Analyst ratings (buy/hold/sell)
- Price targets vs current
- Analyst coverage

Example:
```
AAPL Sentiment:

- Recommendation mean: 2.04 (Buy) ✓ +10 points
- Price target: $253 vs $263 current ✓ -3 points (slight downside)
- 41 analysts covering ✓ +5 points

Sentiment Score: 62/100 (Positive)
```

#### D. Event Risk Score (20% weight)
**Measures: Upcoming event risks**

Factors:
- Earnings dates within option period
- Dividend dates

Example:
```
AAPL Event Risk (45 DTE):

- Next earnings: Oct 31 (within period) ⚠️ -20 points
- Earnings in 6 days ⚠️ HIGH RISK

Event Risk Score: 30/100 (High Risk!)
```

### Step 3: Calculate Composite Score

```
Composite Score = (
    Technical × 0.35 +
    Fundamental × 0.25 +
    Sentiment × 0.20 +
    Event Risk × 0.20
)

AAPL Example:
= (83 × 0.35) + (88 × 0.25) + (62 × 0.20) + (30 × 0.20)
= 29.05 + 22.0 + 12.4 + 6.0
= 69.45/100
```

### Step 4: Adjust Black-Scholes Probability

```
Adjustment = ((Composite Score - 50) / 50) × 15%

Score 50 = Neutral (0% adjustment)
Score 100 = +15% adjustment (safer)
Score 0 = -15% adjustment (riskier)

AAPL Example:
Adjustment = ((69.45 - 50) / 50) × 15%
           = +5.8%

Black-Scholes Prob OTM: 70%
Enhanced Prob OTM: 70% + 5.8% = 75.8%
```

---

## Real-World Example Comparison

### Scenario: AAPL $250 PUT, 45 DTE

**Standard Analysis (Black-Scholes only):**
```
Current: $262
Strike: $250
Prob OTM: 70% (based only on implied volatility)
Decision: Looks okay
```

**Enhanced Analysis:**
```
Current: $262
Strike: $250

Technical Score: 83/100
- Strong uptrend (price > all SMAs)
- Well above support
- High in 52-week range

Fundamental Score: 88/100
- Excellent profitability
- Strong growth
- Healthy financials

Sentiment Score: 62/100
- Analyst buy rating
- Decent price target

Event Risk Score: 30/100
- EARNINGS IN 6 DAYS! ⚠️

Composite Score: 69/100
Enhanced Prob OTM: 75.8% (+5.8% adjustment)

RECOMMENDATION: CAUTION - High event risk!
Wait until after earnings to sell this put!
```

**The difference:** Enhanced analysis catches the earnings risk that Black-Scholes ignores!

---

## Using the Enhanced Scanner

### Run the Scanner:
```bash
python run_enhanced_csp_scan.py
```

### What You'll See:

```
COMPARISON: STANDARD vs ENHANCED PROBABILITY
==============================================================================

ticker | strike | days | prob_otm | enhanced_prob | adjustment | annual_return
-------|--------|------|----------|---------------|------------|---------------
AAPL   | $250   | 45   | 70.0%    | 75.8%         | +5.8%      | 28.5%
MSFT   | $420   | 42   | 68.5%    | 64.2%         | -4.3%      | 26.3%
NVDA   | $175   | 38   | 72.3%    | 78.1%         | +5.8%      | 32.1%
...
```

### Interpretation:

**Positive Adjustment (+):** Enhanced analysis thinks this is SAFER than Black-Scholes
- Good technicals, fundamentals, sentiment
- Low event risk
- Consider INCREASING position size

**Negative Adjustment (-):** Enhanced analysis thinks this is RISKIER than Black-Scholes
- Weak technicals, bad fundamentals, negative sentiment
- High event risk (earnings soon)
- Consider AVOIDING or DECREASING position size

**Near Zero (0 to ±2%):** Neutral
- Standard Black-Scholes is probably accurate
- No strong signals either way

---

## Benefits of Enhanced Analysis

### 1. **Avoid Event Risk**
Black-Scholes doesn't know about earnings dates!

Example:
```
TSLA $220 PUT, 30 DTE
BS Prob OTM: 72%
But earnings in 5 days!
Enhanced analysis: Event Risk Score 20/100
Recommendation: WAIT until after earnings
```

### 2. **Identify High-Quality Opportunities**
Combine good probability with strong fundamentals

Example:
```
MSFT $400 PUT, 45 DTE
BS Prob OTM: 70%
Strong fundamentals (Score: 85/100)
Bullish sentiment (Score: 78/100)
Enhanced Prob OTM: 76.5% (+6.5%)
Recommendation: EXCELLENT - Quality company + good prob
```

### 3. **Spot Hidden Risks**
Technical weakness Black-Scholes misses

Example:
```
STOCK $50 PUT, 40 DTE
BS Prob OTM: 68%
But: Downtrend (Technical Score: 30/100)
     Negative sentiment (Sentiment Score: 35/100)
Enhanced Prob OTM: 58% (-10%)
Recommendation: AVOID - Hidden technical/sentiment risks
```

### 4. **Prioritize Opportunities**
When you have multiple choices, pick the best!

```
Option A: 70% BS prob, +8% adjustment = 78% enhanced
Option B: 72% BS prob, -5% adjustment = 67% enhanced

Choose Option A! Better after enhanced analysis.
```

---

## Component Score Interpretation

### Technical Score

| Score | Meaning | Typical Characteristics |
|-------|---------|------------------------|
| 80-100 | Excellent | Strong uptrend, above all SMAs, high in 52W range |
| 60-79 | Good | Uptrend, above 50-day SMA, decent position |
| 40-59 | Neutral | Mixed signals, sideways movement |
| 20-39 | Weak | Downtrend, below SMAs, near 52W lows |
| 0-19 | Poor | Strong downtrend, well below support |

### Fundamental Score

| Score | Meaning | Typical Characteristics |
|-------|---------|------------------------|
| 80-100 | Excellent | High margins, strong ROE, low debt, consistent growth |
| 60-79 | Good | Profitable, reasonable valuation, good growth |
| 40-59 | Neutral | Average metrics, some concerns |
| 20-39 | Weak | Low profitability, high debt, declining |
| 0-19 | Poor | Unprofitable, very high debt, serious issues |

### Sentiment Score

| Score | Meaning | Typical Characteristics |
|-------|---------|------------------------|
| 80-100 | Very Bullish | Strong Buy rating, high price targets, many analysts |
| 60-79 | Bullish | Buy rating, upside to target price |
| 40-59 | Neutral | Hold rating, target near current price |
| 20-39 | Bearish | Sell rating, downside to target |
| 0-19 | Very Bearish | Strong Sell, significant downside expected |

### Event Risk Score

| Score | Meaning | Event Timing |
|-------|---------|--------------|
| 90-100 | Very Low | No earnings or events in period |
| 70-89 | Low | Events far out (30+ days) |
| 50-69 | Moderate | Events mid-period (14-30 days) |
| 30-49 | High | Events soon (7-14 days) |
| 0-29 | Very High | Events imminent (0-7 days) |

---

## When Enhanced Analysis Helps Most

### Scenario 1: High IV Stocks
**Problem:** High IV makes BS probabilities look worse
**Enhanced Solution:** Fundamentals + sentiment can show if IV is justified or excessive

### Scenario 2: Earnings Season
**Problem:** BS doesn't account for earnings
**Enhanced Solution:** Event risk score warns you

### Scenario 3: Multiple Similar Opportunities
**Problem:** Several options with similar BS probabilities
**Enhanced Solution:** Use composite scores to rank them

### Scenario 4: Trend Following
**Problem:** BS assumes no trends
**Enhanced Solution:** Technical score identifies strong trends (safer OTM puts in uptrends)

---

## Limitations & Caveats

### 1. **Not Perfect**
Enhanced analysis improves probabilities but doesn't guarantee outcomes.
- Markets can be irrational
- Black swans happen
- Past patterns don't guarantee future results

### 2. **Data Dependent**
Quality depends on yfinance data availability:
- Large caps: Excellent data (AAPL, MSFT, GOOGL)
- Small caps: May have limited analyst coverage
- International stocks: May have less data

### 3. **Adjustment Range**
Limited to ±15% adjustment to avoid over-confidence:
- Very strong signals: +10% to +15%
- Strong signals: +5% to +10%
- Moderate: +2% to +5%
- Neutral: -2% to +2%
- Weak: -5% to -2%
- Very weak: -10% to -15%

### 4. **Slower Execution**
Enhanced analysis fetches more data:
- Standard scan: ~30 seconds for 10 tickers
- Enhanced scan: ~2-3 minutes for 10 tickers
- Cache helps on repeated runs

---

## Practical Usage Tips

### Tip 1: Use for Final Selection
```
Step 1: Run standard scan to get candidates
Step 2: Run enhanced scan on top 20
Step 3: Pick the top 5 after enhanced analysis
```

### Tip 2: Check Event Risk Manually
If Event Risk Score < 50:
- Look up exact earnings date
- Consider waiting until after earnings
- Or use shorter DTE options

### Tip 3: Look for Alignment
Best opportunities have:
- ✓ High technical score (uptrend)
- ✓ High fundamental score (quality)
- ✓ High sentiment score (bullish)
- ✓ High event risk score (no earnings soon)

### Tip 4: Avoid Misalignment
Warning signs:
- ❌ High BS prob but low composite score
- ❌ Very low event risk score (earnings soon)
- ❌ Technical + sentiment both below 40

---

## Integration with Other Strategies

### Early Close Strategy + Enhanced Analysis
**Perfect Combination!**

```
1. Sell 45-60 DTE puts on stocks with:
   - High composite scores (60+)
   - High event risk scores (70+) [no earnings soon]
   - Good technical scores (60+) [uptrend]

2. Close at 50-75% profit as usual

3. Enhanced analysis helps you:
   - Pick which puts to sell
   - Avoid earnings disasters
   - Find highest-quality opportunities
```

### Hold-to-Expiration + Enhanced Analysis
```
Focus on:
- Very high enhanced prob OTM (75%+)
- High fundamental scores (quality companies)
- High event risk scores (avoid earnings)

These are "set and forget" opportunities with strong fundamentals.
```

---

## Summary: The Power of Enhanced Analysis

### What You Get:

**Before (Standard BS):**
```
AAPL $250 PUT
Prob OTM: 70%
Decision: Looks okay? Maybe?
```

**After (Enhanced):**
```
AAPL $250 PUT
BS Prob OTM: 70%
Enhanced Prob OTM: 75.8%

Component Breakdown:
- Technical: 83/100 (Strong uptrend)
- Fundamental: 88/100 (Excellent quality)
- Sentiment: 62/100 (Positive)
- Event Risk: 30/100 (EARNINGS IN 6 DAYS!)

Recommendation: WAIT - Earnings risk too high
                Try again after earnings or pick different strike
```

**Much better decision-making!**

---

## Try It Now!

```bash
# Explore what data is available
python explore_yfinance_data.py

# Run enhanced CSP scan
python run_enhanced_csp_scan.py
```

**You'll see probabilities adjusted based on real market factors beyond just volatility!**

---

## Bottom Line

**Black-Scholes is a starting point.**

**Enhanced analysis gives you an edge by incorporating:**
- ✓ Technical trends
- ✓ Fundamental quality
- ✓ Analyst sentiment
- ✓ Event timing

**Result: Better probability estimates = Better trade selection = Higher returns!**

🎯 **Use this to pick the BEST opportunities from your standard scans!**
