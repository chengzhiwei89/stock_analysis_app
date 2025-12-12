"""
Capital Calculator
Calculate deployed and available capital for position management
"""
import sys
import os
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config


class CapitalCalculator:
    """Calculate capital deployment and availability for options positions"""

    def __init__(self):
        """Initialize capital calculator with config settings"""
        self.available_cash = config.CAPITAL_SETTINGS['available_cash']
        self.max_cash_per_position = config.CAPITAL_SETTINGS['max_cash_per_position']
        self.reserve_cash = config.CAPITAL_SETTINGS['reserve_cash']
        self.max_positions = config.CAPITAL_SETTINGS['max_positions']

    def calculate_deployed_capital(self, portfolio_manager) -> Dict:
        """
        Calculate total capital currently deployed in positions

        Args:
            portfolio_manager: PortfolioManager instance

        Returns:
            Dictionary with:
            - total_deployed: Total capital tied up in positions
            - by_strategy: Breakdown by strategy (CSP, CC)
            - by_ticker: Breakdown by ticker
            - position_count: Number of open positions
            - positions_detail: List of position details
        """
        # Get open options positions
        options_df = portfolio_manager.get_options_dataframe(status='open')

        if options_df.empty:
            return {
                'total_deployed': 0.0,
                'by_strategy': {},
                'by_ticker': {},
                'position_count': 0,
                'positions_detail': []
            }

        # Calculate capital required for each position
        positions_detail = []
        by_strategy = {}
        by_ticker = {}
        total_deployed = 0.0

        for _, position in options_df.iterrows():
            # Calculate capital based on strategy
            if position['strategy'] == 'cash_secured_put':
                # CSP: Strike price * 100 * contracts (cash secured)
                capital = position['strike'] * 100 * position['contracts']
            elif position['strategy'] == 'covered_call':
                # CC: Would need stock value, but for now assume 0 additional capital
                # (stock already owned, just selling calls against it)
                capital = 0.0
            else:
                # Default: Use strike as approximation
                capital = position['strike'] * 100 * position['contracts']

            # Calculate days remaining
            try:
                exp_date = datetime.strptime(position['expiration'], '%Y-%m-%d')
                days_remaining = (exp_date - datetime.now()).days
            except:
                days_remaining = 0

            # Add to detail list
            positions_detail.append({
                'ticker': position['ticker'],
                'strategy': position['strategy'],
                'strike': position['strike'],
                'expiration': position['expiration'],
                'contracts': position['contracts'],
                'capital_deployed': capital,
                'days_remaining': days_remaining
            })

            # Aggregate by strategy
            strategy = position['strategy']
            by_strategy[strategy] = by_strategy.get(strategy, 0) + capital

            # Aggregate by ticker
            ticker = position['ticker']
            by_ticker[ticker] = by_ticker.get(ticker, 0) + capital

            # Add to total
            total_deployed += capital

        return {
            'total_deployed': total_deployed,
            'by_strategy': by_strategy,
            'by_ticker': by_ticker,
            'position_count': len(options_df),
            'positions_detail': positions_detail
        }

    def calculate_available_capital(self, portfolio_manager=None) -> Dict:
        """
        Calculate capital available for new positions

        Args:
            portfolio_manager: Optional PortfolioManager instance
                             If provided, will calculate deployed capital

        Returns:
            Dictionary with:
            - total_available: Total cash available (before reserve)
            - deployed: Currently deployed capital
            - remaining_for_new: Available for new positions
            - max_per_position: Max capital per position
            - positions_available: Number of position slots left
            - reserve_cash: Reserved cash amount
        """
        # Calculate deployed capital if portfolio provided
        deployed = 0.0
        current_positions = 0

        if portfolio_manager:
            deployment_info = self.calculate_deployed_capital(portfolio_manager)
            deployed = deployment_info['total_deployed']
            current_positions = deployment_info['position_count']

        # Calculate available capital
        total_available = self.available_cash - self.reserve_cash
        remaining_for_new = max(0, total_available - deployed)

        # Calculate position slots
        positions_available = max(0, self.max_positions - current_positions)

        return {
            'total_available': total_available,
            'deployed': deployed,
            'remaining_for_new': remaining_for_new,
            'max_per_position': self.max_cash_per_position,
            'positions_available': positions_available,
            'reserve_cash': self.reserve_cash,
            'available_cash': self.available_cash,
            'current_positions': current_positions,
            'max_positions': self.max_positions
        }

    def get_position_capacity(self, portfolio_manager) -> Dict:
        """
        Determine how much capacity remains for new positions

        Args:
            portfolio_manager: PortfolioManager instance

        Returns:
            Dictionary with:
            - can_open_new: Whether new positions can be opened
            - reason: If False, reason why
            - max_new_capital: Maximum capital for a new position
            - positions_slots_left: Number of position slots remaining
        """
        capital_info = self.calculate_available_capital(portfolio_manager)

        # Check position limit
        if capital_info['positions_available'] <= 0:
            return {
                'can_open_new': False,
                'reason': 'max_positions_reached',
                'max_new_capital': 0.0,
                'positions_slots_left': 0
            }

        # Check capital availability
        if capital_info['remaining_for_new'] <= 0:
            return {
                'can_open_new': False,
                'reason': 'insufficient_capital',
                'max_new_capital': 0.0,
                'positions_slots_left': capital_info['positions_available']
            }

        # Calculate max capital for new position
        # Lesser of: remaining capital or max per position setting
        max_new_capital = min(
            capital_info['remaining_for_new'],
            capital_info['max_per_position']
        )

        return {
            'can_open_new': True,
            'reason': 'capacity_available',
            'max_new_capital': max_new_capital,
            'positions_slots_left': capital_info['positions_available']
        }

    def calculate_ticker_concentration(self, portfolio_manager) -> Dict[str, float]:
        """
        Calculate capital concentration by ticker (as percentage)

        Args:
            portfolio_manager: PortfolioManager instance

        Returns:
            Dictionary mapping ticker to % of total deployed capital
        """
        deployment_info = self.calculate_deployed_capital(portfolio_manager)
        total_deployed = deployment_info['total_deployed']

        if total_deployed == 0:
            return {}

        concentration = {}
        for ticker, capital in deployment_info['by_ticker'].items():
            concentration[ticker] = (capital / total_deployed) * 100

        return concentration

    def get_capital_summary_string(self, portfolio_manager) -> str:
        """
        Generate formatted string summary of capital status

        Args:
            portfolio_manager: PortfolioManager instance

        Returns:
            Formatted multi-line string with capital summary
        """
        deployment_info = self.calculate_deployed_capital(portfolio_manager)
        capital_info = self.calculate_available_capital(portfolio_manager)

        summary = []
        summary.append("="*80)
        summary.append("PORTFOLIO & CAPITAL ANALYSIS")
        summary.append("="*80)
        summary.append("")
        summary.append("Current Capital Status:")
        summary.append(f"  Total Available Cash:        ${capital_info['available_cash']:,.0f}")
        summary.append(f"  Reserve Cash:                ${capital_info['reserve_cash']:,.0f}")
        summary.append(f"  Deployable Capital:          ${capital_info['total_available']:,.0f}")
        summary.append("")

        if deployment_info['total_deployed'] > 0:
            deployed_pct = (deployment_info['total_deployed'] / capital_info['total_available']) * 100
            remaining_pct = (capital_info['remaining_for_new'] / capital_info['total_available']) * 100
            summary.append(f"  Currently Deployed:          ${deployment_info['total_deployed']:,.0f}  ({deployed_pct:.0f}%)")
            summary.append(f"  Remaining Available:         ${capital_info['remaining_for_new']:,.0f}  ({remaining_pct:.0f}%)")
        else:
            summary.append(f"  Currently Deployed:          $0  (0%)")
            summary.append(f"  Remaining Available:         ${capital_info['remaining_for_new']:,.0f}  (100%)")

        summary.append("")
        summary.append(f"  Open Positions:              {capital_info['current_positions']} / {capital_info['max_positions']}")
        summary.append(f"  Position Slots Available:    {capital_info['positions_available']}")

        # Add breakdown by strategy if positions exist
        if deployment_info['by_strategy']:
            summary.append("")
            summary.append("Deployed Capital by Strategy:")
            for strategy, capital in deployment_info['by_strategy'].items():
                pct = (capital / deployment_info['total_deployed']) * 100 if deployment_info['total_deployed'] > 0 else 0
                summary.append(f"  {strategy.replace('_', ' ').title():25} ${capital:,.0f}  ({pct:.0f}%)")

        # Add breakdown by ticker if positions exist
        if deployment_info['by_ticker']:
            summary.append("")
            summary.append("Deployed Capital by Ticker:")
            # Sort by capital amount (descending)
            sorted_tickers = sorted(deployment_info['by_ticker'].items(), key=lambda x: x[1], reverse=True)
            for ticker, capital in sorted_tickers:
                pct = (capital / deployment_info['total_deployed']) * 100 if deployment_info['total_deployed'] > 0 else 0
                summary.append(f"  {ticker:8} ${capital:,.0f}  ({pct:.0f}%)")

        summary.append("")
        return "\n".join(summary)


if __name__ == '__main__':
    # Quick test
    from src.portfolio.portfolio_manager import PortfolioManager

    portfolio = PortfolioManager()
    calculator = CapitalCalculator()

    print("Testing Capital Calculator...\n")
    print(calculator.get_capital_summary_string(portfolio))

    capacity = calculator.get_position_capacity(portfolio)
    print("\nPosition Capacity:")
    print(f"  Can open new: {capacity['can_open_new']}")
    print(f"  Reason: {capacity['reason']}")
    print(f"  Max new capital: ${capacity['max_new_capital']:,.0f}")
    print(f"  Slots left: {capacity['positions_slots_left']}")
