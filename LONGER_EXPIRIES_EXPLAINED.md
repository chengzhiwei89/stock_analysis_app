# Why Longer Expiries Weren't Showing Up

## The Problem

Your previous scan showed **only 26-day options** (all expiring 2025-11-21). No 30-45 day options appeared even though `max_days` was set to 45.

## Why This Happened

Longer-dated options have different characteristics that caused them to be filtered out:

### 1. Lower Probability OTM
- **26 days out**: ~70-80% prob_otm ✓
- **40 days out**: ~60-65% prob_otm ❌ (filtered by min_prob_otm: 70%)

More time = more uncertainty = lower probability of success

### 2. Higher Delta (More Negative)
- **26 days out**: Delta around -0.25 to -0.30 ✓
- **40 days out**: Delta around -0.35 to -0.40 ❌ (filtered by max_delta: -0.30)

More time = higher delta = higher assignment probability

### 3. Lower Annualized Returns
- **26 days out**: 20-50% annualized ✓
- **40 days out**: 15-25% annualized ❌ (filtered by min_annual_return: 20%)

More time = lower annualized rate (though higher absolute premium)

## The Solution - Relaxed Criteria

I've updated `config.py` with **more realistic criteria for longer-dated options**:

### Changes Made

| Setting | Before | After | Reason |
|---------|--------|-------|--------|
| `max_days` | 45 | **60** | Allow options up to 2 months out |
| `min_prob_otm` | 70% | **65%** | Accept slightly lower probability |
| `max_delta` | -0.30 | **-0.35** | Accept slightly higher delta |
| `min_annual_return` | 20% | **15%** | Accept lower annualized returns |
| `NUM_EXPIRATIONS` | 4 | **6** | Fetch more expiration dates |

### Still Safe!
- **65% prob_otm** = Still 65% chance of success (nearly 2 in 3)
- **-0.35 max delta** = Still only ~35% assignment probability
- **15% annual return** = Still excellent returns
- **100+ volume** = Still good liquidity
- **Quality stocks only** = Still AAPL, MSFT, NVDA, etc.

## Understanding the Trade-off

### Longer Options = Different Risk/Reward Profile

**Advantages of Longer Options (30-60 days):**
- ✓ Higher absolute premiums ($5-10 vs $3-5)
- ✓ More time for mean reversion if stock dips
- ✓ Can roll out if needed (more flexibility)
- ✓ Better for Wheel strategy (longer assignment window)

**Disadvantages:**
- ⚠️ Lower prob_otm (65% vs 75%)
- ⚠️ Higher delta (more assignment risk)
- ⚠️ Lower annualized returns (15-25% vs 25-40%)
- ⚠️ Capital tied up longer

### Example Comparison

**26-Day Option (Previous Results):**
```
AMD $230 strike, 26 days
Premium: $8.25 per share ($825 total)
Annual Return: 50.4%
Prob OTM: 73.6%
Delta: -0.26
Capital: $23,000
```

**45-Day Option (Now Visible):**
```
AMD $230 strike, 45 days (hypothetical)
Premium: $11.50 per share ($1,150 total)
Annual Return: 25.8%  ← Lower annualized
Prob OTM: 67.3%  ← Lower probability
Delta: -0.34  ← Higher delta
Capital: $23,000
```

**Which is better?**
- 26-day: Higher annualized return, safer probability, BUT you have to manage position sooner
- 45-day: Higher absolute income, more time flexibility, BUT slightly riskier

## What You'll See Now

Run the scan again:
```bash
python run_csp_only.py
```

You should now see:
- ✓ Options at 25-60 days (not just 26 days)
- ✓ Mix of short-term (25-35 days) and medium-term (35-60 days)
- ✓ Higher absolute premiums on longer options
- ✓ Mix of annualized returns (15-40%)
- ✓ Still safe (65%+ prob_otm, quality stocks)

## Customizing Further

### Want MORE Longer Options?
Edit `config.py`:
```python
CASH_SECURED_PUT_SETTINGS = {
    'max_days': 90,           # Up to 3 months
    'min_prob_otm': 60.0,     # Accept 60%+ probability
    'max_delta': -0.40,       # Accept higher delta
    'min_annual_return': 12.0, # Lower return threshold
}
```

### Want SAFER Short-Term Only?
```python
CASH_SECURED_PUT_SETTINGS = {
    'min_days': 20,
    'max_days': 35,           # Only 20-35 days
    'min_prob_otm': 70.0,     # Higher probability
    'max_delta': -0.30,       # Lower delta
    'min_annual_return': 20.0, # Higher returns
}
```

## Key Insight

**There's no "perfect" setting** - it depends on your strategy:

🎯 **Income Strategy** (collect premium, avoid assignment)
- Shorter options (25-35 days)
- Higher prob_otm (70%+)
- Lower delta (≤ -0.30)
- Higher annualized returns (20%+)

🎯 **Wheel Strategy** (want to own stocks)
- Longer options (35-60 days)
- Lower prob_otm OK (60-70%)
- Higher delta OK (≤ -0.35)
- Lower returns OK (15%+)
- Focus on entry price/discount

🎯 **Balanced** (NEW default)
- Mix of 25-60 days
- 65%+ prob_otm
- ≤ -0.35 delta
- 15%+ returns

## Why NUM_EXPIRATIONS Increased to 6

Fetching 6 expiration dates (instead of 4) gives you:
- More date choices to find optimal risk/reward
- Better chance of finding 35-60 day options that meet criteria
- More flexibility in position management

## Run Again to See Results

```bash
python run_csp_only.py
```

You should now see a **mix of durations** (26, 33, 40, 47, 54, 60 days) instead of just 26 days!

## Summary

**Before:**
- All results = 26 days (too strict)
- Only shortest-term options qualified
- Missing medium-term opportunities

**After:**
- Results = 25-60 days (balanced)
- Mix of short and medium-term
- More choices for different strategies
- Still safe (65%+ prob, quality stocks)
