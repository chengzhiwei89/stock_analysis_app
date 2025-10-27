# How to Interpret Your Recommendations

## Understanding Cash Secured Put (CSP) Recommendations

When you open `csp_10tickers_20251025_225103.csv`, you'll see multiple columns. Here's what each means and how to use them for trading decisions.

---

## 📊 Key Columns Explained

### Basic Information

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **ticker** | Stock symbol | Which stock you're selling puts on |
| **current_stock_price** | Current market price | Compare with strike to see if you're buying at a discount |
| **strike** | Strike price of the put | The price at which you'd buy the stock if assigned |
| **expiration** | Expiration date | When the option expires |
| **days_to_expiration** | Days until expiration | Shorter = faster income but less premium |

### Premium & Income

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **bid** | What buyers are paying | You'll receive this price (conservative) |
| **ask** | What sellers are asking | Not relevant for CSPs (you're selling) |
| **premium_received** | Income per share | Usually = bid. Your income if you sell |
| **total_premium_received** | Total income for max contracts | If you sell max contracts, this is your income |

### Returns

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **annual_return** | Annualized return % | Compare opportunities - higher = better |
| **monthly_return** | Monthly return % | Income per month |
| **income_return** | Return on capital required | % return on strike price * 100 |

### Purchase Analysis

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **net_purchase_price** | Effective price if assigned | Strike - premium (your actual cost basis) |
| **discount_from_current** | Discount below current price | How much below market you'd buy |
| **capital_required** | Cash needed per share | Usually = strike price |

### Risk Metrics

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **distance_pct** | % from current price | Negative = OTM (safer), Positive = ITM (riskier) |
| **delta** | Probability of assignment | -0.30 = ~30% chance of assignment |
| **prob_otm** | Probability expires worthless | Higher = safer (you keep premium, no assignment) |
| **impliedVolatility** | Expected volatility | Higher = more premium but more risk |

### Cash Filtering (If Enabled)

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **max_affordable_contracts** | Max contracts you can sell | Based on your available cash |
| **total_capital_required** | Total cash needed | strike * 100 * contracts |
| **total_premium_received** | Total income | premium * 100 * contracts |

### Quality Indicators

| Column | What It Means | How to Use It |
|--------|---------------|---------------|
| **volume** | Daily trading volume | Higher = more liquid (easier to close) |
| **openInterest** | Open contracts | Higher = more liquid |
| **moneyness_class** | ITM/OTM/ATM | OTM = safer, ITM = riskier but more premium |

---

## 🎯 How to Choose the Best Opportunities

### Step 1: Filter by Your Goals

**For Income Generation (Conservative)**
- Look for: `prob_otm > 70%`
- Look for: `delta > -0.30` (lower probability of assignment)
- Look for: `discount_from_current > 3%`
- Accept: Lower `annual_return` (15-25%)

**For Stock Acquisition (Wheel Strategy)**
- Look for: `discount_from_current > 5%`
- Look for: Stocks you want to own
- Accept: Higher `delta` (higher probability of assignment)
- Bonus: `annual_return > 20%`

**For Aggressive Income**
- Look for: `annual_return > 30%`
- Look for: `monthly_return > 2%`
- Accept: Lower `prob_otm` (higher risk)
- Accept: Higher `impliedVolatility` (more volatile stocks)

### Step 2: Risk Assessment

**Low Risk Indicators:**
✅ `prob_otm > 70%` - High chance of expiring worthless
✅ `delta < -0.30` - Low assignment probability
✅ `distance_pct < -5%` - Strike well below current price
✅ `volume > 100` - Good liquidity
✅ `openInterest > 500` - Lots of market interest

**High Risk Indicators:**
⚠️ `prob_otm < 50%` - Likely to be assigned
⚠️ `delta > -0.20` - High assignment probability
⚠️ `distance_pct > 0` - Strike above current (ITM)
⚠️ `impliedVolatility > 0.5` - Very volatile stock
⚠️ `volume < 50` - Illiquid, hard to exit

### Step 3: Compare Returns vs Risk

**Good Opportunity:**
```
Ticker: AAPL
Strike: $170
Current Price: $180
Premium: $2.50
Annual Return: 22%
Prob OTM: 75%
Delta: -0.25

Analysis:
✅ Good return (22%)
✅ High probability of success (75% OTM)
✅ Buying 5.5% below current price ($170 vs $180)
✅ If assigned, you own AAPL at effective $167.50 (strike - premium)
```

**Risky Opportunity:**
```
Ticker: TSLA
Strike: $250
Current Price: $245
Premium: $8.00
Annual Return: 45%
Prob OTM: 40%
Delta: -0.60

Analysis:
⚠️ High return but HIGH RISK (45%)
⚠️ Low success probability (40% OTM)
⚠️ Strike ABOVE current (ITM - already in the money)
⚠️ 60% chance of assignment
⚠️ Only works if you really want TSLA at $242 ($250 - $8)
```

---

## 💡 Example: Reading Your First Opportunity

Let's say the top row in your CSV shows:

```csv
ticker,current_stock_price,strike,expiration,days_to_expiration,premium_received,annual_return,monthly_return,net_purchase_price,discount_from_current,prob_otm,delta,volume,max_affordable_contracts,total_capital_required,total_premium_received
NVDA,142.50,135,2024-11-22,28,2.80,29.5,2.4,132.20,7.2,68,-0.32,1250,1,13500,280
```

### What This Means:

**The Trade:**
- Sell 1 put contract on NVDA
- Strike: $135
- Expiration: November 22, 2024 (28 days away)
- Premium: $2.80/share = **$280 total** (2.80 × 100)

**Your Income:**
- Immediate income: **$280** (credited to your account)
- Annualized return: **29.5%**
- Monthly return: **2.4%**

**The Math:**
- Capital required: **$13,500** (135 × 100)
- You need this much cash in your account
- This cash is "secured" for the put

**If NVDA Stays Above $135:**
✅ Option expires worthless
✅ You keep the **$280**
✅ Your cash is freed up
✅ Total time: 28 days

**If NVDA Drops Below $135:**
📦 You're assigned - must buy 100 shares
📦 Purchase price: $135/share = $13,500
📦 But you already got $280 premium
📦 Effective cost: **$132.20/share** (net_purchase_price)
📦 This is **7.2% below** current price ($142.50)

**Risk Assessment:**
- 68% probability it expires worthless (prob_otm)
- 32% probability you'll be assigned (100% - 68%)
- Delta of -0.32 confirms ~32% assignment risk
- Good volume (1,250) - easy to close if needed

**Your Decision:**
✅ **YES** if:
- You're okay owning NVDA at $132.20 (good discount!)
- You have $13,500 available
- You're comfortable with 32% assignment risk
- 29.5% annual return is attractive

❌ **NO** if:
- You don't want to own NVDA
- You don't have $13,500 in cash
- 32% assignment risk is too high
- You need a higher probability of success

---

## 📈 Practical Examples

### Example 1: Conservative Income Play

```
Looking for: Safe income, don't want assignment

Filter the CSV:
- prob_otm > 75%
- delta > -0.25
- volume > 100
- annual_return > 15%

Result might be:
Ticker: SPY
Strike: $450 (current: $475)
Premium: $1.50
Annual Return: 18%
Prob OTM: 82%

Translation:
- Very safe (82% won't be assigned)
- $150 income per contract
- If assigned, buying SPY at $448.50 (5.6% discount)
- Requires $45,000 per contract
```

### Example 2: Wheel Strategy Entry

```
Looking for: Buy quality stock at discount

Filter the CSV:
- discount_from_current > 5%
- Tickers you want to own (AAPL, MSFT, etc.)
- annual_return > 20%
- Accept lower prob_otm (you WANT assignment)

Result might be:
Ticker: AAPL
Strike: $170 (current: $180)
Premium: $3.50
Annual Return: 24%
Discount: 5.5%
Prob OTM: 60%

Translation:
- 40% chance you'll own AAPL at $166.50
- That's a great entry if you want AAPL
- Even if not assigned, 24% return is good
- Then you can sell covered calls on the shares
```

### Example 3: Using Cash Filtering

```
Your available cash: $27,000 (from config)
Max per position: $27,000

CSV shows max_affordable_contracts:

Opportunity 1:
Strike: $250 → 1 contract needs $25,000 ✅
max_affordable_contracts: 1
total_capital_required: $25,000
total_premium_received: $500

Opportunity 2:
Strike: $600 → 1 contract needs $60,000 ❌
max_affordable_contracts: 0
(This won't show up if filtered)

You can immediately see what you can afford!
```

---

## 🎓 Decision Framework

### Step-by-Step Process:

1. **Open the CSV in Excel**
   - Sort by `annual_return` (highest first)
   - Or sort by `prob_otm` (safest first)

2. **Apply Filters Based on Your Goals**
   ```
   Conservative:
   - prob_otm > 70%
   - volume > 100
   - annual_return > 15%

   Aggressive:
   - annual_return > 30%
   - Accept lower prob_otm

   Wheel:
   - discount_from_current > 5%
   - Stocks you want
   ```

3. **Check Risk Metrics**
   - Is `delta` acceptable? (-0.30 or lower is safer)
   - Is `prob_otm` acceptable? (70%+ is safer)
   - Is liquidity good? (volume > 100)

4. **Verify You Can Afford It**
   - Check `capital_required` or `total_capital_required`
   - Do you have that much cash?
   - Does it fit your position sizing rules?

5. **Ask the Key Questions**
   - Am I okay owning this stock at `net_purchase_price`?
   - Is the `annual_return` worth the risk?
   - Do I have the `capital_required`?
   - Can I close the position if needed? (check volume)

6. **Make the Trade**
   - Log into your broker
   - Sell to open put option
   - Strike: `strike` column
   - Expiration: `expiration` column
   - Limit price: `bid` or slightly higher

---

## 🚦 Red Flags to Avoid

❌ **Very High IV** (impliedVolatility > 0.8)
- Stock is extremely volatile
- High premium but high risk
- May gap down suddenly

❌ **Low Volume** (< 50)
- Hard to close if you need to exit
- Wide bid-ask spreads
- May not get filled at good price

❌ **ITM Puts** (distance_pct > 0)
- Already in the money
- Very high probability of assignment
- Only do if you really want the stock NOW

❌ **Low Prob OTM** (< 40%)
- More likely to be assigned than not
- High risk for income-only strategy
- Better for stock acquisition

---

## 💰 Real-World Example: Your $27,000 Cash

Based on your `config.py` settings:
- Available cash: $27,000
- Max per position: $27,000
- Reserve: $5,000
- Deployable: $22,000

**What you can trade:**

```
Opportunity A:
Strike: $200 → Requires $20,000 per contract
max_affordable_contracts: 1 ✅
Premium: $400
You can do this!

Opportunity B:
Strike: $500 → Requires $50,000 per contract
max_affordable_contracts: 0 ❌
Filtered out - too expensive

Opportunity C:
Strike: $100 → Requires $10,000 per contract
max_affordable_contracts: 2 ✅
But max_per_position limits you to 1
Premium: $150 per contract
```

---

## 📝 Quick Reference Card

**For Income Generation:**
- Sort by: `annual_return` (high to low)
- Filter: `prob_otm > 70%`, `volume > 100`
- Pick: High return + High probability

**For Stock Acquisition:**
- Sort by: `discount_from_current` (high to low)
- Filter: Stocks you want to own
- Pick: Good discount + Acceptable return

**For Safety:**
- Sort by: `prob_otm` (high to low)
- Filter: `delta < -0.30`, `volume > 500`
- Pick: Highest probability + Reasonable return

**For Max Premium:**
- Sort by: `premium_received` (high to low)
- Filter: `volume > 100`
- Pick: High premium + Manageable risk

---

## 🎯 Summary

Your CSV contains all the data you need. Focus on:

1. **Annual Return** - How much you'll make
2. **Prob OTM** - How safe it is
3. **Capital Required** - Can you afford it?
4. **Net Purchase Price** - Happy with this if assigned?
5. **Volume** - Can you exit if needed?

**Golden Rule:**
> Only sell puts on stocks you'd be happy to own at the net purchase price

**Would you run `python my_portfolio_setup.py` so I can show you how to interpret YOUR NVDA covered call recommendations specifically?**
