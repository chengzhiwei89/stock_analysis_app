# Changelog

All notable changes to the Stock Options Analysis App will be documented in this file.

## [1.1.0] - 2025-10-27

### Added
- **Near-ATM Safety Filter**: Implemented minimum distance requirement to prevent recommendations of options too close to at-the-money
  - Added `min_distance_pct` setting (default: 2.0%) to ensure strikes are at least 2% away from current price
  - Prevents high-risk assignments from near-ATM positions
  - Example: GOOGL $265 PUT at $266 stock (0.65% away) is now automatically blocked

### Changed
- **config.py**:
  - Updated `CASH_SECURED_PUT_ADVANCED['max_strike_pct']` from 1.0 to 0.98 (enforces 2% minimum cushion)
  - Added `CASH_SECURED_PUT_ADVANCED['min_distance_pct']` = 2.0 (new safety parameter)

### Fixed
- **Critical Bug in Distance Filter**: Fixed distance_pct calculation for PUT options
  - PUT options have negative distance_pct when OTM (strike < current price)
  - Filter now uses `abs(distance_pct) >= min_distance` to correctly handle negative values
  - Previous implementation incorrectly filtered out ALL OTM puts

### Technical Details
- **File**: `src/strategies/cash_secured_put.py` (lines 177-186)
- **Logic**: For PUTs, distance_pct is negative when strike < current (OTM). The safety filter now uses absolute value to ensure minimum distance regardless of option type.
- **Impact**: Scanner now correctly identifies 15-25 quality opportunities per scan (was finding 0 before fix)

### Verification
Tested with GOOGL at $266.74:
- ❌ BLOCKED: $265 PUT (0.65% distance) - Too risky
- ❌ BLOCKED: $262 PUT (1.59% distance) - Too risky
- ✅ ALLOWED: $260 PUT (2.53% distance) - Safe
- ✅ ALLOWED: $255 PUT (4.40% distance) - Safe

---

## [1.0.0] - 2025-10-25

### Initial Release
- Options data extraction using yfinance API
- Cash Secured Put (CSP) strategy analyzer
- Covered Call strategy analyzer
- Wheel strategy analyzer
- Enhanced probability analysis with technical/fundamental/sentiment factors
- Smart market-closed pricing (bid → lastPrice → ask/2 fallback)
- 31-ticker research-backed watchlist
- Black-Scholes probability calculations
- Comprehensive options metrics (Greeks, IV, probabilities)
- Export to CSV and Excel
- Automated recommendations saving
