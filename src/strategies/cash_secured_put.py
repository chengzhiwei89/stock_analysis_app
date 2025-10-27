"""
Cash Secured Put Strategy Analyzer
Analyzes options for cash secured put opportunities
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from ..data.greeks_calculator import GreeksCalculator


class CashSecuredPutAnalyzer:
    """Analyze cash secured put opportunities"""

    def __init__(self):
        self.greeks_calc = GreeksCalculator()

    def _calculate_effective_price(self, options_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate effective price for selling options
        Uses bid when market is open, lastPrice as fallback when market closed (bid=0)

        Args:
            options_df: DataFrame with bid, ask, lastPrice columns

        Returns:
            DataFrame with added effective_price and price_source columns
        """
        options_df = options_df.copy()

        # For selling options (CSP), we receive the bid price
        # If bid = 0 (market closed), use lastPrice as estimate
        # If both are 0, use ask/2 as very conservative estimate

        def get_price(row):
            if pd.notna(row['bid']) and row['bid'] > 0:
                return row['bid'], 'bid'
            elif pd.notna(row['lastPrice']) and row['lastPrice'] > 0:
                return row['lastPrice'], 'lastPrice'
            elif pd.notna(row['ask']) and row['ask'] > 0:
                return row['ask'] * 0.5, 'ask/2'  # Very conservative
            else:
                return 0, 'none'

        results = options_df.apply(get_price, axis=1, result_type='expand')
        options_df['effective_price'] = results[0]
        options_df['price_source'] = results[1]

        return options_df

    def analyze_cash_secured_puts(self, options_df: pd.DataFrame,
                                  min_premium: float = 0.5,
                                  min_annual_return: float = 10.0,
                                  min_days: int = 0,
                                  max_days: int = 60,
                                  min_prob_otm: Optional[float] = None,
                                  min_volume: Optional[int] = None,
                                  quality_tickers: Optional[List[str]] = None,
                                  min_delta: Optional[float] = None,
                                  max_delta: Optional[float] = None,
                                  available_cash: Optional[float] = None,
                                  max_cash_per_position: Optional[float] = None) -> pd.DataFrame:
        """
        Analyze cash secured put opportunities

        Args:
            options_df: DataFrame with options data
            min_premium: Minimum premium to collect ($ per share)
            min_annual_return: Minimum annualized return (%)
            min_days: Minimum days to expiration (avoid very short options)
            max_days: Maximum days to expiration
            min_prob_otm: Minimum probability of expiring OTM (% for safer trades)
            min_volume: Minimum option volume for liquidity
            quality_tickers: List of quality tickers to filter by (None = all)
            min_delta: Minimum delta magnitude (e.g., -0.4)
            max_delta: Maximum delta magnitude (e.g., -0.2 for safer puts)
            available_cash: Total cash available for CSP strategies (None to disable filtering)
            max_cash_per_position: Maximum cash per position (None to use available_cash)

        Returns:
            DataFrame with analyzed cash secured put opportunities
        """
        if options_df.empty:
            return pd.DataFrame()

        # Filter for puts only
        puts = options_df[options_df['option_type'] == 'put'].copy()

        # Calculate effective price (handles market closed scenario)
        puts = self._calculate_effective_price(puts)

        if puts.empty:
            return pd.DataFrame()

        # Filter by quality tickers if specified
        if quality_tickers is not None:
            puts = puts[puts['ticker'].isin(quality_tickers)]

        if puts.empty:
            return pd.DataFrame()

        # Enrich with calculated metrics
        puts = self.greeks_calc.enrich_option_data(puts)

        # Filter by criteria (use effective_price instead of bid)
        filter_conditions = [
            (puts['days_to_expiration'] <= max_days),
            (puts['days_to_expiration'] >= min_days),
            (puts['effective_price'] >= min_premium)
        ]

        # Add volume filter if specified
        if min_volume is not None and 'volume' in puts.columns:
            filter_conditions.append(puts['volume'] >= min_volume)

        # Combine all filters
        filtered = puts[pd.concat(filter_conditions, axis=1).all(axis=1)].copy()

        if filtered.empty:
            return pd.DataFrame()

        # Calculate cash secured put specific metrics
        # Capital required = strike price * 100 (cash to secure)
        filtered['capital_required'] = filtered['strike']

        # Premium received = effective_price (bid when market open, lastPrice when closed)
        filtered['premium_received'] = filtered['effective_price']

        # Keep original bid/ask/lastPrice for reference
        filtered['original_bid'] = filtered['bid']
        filtered['original_ask'] = filtered['ask']
        filtered['original_lastPrice'] = filtered['lastPrice']

        # Keep option_type for downstream analysis
        if 'option_type' not in filtered.columns:
            filtered['option_type'] = 'put'

        # Effective purchase price if assigned
        filtered['net_purchase_price'] = filtered['strike'] - filtered['premium_received']
        filtered['discount_from_current'] = (
            (filtered['current_stock_price'] - filtered['net_purchase_price']) /
            filtered['current_stock_price'] * 100
        )

        # Return on capital (based on strike price as capital)
        filtered['income_return'] = (filtered['premium_received'] / filtered['strike']) * 100

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

        # Filter by delta if specified (note: put deltas are negative)
        if min_delta is not None and 'delta' in filtered.columns:
            filtered = filtered[filtered['delta'] >= min_delta]  # e.g., >= -0.4
        if max_delta is not None and 'delta' in filtered.columns:
            filtered = filtered[filtered['delta'] <= max_delta]  # e.g., <= -0.2

        # Filter by probability OTM if specified
        if min_prob_otm is not None and 'prob_otm' in filtered.columns:
            filtered = filtered[filtered['prob_otm'] >= min_prob_otm]

        if filtered.empty:
            return pd.DataFrame()

        # Filter by available cash if specified
        if available_cash is not None:
            # Calculate cash required per contract (strike * 100)
            filtered['cash_per_contract'] = filtered['strike'] * 100

            # Determine max affordable contracts per position
            if max_cash_per_position is not None:
                filtered['max_affordable_contracts'] = (max_cash_per_position / filtered['cash_per_contract']).apply(int)
            else:
                filtered['max_affordable_contracts'] = (available_cash / filtered['cash_per_contract']).apply(int)

            # Filter out options where we can't afford even 1 contract
            filtered = filtered[filtered['max_affordable_contracts'] >= 1]

            # Calculate total capital needed and potential income for max contracts
            filtered['total_capital_required'] = filtered['cash_per_contract'] * filtered['max_affordable_contracts']
            filtered['total_premium_received'] = filtered['premium_received'] * filtered['max_affordable_contracts'] * 100

        if filtered.empty:
            return pd.DataFrame()

        # Calculate cushion (how far price can drop before loss)
        filtered['cushion'] = (filtered['net_purchase_price'] / filtered['current_stock_price']) * 100 - 100

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
                            min_days: int = 0,
                            max_days: int = 45,
                            min_prob_otm: Optional[float] = None,
                            min_volume: Optional[int] = None,
                            quality_tickers: Optional[List[str]] = None,
                            min_delta: Optional[float] = None,
                            max_delta: Optional[float] = None,
                            top_n: int = 20,
                            available_cash: Optional[float] = None,
                            max_cash_per_position: Optional[float] = None) -> pd.DataFrame:
        """
        Get top cash secured put opportunities

        Args:
            options_df: DataFrame with options data
            min_premium: Minimum premium
            min_annual_return: Minimum annualized return
            min_days: Minimum days to expiration
            max_days: Maximum days to expiration
            min_prob_otm: Minimum probability of expiring OTM
            min_volume: Minimum option volume
            quality_tickers: List of quality tickers to filter by
            min_delta: Minimum delta magnitude
            max_delta: Maximum delta magnitude
            top_n: Number of top opportunities to return
            available_cash: Total cash available for CSP strategies
            max_cash_per_position: Maximum cash per position

        Returns:
            DataFrame with top opportunities
        """
        results = self.analyze_cash_secured_puts(
            options_df,
            min_premium=min_premium,
            min_annual_return=min_annual_return,
            min_days=min_days,
            max_days=max_days,
            min_prob_otm=min_prob_otm,
            min_volume=min_volume,
            quality_tickers=quality_tickers,
            min_delta=min_delta,
            max_delta=max_delta,
            available_cash=available_cash,
            max_cash_per_position=max_cash_per_position
        )

        if results.empty:
            return pd.DataFrame()

        # Select relevant columns
        columns = [
            'ticker', 'current_stock_price', 'strike', 'expiration',
            'days_to_expiration', 'bid', 'ask', 'lastPrice',
            'premium_received', 'price_source', 'original_bid', 'original_ask', 'original_lastPrice',
            'annual_return', 'monthly_return',
            'income_return', 'net_purchase_price', 'discount_from_current',
            'cushion', 'distance_pct',
            'prob_otm', 'delta', 'impliedVolatility',
            'volume', 'openInterest', 'moneyness_class',
            'risk_reward_score', 'option_type',
            'max_affordable_contracts', 'total_capital_required', 'total_premium_received'
        ]

        # Filter to only include columns that exist
        available_columns = [col for col in columns if col in results.columns]

        return results[available_columns].head(top_n)

    def summarize_by_ticker(self, analyzed_df: pd.DataFrame) -> pd.DataFrame:
        """
        Summarize cash secured put opportunities by ticker

        Args:
            analyzed_df: DataFrame from analyze_cash_secured_puts

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
            'discount_from_current': 'mean',
            'prob_otm': 'mean' if 'prob_otm' in analyzed_df.columns else 'count'
        }).round(2)

        summary.columns = ['stock_price', 'num_opportunities', 'avg_annual_return',
                          'max_annual_return', 'avg_premium', 'max_premium',
                          'avg_days', 'avg_discount', 'avg_prob_otm']

        return summary.sort_values('max_annual_return', ascending=False)

    def compare_expirations(self, options_df: pd.DataFrame, ticker: str,
                          strike_range: tuple = (0.90, 1.00)) -> pd.DataFrame:
        """
        Compare cash secured put opportunities across different expirations

        Args:
            options_df: DataFrame with options data
            ticker: Ticker to analyze
            strike_range: Tuple of (min_multiplier, max_multiplier) for strikes
                         e.g., (0.90, 1.00) = strikes at or below current price

        Returns:
            DataFrame comparing different expirations
        """
        ticker_data = options_df[
            (options_df['ticker'] == ticker) &
            (options_df['option_type'] == 'put')
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
                row['strike'],
                row['days_to_expiration']
            ), axis=1
        )

        ticker_data['net_purchase_price'] = ticker_data['strike'] - ticker_data['premium_received']
        ticker_data['discount_from_current'] = (
            (ticker_data['current_stock_price'] - ticker_data['net_purchase_price']) /
            ticker_data['current_stock_price'] * 100
        )

        # Select columns
        result = ticker_data[[
            'expiration', 'days_to_expiration', 'strike', 'distance_pct',
            'bid', 'annual_return', 'net_purchase_price', 'discount_from_current',
            'delta', 'prob_otm', 'volume', 'openInterest'
        ]].sort_values('days_to_expiration')

        return result

    def find_wheel_candidates(self, options_df: pd.DataFrame,
                            target_entry_discount: float = 5.0,
                            min_annual_return: float = 20.0,
                            max_days: int = 45,
                            available_cash: Optional[float] = None,
                            max_cash_per_position: Optional[float] = None) -> pd.DataFrame:
        """
        Find good candidates for the Wheel strategy
        (selling puts to get assigned, then selling calls)

        Args:
            options_df: DataFrame with options data
            target_entry_discount: Desired discount from current price (%)
            min_annual_return: Minimum annualized return
            max_days: Maximum days to expiration
            available_cash: Total cash available for CSP strategies
            max_cash_per_position: Maximum cash per position

        Returns:
            DataFrame with wheel strategy candidates
        """
        results = self.analyze_cash_secured_puts(
            options_df,
            min_premium=0.5,
            min_annual_return=min_annual_return,
            max_days=max_days,
            available_cash=available_cash,
            max_cash_per_position=max_cash_per_position
        )

        if results.empty:
            return pd.DataFrame()

        # Filter for good entry prices (at discount)
        wheel_candidates = results[
            results['discount_from_current'] >= target_entry_discount
        ].copy()

        # Add quality score
        wheel_candidates['wheel_score'] = (
            wheel_candidates['annual_return'] * 0.4 +
            wheel_candidates['discount_from_current'] * 0.3 +
            (wheel_candidates['prob_otm'] if 'prob_otm' in wheel_candidates.columns else 50) * 0.3
        )

        return wheel_candidates.sort_values('wheel_score', ascending=False)
