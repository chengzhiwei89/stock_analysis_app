"""
Configuration Settings
Modify these settings to customize your analysis
"""

# ============================================================================
# WATCHLIST - Tickers to analyze (30 tickers optimized for options income)
# Research-backed selection: Score 75+, good liquidity, diverse sectors
# ============================================================================
WATCHLIST = [
    # === ETFs (2) - Foundation: Best liquidity ===
    'SPY',    # S&P 500 ETF - Score: 90, most liquid options in world
    'QQQ',    # Nasdaq 100 ETF - Score: 85, tech exposure

    # === Tech - Mega Cap (6) - Core Holdings ===
    'AAPL',   # Apple - Score: 85, most liquid stock options
    'MSFT',   # Microsoft - Score: 85, enterprise leader
    'GOOGL',  # Google - Score: 85, search/cloud dominant
    'AMZN',   # Amazon - Score: 85, e-commerce/cloud
    'META',   # Meta (Facebook) - Score: 80, social media
    'TSLA',   # Tesla - Score: 80, HIGH volatility = HIGH premiums

    # === Semiconductors (6) - Hot Sector ===
    'NVDA',   # NVIDIA - Score: 75, AI leader, high volume
    'AMD',    # AMD - Score: 80, high beta, good premiums
    'INTC',   # Intel - Score: 85, LOW capital ($3,828), HIGH volume
    'AVGO',   # Broadcom - Score: 85, quality chip maker
    'MU',     # Micron - Score: 80, memory chips, cyclical
    'QCOM',   # Qualcomm - Score: 80, mobile/5G chips

    # === Software & Tech Services (5) ===
    'CRM',    # Salesforce - Score: 85, CRM leader
    'ORCL',   # Oracle - Score: 80, database/cloud
    'CRWD',   # CrowdStrike - Score: 80, cybersecurity
    'CSCO',   # Cisco - Score: 80, networking, LOW capital ($7,063)
    'ANET',   # Arista Networks - Score: 80, cloud networking

    # === Financials (5) - Yield & Stability ===
    'JPM',    # JP Morgan - Score: 80, #1 US bank
    'BAC',    # Bank of America - Score: 80, LOW capital ($5,257)
    'GS',     # Goldman Sachs - Score: 85, investment banking
    'MS',     # Morgan Stanley - Score: 80, wealth management
    'C',      # Citigroup - Score: 80, global bank, affordable

    # === Consumer & Retail (2) ===
    'HD',     # Home Depot - Score: 80, home improvement leader
    'NKE',    # Nike - Score: 80, athletic brand, LOW capital ($6,911)

    # === Healthcare (1) - Defensive ===
    'PFE',    # Pfizer - Score: 75, VERY low capital ($2,476), defensive

    # === Industrials & Aerospace (2) ===
    'BA',     # Boeing - Score: 85, aerospace, volatile = premiums
    'CAT',    # Caterpillar - Score: 80, heavy machinery

    # === Metals & Mining (1) - Diversification ===
    'SCCO',   # Southern Copper - Score: 85, best metals option
]

# WATCHLIST SUMMARY (31 tickers total):
#
# Quality Distribution:
#   Score 85 (Excellent): 11 tickers (SPY, INTC, SCCO, BA, CRM, GS, AAPL, MSFT, GOOGL, AMZN, AVGO)
#   Score 80 (Very Good): 17 tickers (QQQ, META, TSLA, AMD, MU, QCOM, ORCL, CRWD, CSCO, ANET, JPM, BAC, MS, C, HD, NKE, CAT)
#   Score 75 (Good): 3 tickers (NVDA, PFE)
#
# Capital Requirements (per contract):
#   Under $10k: 7 tickers (PFE $2,476, BAC $5,257, NKE $6,911, CSCO $7,063, C $9,878, SCCO $12,934)
#   $10k-$30k: 15 tickers
#   Over $30k: 9 tickers
#   Total for 1 contract each: ~$850,000
#
# Sector Balance:
#   Tech/Semiconductors: 17 (55%) - AAPL, MSFT, GOOGL, AMZN, META, TSLA, NVDA, AMD, INTC, AVGO, MU, QCOM, CRM, ORCL, CRWD, CSCO, ANET
#   Financials: 5 (16%) - JPM, BAC, GS, MS, C
#   Consumer/Retail: 2 (6%) - HD, NKE
#   Healthcare: 1 (3%) - PFE
#   Industrials/Aerospace: 2 (6%) - BA, CAT
#   Metals/Mining: 1 (3%) - SCCO
#   ETFs: 2 (6%) - SPY, QQQ
#   Infrastructure: 1 (3%) - ANET
#
# Liquidity Highlights:
#   Highest Options Volume: TSLA (116/day), INTC (81/day), NVDA (86/day), AMZN (90/day)
#   All tickers have active options markets with good spreads
#
# Run: python research_watchlist.py to evaluate additional tickers

