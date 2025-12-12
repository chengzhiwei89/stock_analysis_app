"""
Market Hours Utility
Checks if US stock market is currently open
"""
from datetime import datetime, time
import pytz
from typing import Tuple


def is_market_open() -> bool:
    """
    Check if US stock market is currently open

    Market hours: 9:30 AM - 4:00 PM ET, Monday-Friday (excluding holidays)

    Returns:
        True if market is open, False otherwise
    """
    # Get current time in Eastern Time
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)

    # Check if it's a weekday (Monday=0, Sunday=6)
    if now_et.weekday() >= 5:  # Saturday or Sunday
        return False

    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = time(9, 30)
    market_close = time(16, 0)
    current_time = now_et.time()

    # Check if current time is within market hours
    if market_open <= current_time <= market_close:
        # TODO: Add holiday checking (NYSE holidays)
        # For now, we assume weekdays = trading days
        return True

    return False


def get_market_status() -> Tuple[str, str]:
    """
    Get detailed market status information

    Returns:
        Tuple of (status, description) where:
        - status: 'OPEN', 'CLOSED', 'PRE_MARKET', 'AFTER_HOURS'
        - description: Human-readable description
    """
    et_tz = pytz.timezone('US/Eastern')
    now_et = datetime.now(et_tz)

    # Check if weekend
    if now_et.weekday() >= 5:
        return 'CLOSED', 'Market closed (Weekend)'

    # Define time periods
    current_time = now_et.time()
    pre_market_start = time(4, 0)
    market_open = time(9, 30)
    market_close = time(16, 0)
    after_hours_end = time(20, 0)

    # Determine status
    if market_open <= current_time <= market_close:
        return 'OPEN', 'Market is OPEN (9:30 AM - 4:00 PM ET)'
    elif pre_market_start <= current_time < market_open:
        return 'PRE_MARKET', 'Pre-market hours (4:00 AM - 9:30 AM ET)'
    elif market_close < current_time <= after_hours_end:
        return 'AFTER_HOURS', 'After-hours trading (4:00 PM - 8:00 PM ET)'
    else:
        return 'CLOSED', 'Market closed (After 8:00 PM or before 4:00 AM ET)'


if __name__ == '__main__':
    # Quick test
    status, description = get_market_status()
    print(f"Market Status: {status}")
    print(f"Description: {description}")
    print(f"Is Market Open: {is_market_open()}")
