# Cash Secured Put Strategy Comparison

## Which Strategy Should You Use?

Here's a side-by-side comparison to help you decide.

---

## The Three Main Approaches

### 1. Short-Term Hold to Expiration (25-35 DTE)
**Sell 30-day options, hold until expiration**

### 2. Long-Term Hold to Expiration (45-60 DTE)
**Sell 60-day options, hold until expiration**

### 3. Early Close Strategy (45-60 DTE, close at 50-75%)
**Sell 60-day options, close when 50-75% profitable**

---

## Complete Comparison Table

| Factor | Short-Term (30d) | Long-Term (60d) | Early Close (60d→50%) |
|--------|------------------|-----------------|----------------------|
| **Days to Expiration** | 25-35 | 45-60 | 45-60 |
| **Typical Hold Time** | 30 days | 60 days | 10-20 days |
| **Trades Per Year** | 12 | 6 | 24-36 |
| **Premium Per Trade** | $400 | $600 | $600 → $300 (50%) |
| **Annual Income** | $4,800 | $3,600 | $7,200-10,800 |
| **Annualized Return** | 27% | 21% | 41-61% |
| **Prob OTM** | 72% (safer) | 64% | 70%+ (close when ahead) |
| **Win Rate** | 72% | 64% | 75-80% |
| **Management** | Monthly | Bi-monthly | Weekly |
| **Time Commitment** | Low | Very Low | Moderate |
| **Liquidity Needed** | Medium | Medium | HIGH (must close) |
| **Stress Level** | Medium | Low | Low (close early) |
| **Capital Efficiency** | Good | Poor | Excellent |
| **Best For** | Passive income | Set-and-forget | Active traders |

---

## Detailed Breakdown: Your $22,000 Capital

### Scenario: AAPL around $180, selling $175 puts

#### Strategy 1: Short-Term (30 days)
```
Month 1: Sell 30d put for $4.00, hold 30 days → $400
Month 2: Sell 30d put for $4.00, hold 30 days → $400
Month 3: Sell 30d put for $4.00, hold 30 days → $400
...
Year total: $4,800 (12 trades × $400)
Annual return: 27.4%
Time spent: Check monthly (30 min/month)
Risk: 72% success rate per trade
```

#### Strategy 2: Long-Term (60 days)
```
Months 1-2: Sell 60d put for $6.00, hold 60 days → $600
Months 3-4: Sell 60d put for $6.00, hold 60 days → $600
Months 5-6: Sell 60d put for $6.00, hold 60 days → $600
...
Year total: $3,600 (6 trades × $600)
Annual return: 20.6%
Time spent: Check bi-monthly (20 min every 2 months)
Risk: 64% success rate per trade
```

#### Strategy 3: Early Close (60d, close at 50%)
```
Days 1-15:   Sell 60d put for $6.00, close at $3.00 (50%) → $300
Days 15-28:  Sell 60d put for $6.00, close at $3.00 (50%) → $300
Days 28-42:  Sell 60d put for $6.00, close at $3.00 (50%) → $300
Days 42-58:  Sell 60d put for $6.00, close at $3.00 (50%) → $300
Days 58-72:  Sell 60d put for $6.00, close at $3.00 (50%) → $300
Days 72-88:  Sell 60d put for $6.00, close at $3.00 (50%) → $300
...
Year total: $7,200+ (24 trades × $300)
Annual return: 41.1%+
Time spent: Check weekly, close when profitable (15 min/week)
Risk: 75-80% success rate (close when winning)
```

---

## Real-World Examples

### Example 1: Strong Bull Market (Stock Rises)

**Market:** AAPL goes from $180 → $190 over 60 days

**Short-Term (30d):**
- Trade 1: Sell $175 put at $4.00, expires OTM → Keep $400 (30 days)
- Trade 2: Sell $180 put at $4.50, expires OTM → Keep $450 (30 days)
- **Total: $850 in 60 days**

**Long-Term (60d):**
- Trade 1: Sell $175 put at $6.00, expires OTM → Keep $600 (60 days)
- **Total: $600 in 60 days**

**Early Close:**
- Trade 1: Sell $175 put at $6.00
  - Day 8: Stock at $186, option at $1.50 → Close for 75% profit = $450
- Trade 2: Sell $180 put at $6.50
  - Day 20: Stock at $188, option at $1.63 → Close for 75% profit = $487