# ============================================================================
# DATA FETCHING SETTINGS
# ============================================================================
NUM_EXPIRATIONS = 6  # Number of expiration dates to fetch per ticker (increased for more options)
DATA_DIR = "data/option_chains"  # Directory for storing options data
PORTFOLIO_DIR = "data/portfolio"  # Directory for portfolio data

# ============================================================================
# COVERED CALL CRITERIA
# ============================================================================
COVERED_CALL_SETTINGS = {
    'min_premium': 0.50,           # Minimum premium per share ($)
    'min_annual_return': 15.0,     # Minimum annualized return (%)
    'max_days': 45,                # Maximum days to expiration
    'min_delta': None,             # Minimum delta (e.g., 0.2) - None to disable
    'max_delta': None,             # Maximum delta (e.g., 0.4) - None to disable
    'top_n': 20,                   # Number of top opportunities to display
}

# Advanced covered call filters
COVERED_CALL_ADVANCED = {
    'min_volume': 10,              # Minimum option volume for liquidity
    'min_open_interest': 50,       # Minimum open interest
    'max_bid_ask_spread_pct': 10,  # Maximum bid-ask spread as % of price
    'prefer_otm': True,            # Prefer out-of-the-money options
    'target_distance_pct': 3.0,    # Target % above current price
}

# ============================================================================
# CAPITAL SETTINGS
# ============================================================================
CAPITAL_SETTINGS = {
    'available_cash': 38000.0,         # Total cash available for CSP strategies ($) - $24k + $27k SGD ≈ $38k USD
    'max_cash_per_position': 30000.0,  # Maximum cash per single CSP position ($) - INCREASED to allow pricier stocks
    'reserve_cash': 3000.0,            # Cash to keep in reserve (not deployed) ($) - emergency fund
    'max_positions': 4,                # Maximum number of simultaneous CSP positions - diversification
    'auto_calculate_contracts': True,  # Auto-calculate max contracts based on cash
}

# ============================================================================
# CASH SECURED PUT CRITERIA - OPTIMIZED FOR 30-45 DTE + EARLY PROFIT TAKING
# ============================================================================
# Strategy: Sell 30-45 DTE puts, close at 50% profit (typically 10-20 days),
#           force close at 21 DTE if target not hit, immediately roll to new position
# Expected: 18-24 trades/year with lower stress than weeklies
# ============================================================================

# Basic Settings - Core filtering criteria
CASH_SECURED_PUT_SETTINGS = {
    'min_premium': 0.50,           # Minimum premium per share ($) - captures more opportunities
    'min_annual_return': 12.0,     # Minimum annualized return (%) - realistic for 30-45 DTE
    'min_days': 20,                # Minimum days to expiration - EXPANDED to capture more expirations
    'max_days': 60,                # Maximum days to expiration - includes next monthly cycle
    'top_n': 20,                   # Number of top opportunities to display
    'use_available_cash': True,    # Filter by available cash from CAPITAL_SETTINGS
}

