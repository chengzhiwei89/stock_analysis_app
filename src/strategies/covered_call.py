"""
Covered Call Strategy Analyzer
Analyzes options for covered call opportunities
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from ..data.greeks_calculator import GreeksCalculator


class CoveredCallAnalyzer:
    """Analyze covered call opportunities"""

    def __init__(self):
        self.greeks_calc = GreeksCalculator()

    def analyze_covered_calls(self, options_df: pd.DataFrame,
                              min_premium: float = 0.5,
                              min_annual_return: float = 10.0,
                              max_days: int = 60,
                              min_delta: Optional[float] = None,
                              max_delta: Optional[float] = None) -> pd.DataFrame:
        """
        Analyze covered call opportunities

        Args:
            options_df: DataFrame with options data
            min_premium: Minimum premium to collect ($ per share)
            min_annual_return: Minimum annualized return (%)
            max_days: Maximum days to expiration
            min_delta: Minimum delta (e.g., 0.2)
            max_delta: Maximum delta (e.g., 0.4 for ~60% OTM probability)

        Returns:
            DataFrame with analyzed covered call opportunities
        """
        if options_df.empty:
            return pd.DataFrame()

        # Filter for calls only
        calls = options_df[options_df['option_type'] == 'call'].copy()

        if calls.empty:
            return pd.DataFrame()

        # Enrich with calculated metrics
        calls = self.greeks_calc.enrich_option_data(calls)

        # Filter for realistic strikes (reject extremely OTM strikes)
        # For covered calls, typically want strikes within 0-50% above current price
        # Anything more than 100% OTM is unrealistic for normal covered calls
        current_price = calls['current_stock_price'].iloc[0] if len(calls) > 0 else 0
        if current_price > 0:
            max_strike = current_price * 1.5  # Max 50% OTM
            calls = calls[
                (calls['strike'] >= current_price * 0.95) &  # At least 5% ITM
                (calls['strike'] <= max_strike)
            ].copy()

        if calls.empty:
            return pd.DataFrame()

        # Use lastPrice as fallback when bid is not available (market closed)
        calls['price_source'] = calls['bid'].apply(lambda x: 'bid' if x > 0 else 'lastPrice')
        calls['effective_price'] = calls.apply(
            lambda row: row['bid'] if row['bid'] > 0 else row['lastPrice'],
            axis=1
        )

        # Filter by criteria
        filtered = calls[
            (calls['days_to_expiration'] <= max_days) &
            (calls['days_to_expiration'] > 0) &
            (calls['effective_price'] >= min_premium)  # Use effective price
        ].copy()

        if filtered.empty:
            return pd.DataFrame()

        # Calculate covered call specific metrics
        # Capital required = stock price (we own the stock)
        filtered['capital_required'] = filtered['current_stock_price']

        # Premium received = effective price (bid or lastPrice)
        filtered['premium_received'] = filtered['effective_price']

        # Total return if called away
        filtered['max_profit'] = (filtered['strike'] - filtered['current_stock_price']) + filtered['premium_received']
        filtered['max_profit_pct'] = (filtered['max_profit'] / filtered['current_stock_price']) * 100

        # Return if not called (keep premium + stock)
        filtered['income_return'] = (filtered['premium_received'] / filtered['current_stock_price']) * 100

        # Annualized and monthly returns
        filtered['annual_return'] = filtered.apply(
            lambda row: self.greeks_calc.calculate_annualized_return(
                row['premium_received'],
                row['capital_required'],
                row['days_to_expiration']
            ), axis=1
        )

        filtered['monthly_return'] = filtered.apply(
            lambda row: self.greeks_calc.calculate_monthly_return(
                row['premium_received'],
                row['capital_required'],
                row['days_to_expiration']
            ), axis=1
        )

        # Filter by return
        filtered = filtered[filtered['annual_return'] >= min_annual_return]

        # Filter by delta if specified
        if min_delta is not None and 'delta' in filtered.columns:
            filtered = filtered[filtered['delta'] >= min_delta]
        if max_delta is not None and 'delta' in filtered.columns:
            filtered = filtered[filtered['delta'] <= max_delta]

        # Calculate downside protection
        filtered['downside_protection'] = (filtered['premium_received'] / filtered['current_stock_price']) * 100

        # Breakeven
        filtered['breakeven_price'] = filtered['current_stock_price'] - filtered['premium_received']
        filtered['breakeven_pct'] = ((filtered['breakeven_price'] - filtered['current_stock_price']) /
                                     filtered['current_stock_price']) * 100

        # Risk/reward score (higher is better)
        filtered['risk_reward_score'] = (
            filtered['annual_return'] * filtered['prob_otm'] / 100
            if 'prob_otm' in filtered.columns else filtered['annual_return']
        )

        # Sort by risk-reward score
        filtered = filtered.sort_values('risk_reward_score', ascending=False)

        return filtered

    def get_top_opportunities(self, options_df: pd.DataFrame,
                            min_premium: float = 0.5,
                            min_annual_return: float = 15.0,
                            max_days: int = 45,
                            top_n: int = 20) -> pd.DataFrame:
        """
        Get top covered call opportunities

        Args:
            options_df: DataFrame with options data
            min_premium: Minimum premium
            min_annual_return: Minimum annualized return
            max_days: Maximum days to expiration
            top_n: Number of top opportunities to return

        Returns:
            DataFrame with top opportunities
        """
        results = self.analyze_covered_calls(
            options_df,
            min_premium=min_premium,
            min_annual_return=min_annual_return,
            max_days=max_days
        )

        if results.empty:
            return pd.DataFrame()

        # Select relevant columns
        columns = [
            'ticker', 'current_stock_price', 'strike', 'expiration',
            'days_to_expiration', 'bid', 'ask', 'lastPrice',
            'premium_received', 'annual_return', 'monthly_return',
            'income_return', 'max_profit', 'max_profit_pct',
            'downside_protection', 'distance_pct',
            'prob_otm', 'delta', 'impliedVolatility',
            'volume', 'openInterest', 'moneyness_class',
            'risk_reward_score'
        ]

        # Filter to only include columns that exist
        available_columns = [col for col in columns if col in results.columns]

        return results[available_columns].head(top_n)

    def summarize_by_ticker(self, analyzed_df: pd.DataFrame) -> pd.DataFrame:
        """
        Summarize covered call opportunities by ticker

        Args:
            analyzed_df: DataFrame from analyze_covered_calls

        Returns:
            Summary DataFrame grouped by ticker
        """
        if analyzed_df.empty:
            return pd.DataFrame()

        summary = analyzed_df.groupby('ticker').agg({
            'current_stock_price': 'first',
            'strike': 'count',
            'annual_return': ['mean', 'max'],
            'premium_received': ['mean', 'max'],
            'days_to_expiration': 'mean',
            'prob_otm': 'mean' if 'prob_otm' in analyzed_df.columns else 'count'
        }).round(2)

        summary.columns = ['stock_price', 'num_opportunities', 'avg_annual_return',
                          'max_annual_return', 'avg_premium', 'max_premium',
                          'avg_days', 'avg_prob_otm']

        return summary.sort_values('max_annual_return', ascending=False)

    def compare_expirations(self, options_df: pd.DataFrame, ticker: str,
                          strike_range: tuple = (0.95, 1.05)) -> pd.DataFrame:
        """
        Compare covered call opportunities across different expirations

        Args:
            options_df: DataFrame with options data
            ticker: Ticker to analyze
            strike_range: Tuple of (min_multiplier, max_multiplier) for strikes
                         e.g., (0.95, 1.05) = strikes within 5% of current price

        Returns:
            DataFrame comparing different expirations
        """
        ticker_data = options_df[
            (options_df['ticker'] == ticker) &
            (options_df['option_type'] == 'call')
        ].copy()

        if ticker_data.empty:
            return pd.DataFrame()

        # Enrich data
        ticker_data = self.greeks_calc.enrich_option_data(ticker_data)

        # Filter strikes
        current_price = ticker_data['current_stock_price'].iloc[0]
        min_strike = current_price * strike_range[0]
        max_strike = current_price * strike_range[1]

        ticker_data = ticker_data[
            (ticker_data['strike'] >= min_strike) &
            (ticker_data['strike'] <= max_strike)
        ]

        # Calculate returns
        ticker_data['premium_received'] = ticker_data['bid']
        ticker_data['annual_return'] = ticker_data.apply(
            lambda row: self.greeks_calc.calculate_annualized_return(
                row['premium_received'],
                row['current_stock_price'],
                row['days_to_expiration']
            ), axis=1
        )

        # Select columns
        result = ticker_data[[
            'expiration', 'days_to_expiration', 'strike', 'distance_pct',
            'bid', 'annual_return', 'delta', 'prob_otm', 'volume', 'openInterest'
        ]].sort_values('days_to_expiration')

        return result