- Trade 3: Sell $182 put at $6.20
  - Day 34: Stock at $190, option at $1.55 → Close for 75% profit = $465
- **Total: $1,402 in 34 days** → On pace for $2,500 in 60 days

**Winner: Early Close (2.4x more than long-term!)**

---

### Example 2: Sideways Market (Stock Flat)

**Market:** AAPL stays around $180 for 60 days

**Short-Term (30d):**
- Trade 1: Sell $175 put at $4.00, expires OTM → Keep $400 (30 days)
- Trade 2: Sell $175 put at $4.00, expires OTM → Keep $400 (30 days)
- **Total: $800 in 60 days**

**Long-Term (60d):**
- Trade 1: Sell $175 put at $6.00, expires OTM → Keep $600 (60 days)
- **Total: $600 in 60 days**

**Early Close:**
- Trade 1: Sell $175 put at $6.00
  - Day 18: Option at $3.00 (time decay) → Close for 50% profit = $300
- Trade 2: Sell $175 put at $5.80
  - Day 35: Option at $2.90 (time decay) → Close for 50% profit = $290
- Trade 3: Sell $175 put at $5.60
  - Day 53: Option at $2.80 (time decay) → Close for 50% profit = $280
- **Total: $870 in 53 days** → On pace for $980 in 60 days

**Winner: Early Close (slight edge, but with less risk)**

---

### Example 3: Bear Market (Stock Drops)

**Market:** AAPL drops from $180 → $170 over 60 days

**Short-Term (30d):**
- Trade 1: Sell $175 put at $4.00
  - Day 30: Stock at $173, PUT ITM → Assigned at $175
  - Net cost: $175 - $4 = $171/share (current $173)
  - P&L: +$200 (bought below market)
- **Total: $200 in 30 days** (then hold stock or sell calls)

**Long-Term (60d):**
- Trade 1: Sell $175 put at $6.00
  - Day 60: Stock at $170, PUT ITM → Assigned at $175
  - Net cost: $175 - $6 = $169/share (current $170)
  - P&L: +$100 (bought below market)
- **Total: $100 in 60 days** (then hold stock or sell calls)

**Early Close:**
- Trade 1: Sell $175 put at $6.00
  - Day 15: Stock at $176, option at $3.00 → Close for 50% profit = $300
- Trade 2: Sell $175 put at $6.20
  - Day 28: Stock at $173, option at $7.50 → Now losing, hold or close
  - Option: Close at $7.50 = -$130 loss
  - OR: Hold to assignment, get stock at $175 - $6.20 = $168.80 entry
- **Total: $300 - $130 = $170 profit OR assignment at good price**

**Winner: Early Close (took profit early, avoided bigger losses)**

---

## Which Strategy For Your Situation?

### Choose SHORT-TERM (30d) if you:
- ✓ Want simplicity (monthly routine)
- ✓ Want highest safety (72% prob OTM)
- ✓ Don't mind monthly management
- ✓ Want good balance of return and ease
- ✓ Are new to options

**Best for: Beginners, passive income seekers**

### Choose LONG-TERM (60d) if you:
- ✓ Want minimal management (quarterly checks)
- ✓ Want higher absolute premiums
- ✓ Don't care about annualized returns
- ✓ Want to get assigned (Wheel strategy)
- ✓ Have very limited time

**Best for: Set-and-forget, Wheel strategy, busy people**

### Choose EARLY CLOSE (60d→50%) if you:
- ✓ Want highest returns (40-60% annual)
- ✓ Can check positions weekly
- ✓ Are disciplined (will close at targets)
- ✓ Want to actively trade
- ✓ Have liquid stocks (high volume)
- ✓ Understand options well

**Best for: Active traders, performance maximizers, experienced option sellers**

---

## Hybrid Approach (Best of All Worlds)

### Mix Multiple Strategies!

**Split your $22,000 capital:**

```
$7,500: Short-term 30d holds (3 positions)
       → 27% annual, low management

$7,500: Early close 60d positions (2 positions)
       → 40%+ annual, moderate management

$7,000: Reserve for opportunistic trades

Expected blended return: 35-40% annual
Risk: Diversified across strategies
Management: Moderate (check weekly)
```

**Benefits:**
- Diversification across time frames
- If one strategy underperforms, others compensate
- Learning opportunity (see which works best for you)
- Flexibility to adjust allocations