# Advanced Settings - Risk management and quality filters
CASH_SECURED_PUT_ADVANCED = {
    # Greeks-based filters - Balanced for safety + opportunity
    'min_prob_otm': 65.0,          # Minimum probability OTM (%) - balanced (will improve as time passes)
    'min_delta': None,             # Minimum delta (e.g., -0.4) - None to disable
    'max_delta': -0.30,            # Maximum delta - conservative (further OTM)

    # Liquidity filters - Important for early profit-taking strategy
    'min_volume': 100,             # Minimum option volume - adequate liquidity
    'min_open_interest': 100,      # Minimum open interest - adequate for exit

    # Safety filters
    'target_discount': 5.0,        # Target discount from current price (%)
    'max_strike_pct': 0.98,        # Maximum strike as % of current (2% minimum cushion)
    'min_distance_pct': 2.0,       # Strike must be at least 2% below current
    'quality_tickers_only': False,  # Scan all tickers in watchlist (change to True to restrict to CSP_QUALITY_TICKERS)
    'avoid_itm': True,             # Avoid in-the-money puts
}

# Early Profit-Taking Rules (Manual execution - track your trades!)
EARLY_PROFIT_TAKING = {
    'target_profit_pct': 50,       # Close when you've captured 50% of max profit
    'aggressive_target_pct': 75,   # Close immediately if you hit 75% profit quickly
    'force_close_dte': 21,         # Force close at 21 DTE if targets not hit
    'min_hold_days': 7,            # Don't close before 7 days (let theta work)
    'check_frequency': 'weekly',   # Check positions weekly (not daily)
}

# Example: Sell put for $2.00 premium (45 DTE)
#  - After 10 days: Premium is now $1.00 → Close for 50% profit ($1.00 gain)
#  - After 7 days: Premium is now $0.50 → Close for 75% profit ($1.50 gain)
#  - At 21 DTE: Still $1.50 → Force close anyway (30% profit is fine)
#  - Immediately open new 30-45 DTE position

# Quality tickers for CSP strategy (only trade these if quality_tickers_only = True)
CSP_QUALITY_TICKERS = [
    'AAPL',   # Apple
    'MSFT',   # Microsoft
    'GOOGL',  # Google
    'GOOG',   # Google (Class C)
    'AMZN',   # Amazon
    'META',   # Meta
    'NVDA',   # NVIDIA
    'AMD',    # AMD
    'TSLA',   # Tesla
    'QQQ',    # Nasdaq 100 ETF
    'SPY',    # S&P 500 ETF
    'IWM',    # Russell 2000 ETF
    'DIA',    # Dow Jones ETF
]

# ============================================================================
# WHEEL STRATEGY SETTINGS
# ============================================================================
WHEEL_SETTINGS = {
    'target_entry_discount': 5.0,  # Desired discount to enter position (%)
    'min_annual_return': 20.0,     # Minimum annualized return for puts
    'max_days': 45,                # Maximum days to expiration
    'prefer_quality': True,        # Prefer lower volatility, higher probability
}

# ============================================================================
# DISPLAY SETTINGS
# ============================================================================
DISPLAY_SETTINGS = {
    'table_format': 'grid',        # Options: 'grid', 'simple', 'fancy_grid', 'pipe'
    'decimal_places': 2,           # Decimal places for prices
    'show_greeks': True,           # Show delta, gamma, theta, vega
    'show_volume': True,           # Show volume and open interest
    'color_output': False,         # Colored terminal output (requires termcolor)
}

# ============================================================================
# RISK MANAGEMENT
# ============================================================================
RISK_SETTINGS = {
    'max_position_size': 5.0,      # Maximum % of portfolio per position
    'max_concentration': 20.0,     # Maximum % in single ticker
    'min_diversification': 5,      # Minimum number of different tickers
    'max_leverage': 1.0,           # Maximum leverage (1.0 = no margin)
}

# ============================================================================
# ALERT THRESHOLDS
# ============================================================================
ALERT_SETTINGS = {
    'high_return_threshold': 30.0,     # Flag opportunities above this return
    'high_premium_threshold': 5.0,     # Flag premiums above this amount
    'high_iv_threshold': 0.5,          # Flag IV above 50%
    'low_liquidity_threshold': 100,    # Warn if open interest below this
}

# ============================================================================
# ANALYSIS PREFERENCES
# ============================================================================
ANALYSIS_PREFERENCES = {
    'calculate_probabilities': True,   # Calculate OTM probabilities
    'use_bid_for_selling': True,       # Use bid price for premium (conservative)
    'use_ask_for_buying': True,        # Use ask price for buying (conservative)
    'include_weekly_options': True,    # Include weekly expirations
    'include_quarterly_options': True, # Include quarterly expirations
}

