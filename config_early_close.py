"""
Configuration for Early Profit-Taking Strategy
Sell 45-60 DTE options, close at 50-75% profit
"""

# ============================================================================
# WATCHLIST - Focus on liquid stocks for easy closing
# ============================================================================
WATCHLIST = [
    'AAPL',   # Apple - very liquid
    'MSFT',   # Microsoft - very liquid
    'NVDA',   # NVIDIA - very liquid
    'GOOGL',  # Google - very liquid
    'AMZN',   # Amazon - very liquid
    'META',   # Meta - very liquid
    'QQQ',    # Nasdaq ETF - extremely liquid
    'SPY',    # S&P 500 ETF - extremely liquid
]

# ============================================================================
# DATA FETCHING - Get more expirations for 45-60 day range
# ============================================================================
NUM_EXPIRATIONS = 8  # Increased to find more 45-60 DTE options
DATA_DIR = "data/option_chains"
PORTFOLIO_DIR = "data/portfolio"

# ============================================================================
# CAPITAL SETTINGS
# ============================================================================
CAPITAL_SETTINGS = {
    'available_cash': 27000.0,
    'max_cash_per_position': 27000.0,
    'reserve_cash': 5000.0,
    'max_positions': 3,
    'auto_calculate_contracts': True,
}

# ============================================================================
# CASH SECURED PUT CRITERIA - EARLY CLOSE STRATEGY
# ============================================================================
CASH_SECURED_PUT_SETTINGS = {
    'min_premium': 1.00,           # Higher premium (longer DTE = bigger premiums)
    'min_annual_return': 12.0,     # Lower threshold - you'll beat this with early close!
    'min_days': 40,                # Target 45-60 day sweet spot
    'max_days': 65,                # Include up to 65 days
    'min_prob_otm': 65.0,          # Moderate - you'll close before it matters
    'min_delta': None,
    'max_delta': -0.35,            # Allow slightly higher delta (will improve as stock moves)
    'top_n': 20,
    'use_available_cash': True,
}

# Advanced filters - LIQUIDITY IS CRITICAL for early closing
CASH_SECURED_PUT_ADVANCED = {
    'min_volume': 500,             # MUST HAVE: Need volume to close with tight spreads
    'min_open_interest': 500,      # MUST HAVE: Need OI to close easily
    'target_discount': 5.0,
    'max_strike_pct': 1.0,
    'quality_tickers_only': True,
    'avoid_itm': True,
}

# Quality tickers for CSP strategy
CSP_QUALITY_TICKERS = [
    'AAPL',   # Excellent liquidity
    'MSFT',   # Excellent liquidity
    'GOOGL',  # Good liquidity
    'AMZN',   # Good liquidity
    'META',   # Good liquidity
    'NVDA',   # Excellent liquidity
    'QQQ',    # Best liquidity (ETF)
    'SPY',    # Best liquidity (ETF)
    'IWM',    # Good liquidity (ETF)
]

# ============================================================================
# EARLY CLOSE STRATEGY SETTINGS - NEW
# ============================================================================
EARLY_CLOSE_SETTINGS = {
    'profit_target_50': 0.50,      # Close at 50% max profit
    'profit_target_75': 0.75,      # Close at 75% max profit (if reached quickly)
    'max_dte_hold': 21,            # Force close at 21 DTE if target not hit
    'min_dte_avoid': 7,            # Never hold into final week
    'track_positions': True,       # Keep log of all trades
    'auto_alerts': True,           # Generate profit target alerts
}

# ============================================================================
# DISPLAY SETTINGS
# ============================================================================
DISPLAY_SETTINGS = {
    'table_format': 'grid',
    'decimal_places': 2,
    'show_greeks': True,
    'show_volume': True,
    'color_output': False,
}