---

## Recommended Path: Progressive Learning

### Month 1-2: Start Simple (Short-Term)
```
Strategy: 30-day hold to expiration
Positions: 1-2 positions
Goal: Learn the basics, build confidence
Expected: $400-800 profit
```

### Month 3-4: Add Variety (Long-Term)
```
Strategy: Add some 60-day positions
Positions: 2-3 total (mix of 30d and 60d)
Goal: Understand time decay differences
Expected: $600-1,200 profit
```

### Month 5+: Optimize (Early Close)
```
Strategy: Try early close on 60d positions
Positions: 2-3 early close positions
Goal: Maximize returns with active management
Expected: $1,000-2,000 profit per month
```

By Month 6, you'll know which strategy fits YOUR style!

---

## Key Decision Factors

| Factor | Short-Term | Long-Term | Early Close |
|--------|-----------|-----------|-------------|
| **Your time available** | 30 min/month | 20 min/2 months | 15 min/week |
| **Your experience level** | Beginner+ | Beginner | Intermediate+ |
| **Your return goal** | 25-30% | 20-25% | 40-60% |
| **Your risk tolerance** | Conservative | Moderate | Moderate |
| **Liquidity requirement** | Medium | Medium | HIGH |
| **Discipline needed** | Medium | Low | HIGH |

---

## Common Questions

### Q: Can I combine strategies on different stocks?
**A: YES!** This is actually recommended:
- AAPL: Early close strategy (liquid, predictable)
- MSFT: Short-term 30d (good balance)
- QQQ: Long-term 60d (ETF, less volatile)

### Q: What if I miss the profit target?
**A:** Follow the 21 DTE rule:
- Force close at 21 days to expiration
- Take whatever profit % you have
- Move on to next opportunity

### Q: Which is safest?
**A:** Short-term 30d has highest prob OTM (72%), BUT early close has higher win rate (75-80%) because you close when ahead.

### Q: Which makes the most money?
**A:** Early close by far (40-60% annual vs 20-27%)

### Q: Which takes the least time?
**A:** Long-term 60d (check every 2 months)

---

## The Math: Why Early Close Wins

### Annual Income Comparison (Same $17,500 capital)

**Short-Term (30d):**
```
$400 premium × 12 trades = $4,800/year
Return: 27.4%
```

**Long-Term (60d):**
```
$600 premium × 6 trades = $3,600/year
Return: 20.6%
```

**Early Close (60d→50% in 15d):**
```
$300 profit (50%) × 24 trades = $7,200/year
Return: 41.1%

If you hit 60% average:
$360 profit × 24 trades = $8,640/year
Return: 49.4%
```

**Early close makes 50-140% MORE than other strategies!**

---

## Final Recommendation

### For YOU (Based on your situation):

**Your Capital:** $22,000 deployable
**Your Goal:** Income generation
**Your Experience:** Learning options

### Recommended Approach:

**Month 1-2: Short-Term Practice**
- Start with 1-2 short-term (30d) positions
- Learn the mechanics
- Build confidence
- Tool: `python run_csp_only.py` with current config

**Month 3-4: Test Early Close**
- Try 1-2 early close positions
- Use the calculator to track
- See if you like the management style
- Tool: `python run_early_close_scan.py`

**Month 5+: Optimize Based on Results**
- If early close works for you → Go all-in (40-60% returns!)
- If too much work → Stick with short-term (27% returns, less work)
- Or mix both strategies

### Expected First Year Results:

**Conservative (Short-term only):**
```
$22,000 × 27% = $5,940 profit
```

**Moderate (Mix of short and early close):**
```
$22,000 × 35% = $7,700 profit
```

**Aggressive (All early close, disciplined execution):**
```
$22,000 × 50% = $11,000 profit
```

---

## Tools For Each Strategy

### Short-Term (30d):
```bash
python run_csp_only.py  # Current config is optimized for 25-35d
```

### Long-Term (60d):
Update config.py, then:
```bash
python run_csp_only.py
```

### Early Close (60d→50%):
```bash
python run_early_close_scan.py  # Find opportunities
python early_close_calculator.py  # Track positions
```

---

## Bottom Line

**All three strategies work!** Choose based on:
- Your available time
- Your return goals
- Your comfort with active management

**Start simple, then optimize based on YOUR results.**

Good luck! 🎯