# ============================================================================
# RECOMMENDATIONS SETTINGS
# ============================================================================
RECOMMENDATIONS_SETTINGS = {
    'auto_save': True,                      # Automatically save all recommendations
    'save_directory': 'data/recommendations',  # Where to save recommendations
    'save_excel': True,                     # Also save combined Excel file
    'keep_days': 30,                        # Auto-cleanup after this many days (0 = never)
}

# ============================================================================
# EXPORT SETTINGS
# ============================================================================
EXPORT_SETTINGS = {
    'auto_save': True,             # Automatically save results
    'export_format': 'csv',        # Options: 'csv', 'excel', 'json'
    'include_timestamp': True,     # Add timestamp to filenames
    'save_summary': True,          # Save summary statistics
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_aggressive_cc_settings():
    """Return aggressive covered call settings (higher returns, more risk)"""
    return {
        'min_premium': 1.00,
        'min_annual_return': 30.0,
        'max_days': 30,
        'max_delta': 0.5,
        'top_n': 15,
    }


def get_conservative_cc_settings():
    """Return conservative covered call settings (lower returns, less risk)"""
    return {
        'min_premium': 0.25,
        'min_annual_return': 10.0,
        'max_days': 60,
        'max_delta': 0.2,
        'top_n': 20,
    }


def get_aggressive_csp_settings():
    """Return aggressive cash secured put settings"""
    return {
        'min_premium': 1.00,
        'min_annual_return': 30.0,
        'max_days': 30,
        'min_delta': -0.5,
        'top_n': 15,
    }


def get_conservative_csp_settings():
    """Return conservative cash secured put settings"""
    return {
        'min_premium': 0.25,
        'min_annual_return': 12.0,
        'max_days': 60,
        'max_delta': -0.2,
        'top_n': 20,
    }


def get_monthly_income_settings():
    """Settings optimized for monthly income generation"""
    return {
        'covered_call': {
            'min_premium': 0.50,
            'min_annual_return': 18.0,
            'max_days': 35,
            'max_delta': 0.3,
        },
        'cash_secured_put': {
            'min_premium': 0.50,
            'min_annual_return': 18.0,
            'max_days': 35,
            'max_delta': -0.3,
        }
    }


# ============================================================================
# PRESET WATCHLISTS
# ============================================================================

WATCHLIST_PRESETS = {
    'tech': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'AMD', 'TSLA'],
    'dividend': ['JNJ', 'PG', 'KO', 'PEP', 'MCD', 'WMT', 'VZ', 'T'],
    'etf': ['SPY', 'QQQ', 'IWM', 'DIA', 'VOO', 'VTI', 'EEM', 'GLD'],
    'high_iv': ['TSLA', 'AMD', 'NVDA', 'GME', 'AMC', 'PLTR'],
    'mega_cap': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'BRK.B'],
}


def get_watchlist(preset='default'):
    """
    Get a preset watchlist

    Args:
        preset: 'default', 'tech', 'dividend', 'etf', 'high_iv', or 'mega_cap'

    Returns:
        List of tickers
    """
    if preset == 'default':
        return WATCHLIST
    else:
        return WATCHLIST_PRESETS.get(preset, WATCHLIST)


def get_deployable_cash():
    """
    Calculate cash available for deployment in CSP strategies

    Returns:
        Total cash available minus reserve
    """
    return CAPITAL_SETTINGS['available_cash'] - CAPITAL_SETTINGS['reserve_cash']


def calculate_max_contracts(strike_price):
    """
    Calculate maximum number of contracts affordable at given strike

    Args:
        strike_price: Strike price of the put option

    Returns:
        Maximum number of contracts that can be sold
    """
    cash_per_contract = strike_price * 100  # Each contract = 100 shares
    max_per_position = CAPITAL_SETTINGS['max_cash_per_position']
    deployable = get_deployable_cash()

    # Limit by position size
    contracts_by_position = int(max_per_position / cash_per_contract)

    # Limit by total deployable cash
    contracts_by_total = int(deployable / cash_per_contract)

    return min(contracts_by_position, contracts_by_total)
