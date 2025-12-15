"""
Greeks Calculator
Calculate additional option Greeks and metrics
"""
import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime


class GreeksCalculator:
    """Calculate option Greeks and other metrics"""

    @staticmethod
    def calculate_days_to_expiration(expiration_date: str) -> int:
        """
        Calculate days to expiration

        Args:
            expiration_date: Expiration date string (YYYY-MM-DD)

        Returns:
            Number of days to expiration
        """
        try:
            exp_date = pd.to_datetime(expiration_date)
            today = pd.Timestamp.now()
            return max(0, (exp_date - today).days)
        except:
            return 0

    @staticmethod
    def calculate_annualized_return(premium: float, capital: float, days: int) -> float:
        """
        Calculate annualized return on capital

        Args:
            premium: Option premium received
            capital: Capital required (stock price for covered call, strike for CSP)
            days: Days to expiration

        Returns:
            Annualized return as percentage
        """
        if capital <= 0 or days <= 0:
            return 0.0

        daily_return = premium / capital
        annualized = (daily_return * 365 / days) * 100
        return annualized

    @staticmethod
    def calculate_monthly_return(premium: float, capital: float, days: int) -> float:
        """
        Calculate monthly return on capital

        Args:
            premium: Option premium received
            capital: Capital required
            days: Days to expiration

        Returns:
            Monthly return as percentage
        """
        if capital <= 0 or days <= 0:
            return 0.0

        daily_return = premium / capital
        monthly = (daily_return * 30 / days) * 100
        return monthly

    @staticmethod
    def calculate_breakeven(stock_price: float, premium: float, option_type: str) -> float:
        """
        Calculate breakeven price

        Args:
            stock_price: Current stock price
            premium: Option premium
            option_type: 'call' or 'put'

        Returns:
            Breakeven price
        """
        if option_type.lower() == 'call':
            return stock_price - premium  # For covered call
        else:
            return stock_price - premium  # For cash secured put

    @staticmethod
    def calculate_probability_otm(current_price: float, strike: float,
                                  implied_vol: float, days: int, option_type: str) -> float:
        """
        Calculate probability of option expiring out of the money

        Args:
            current_price: Current stock price
            strike: Strike price
            implied_vol: Implied volatility (as decimal, e.g., 0.25 for 25%)
            days: Days to expiration
            option_type: 'call' or 'put'

        Returns:
            Probability as percentage
        """
        if days <= 0:
            return 0.0

        try:
            # Sanity check on IV - yfinance often returns bad IV data for short-dated options
            # If IV is unreasonably low (< 10%), use a reasonable default
            effective_iv = implied_vol
            if implied_vol < 0.10:  # Less than 10% IV is unrealistic for most stocks
                # Use a moderate default IV of 45% for tech stocks
                # This is a reasonable estimate when data is missing/bad
                effective_iv = 0.45

            time_to_expiration = days / 365.0
            d1 = (np.log(current_price / strike) + (0.5 * effective_iv ** 2) * time_to_expiration) / \
                 (effective_iv * np.sqrt(time_to_expiration))

            if option_type.lower() == 'call':
                # Probability of being below strike at expiration
                prob_otm = norm.cdf(-d1) * 100
            else:
                # Probability of being above strike at expiration
                prob_otm = norm.cdf(d1) * 100

            return prob_otm
        except:
            return 0.0

    @staticmethod
    def enrich_option_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add calculated metrics to option data

        Args:
            df: DataFrame with option data

        Returns:
            Enhanced DataFrame with additional metrics
        """
        if df.empty:
            return df

        df = df.copy()

        # Calculate days to expiration
        df['days_to_expiration'] = df['expiration'].apply(
            GreeksCalculator.calculate_days_to_expiration
        )

        # Bid-Ask spread
        df['bid_ask_spread'] = df['ask'] - df['bid']
        df['bid_ask_spread_pct'] = (df['bid_ask_spread'] / df['lastPrice']) * 100

        # Moneyness
        df['moneyness'] = df['strike'] / df['current_stock_price']
        df['distance_from_price'] = df['strike'] - df['current_stock_price']
        df['distance_pct'] = (df['distance_from_price'] / df['current_stock_price']) * 100

        # ITM/OTM/ATM classification
        def classify_option(row):
            if row['option_type'] == 'call':
                if row['strike'] < row['current_stock_price']:
                    return 'ITM'
                elif row['strike'] > row['current_stock_price']:
                    return 'OTM'
                else:
                    return 'ATM'
            else:  # put
                if row['strike'] > row['current_stock_price']:
                    return 'ITM'
                elif row['strike'] < row['current_stock_price']:
                    return 'OTM'
                else:
                    return 'ATM'

        df['moneyness_class'] = df.apply(classify_option, axis=1)

        # Probability of OTM
        if 'impliedVolatility' in df.columns:
            df['prob_otm'] = df.apply(
                lambda row: GreeksCalculator.calculate_probability_otm(
                    row['current_stock_price'],
                    row['strike'],
                    row['impliedVolatility'],
                    row['days_to_expiration'],
                    row['option_type']
                ), axis=1
            )

        # Effective premium (mid price)
        df['mid_price'] = (df['bid'] + df['ask']) / 2

        return df