# ============================================================================
# RECOMMENDATIONS SETTINGS
# ============================================================================
RECOMMENDATIONS_SETTINGS = {
    'auto_save': True,
    'save_directory': 'data/recommendations',
    'save_excel': True,
    'keep_days': 30,
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_profit_target_price(sold_price: float, target_pct: float = 0.50) -> float:
    """
    Calculate the option price at which you should close for target profit

    Args:
        sold_price: Price you sold the option for (e.g., $6.00)
        target_pct: Target profit percentage (0.50 = 50%, 0.75 = 75%)

    Returns:
        Price to buy back option (e.g., $3.00 for 50% profit on $6.00)

    Example:
        Sold put for $6.00, want 50% profit:
        calculate_profit_target_price(6.00, 0.50) = $3.00

        Sold put for $6.00, want 75% profit:
        calculate_profit_target_price(6.00, 0.75) = $1.50
    """
    profit_amount = sold_price * target_pct
    close_price = sold_price - profit_amount
    return close_price


def generate_close_alert_text(ticker: str, strike: float, expiration: str,
                               sold_price: float, target_50: float, target_75: float) -> str:
    """
    Generate alert text for broker alerts

    Returns text you can paste into broker price alerts
    """
    alert_text = f"""
    POSITION: {ticker} ${strike} PUT {expiration}
    SOLD FOR: ${sold_price:.2f}

    PROFIT TARGETS:
    50% Profit: Close when option reaches ${target_50:.2f}
    75% Profit: Close when option reaches ${target_75:.2f}

    SET ALERTS AT:
    - ${target_50:.2f} (50% profit - good exit)
    - ${target_75:.2f} (75% profit - excellent exit)

    AUTO-CLOSE DATE: {21} days from now (21 DTE rule)
    """
    return alert_text


def print_trade_plan(ticker: str, strike: float, sold_price: float, days: int):
    """
    Print a trade plan for early close strategy
    """
    target_50 = calculate_profit_target_price(sold_price, 0.50)
    target_75 = calculate_profit_target_price(sold_price, 0.75)

    max_profit = sold_price * 100  # Per contract
    profit_50 = max_profit * 0.50
    profit_75 = max_profit * 0.75

    print(f"\n{'='*80}")
    print(f"TRADE PLAN: {ticker} ${strike} PUT ({days} DTE)")
    print(f"{'='*80}")
    print(f"\nOPENING:")
    print(f"  Action: Sell to Open")
    print(f"  Premium: ${sold_price:.2f} per share (${max_profit:.0f} total)")
    print(f"  Days: {days} DTE")

    print(f"\nPROFIT TARGETS:")
    print(f"  50% Target: ${target_50:.2f} → Profit: ${profit_50:.0f}")
    print(f"  75% Target: ${target_75:.2f} → Profit: ${profit_75:.0f}")
    print(f"  100% Target: $0.00 → Profit: ${max_profit:.0f} (don't wait for this!)")

    print(f"\nMANAGEMENT RULES:")
    print(f"  1. Close IMMEDIATELY if option reaches ${target_50:.2f} (50% profit)")
    print(f"  2. Close IMMEDIATELY if option reaches ${target_75:.2f} (75% profit)")
    print(f"  3. Force close at {days - 21} days elapsed (21 DTE remaining)")
    print(f"  4. NEVER hold into final 7 days")

    print(f"\nEXPECTED TIMELINE:")
    print(f"  Typical hold: 10-20 days to reach 50% profit")
    print(f"  If stock moves in your favor: 5-15 days to reach 75% profit")
    print(f"  Maximum hold: {days - 21} days (then force close)")

    print(f"\n{'='*80}\n")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: You sold AAPL $180 put for $6.00
    print("\nEXAMPLE: AAPL $180 PUT EARLY CLOSE STRATEGY")
    print_trade_plan(ticker='AAPL', strike=180, sold_price=6.00, days=45)

    # Calculate profit targets
    target_50 = calculate_profit_target_price(6.00, 0.50)
    target_75 = calculate_profit_target_price(6.00, 0.75)

    print(f"\nSET BROKER ALERTS:")
    print(f"  Alert 1: AAPL 180 PUT at ${target_50:.2f} (50% profit)")
    print(f"  Alert 2: AAPL 180 PUT at ${target_75:.2f} (75% profit)")
