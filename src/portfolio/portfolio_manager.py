"""
Portfolio Manager
Track existing stock and option positions
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import json
import os


class PortfolioManager:
    """Manage portfolio of stocks and options"""

    def __init__(self, portfolio_file: str = "data/portfolio/portfolio.json"):
        """
        Initialize portfolio manager

        Args:
            portfolio_file: Path to portfolio JSON file
        """
        self.portfolio_file = portfolio_file
        os.makedirs(os.path.dirname(portfolio_file), exist_ok=True)
        self.portfolio = self._load_portfolio()

    def _load_portfolio(self) -> Dict:
        """Load portfolio from file"""
        if os.path.exists(self.portfolio_file):
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        else:
            return {
                'stocks': [],
                'options': [],
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    def _save_portfolio(self):
        """Save portfolio to file"""
        self.portfolio['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.portfolio, f, indent=2)
        print(f"Portfolio saved to {self.portfolio_file}")

    def add_stock_position(self, ticker: str, shares: int, cost_basis: float,
                          purchase_date: str, notes: str = ""):
        """
        Add stock position to portfolio

        Args:
            ticker: Stock ticker
            shares: Number of shares
            cost_basis: Cost per share
            purchase_date: Purchase date (YYYY-MM-DD)
            notes: Optional notes
        """
        position = {
            'ticker': ticker,
            'shares': shares,
            'cost_basis': cost_basis,
            'purchase_date': purchase_date,
            'notes': notes,
            'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        self.portfolio['stocks'].append(position)
        self._save_portfolio()
        print(f"Added {shares} shares of {ticker} @ ${cost_basis:.2f}")

    def add_option_position(self, ticker: str, option_type: str, strike: float,
                          expiration: str, contracts: int, premium: float,
                          open_date: str, strategy: str = "", notes: str = ""):
        """
        Add option position to portfolio

        Args:
            ticker: Underlying ticker
            option_type: 'call' or 'put'
            strike: Strike price
            expiration: Expiration date (YYYY-MM-DD)
            contracts: Number of contracts
            premium: Premium per share (received if sold, paid if bought)
            open_date: Date position opened (YYYY-MM-DD)
            strategy: Strategy name (e.g., 'covered_call', 'cash_secured_put')
            notes: Optional notes
        """
        position = {
            'ticker': ticker,
            'option_type': option_type,
            'strike': strike,
            'expiration': expiration,
            'contracts': contracts,
            'premium': premium,
            'open_date': open_date,
            'strategy': strategy,
            'status': 'open',
            'notes': notes,
            'added_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        self.portfolio['options'].append(position)
        self._save_portfolio()
        print(f"Added {contracts} {ticker} {strike} {option_type} @ ${premium:.2f} premium")

    def close_option_position(self, index: int, close_date: str,
                            close_premium: float = 0.0, outcome: str = "expired"):
        """
        Close an option position

        Args:
            index: Index in options list
            close_date: Date closed (YYYY-MM-DD)
            close_premium: Premium paid to close (if bought back)
            outcome: 'expired', 'assigned', 'bought_back'
        """
        if 0 <= index < len(self.portfolio['options']):
            self.portfolio['options'][index]['status'] = 'closed'
            self.portfolio['options'][index]['close_date'] = close_date
            self.portfolio['options'][index]['close_premium'] = close_premium
            self.portfolio['options'][index]['outcome'] = outcome
            self._save_portfolio()
            print(f"Closed option position #{index}")
        else:
            print(f"Invalid index: {index}")

    def remove_stock_position(self, index: int):
        """Remove stock position"""
        if 0 <= index < len(self.portfolio['stocks']):
            removed = self.portfolio['stocks'].pop(index)
            self._save_portfolio()
            print(f"Removed {removed['ticker']} position")
        else:
            print(f"Invalid index: {index}")

    def get_stocks_dataframe(self) -> pd.DataFrame:
        """Get stock positions as DataFrame"""
        if not self.portfolio['stocks']:
            return pd.DataFrame()
        return pd.DataFrame(self.portfolio['stocks'])

    def get_options_dataframe(self, status: str = 'all') -> pd.DataFrame:
        """
        Get option positions as DataFrame

        Args:
            status: 'open', 'closed', or 'all'

        Returns:
            DataFrame with option positions
        """
        if not self.portfolio['options']:
            return pd.DataFrame()

        df = pd.DataFrame(self.portfolio['options'])

        if status == 'open':
            df = df[df['status'] == 'open']
        elif status == 'closed':
            df = df[df['status'] == 'closed']

        return df

    def get_covered_call_opportunities(self) -> pd.DataFrame:
        """
        Get stocks available for covered calls

        Returns:
            DataFrame with stocks that can be used for covered calls
        """
        stocks_df = self.get_stocks_dataframe()
        if stocks_df.empty:
            return pd.DataFrame()

        # Check which stocks have enough shares for covered calls (100+ shares)
        stocks_df['contracts_available'] = stocks_df['shares'] // 100
        covered_call_stocks = stocks_df[stocks_df['contracts_available'] > 0].copy()

        return covered_call_stocks[['ticker', 'shares', 'contracts_available',
                                   'cost_basis', 'purchase_date', 'notes']]

    def analyze_portfolio_with_current_prices(self, price_data: Dict[str, float]) -> Dict:
        """
        Analyze portfolio with current prices

        Args:
            price_data: Dictionary of {ticker: current_price}

        Returns:
            Dictionary with portfolio analysis
        """
        analysis = {
            'total_stock_value': 0,
            'total_stock_cost': 0,
            'total_gain_loss': 0,
            'stock_positions': [],
            'option_positions': []
        }

        # Analyze stocks
        for stock in self.portfolio['stocks']:
            ticker = stock['ticker']
            current_price = price_data.get(ticker, stock['cost_basis'])

            position_value = current_price * stock['shares']
            position_cost = stock['cost_basis'] * stock['shares']
            gain_loss = position_value - position_cost
            gain_loss_pct = (gain_loss / position_cost * 100) if position_cost > 0 else 0

            analysis['stock_positions'].append({
                'ticker': ticker,
                'shares': stock['shares'],
                'cost_basis': stock['cost_basis'],
                'current_price': current_price,
                'position_value': position_value,
                'position_cost': position_cost,
                'gain_loss': gain_loss,
                'gain_loss_pct': gain_loss_pct,
                'purchase_date': stock['purchase_date']
            })

            analysis['total_stock_value'] += position_value
            analysis['total_stock_cost'] += position_cost

        analysis['total_gain_loss'] = analysis['total_stock_value'] - analysis['total_stock_cost']
        analysis['total_gain_loss_pct'] = (
            (analysis['total_gain_loss'] / analysis['total_stock_cost'] * 100)
            if analysis['total_stock_cost'] > 0 else 0
        )

        # Analyze open options
        for option in self.portfolio['options']:
            if option['status'] == 'open':
                days_remaining = (pd.to_datetime(option['expiration']) -
                                pd.Timestamp.now()).days

                analysis['option_positions'].append({
                    'ticker': option['ticker'],
                    'type': option['option_type'],
                    'strike': option['strike'],
                    'expiration': option['expiration'],
                    'days_remaining': days_remaining,
                    'contracts': option['contracts'],
                    'premium_received': option['premium'] * option['contracts'] * 100,
                    'strategy': option['strategy']
                })

        return analysis

    def export_to_csv(self, output_dir: str = "data/portfolio"):
        """Export portfolio to CSV files"""
        os.makedirs(output_dir, exist_ok=True)

        # Export stocks
        stocks_df = self.get_stocks_dataframe()
        if not stocks_df.empty:
            stocks_file = os.path.join(output_dir, 'stocks.csv')
            stocks_df.to_csv(stocks_file, index=False)
            print(f"Stocks exported to {stocks_file}")

        # Export options
        options_df = self.get_options_dataframe()
        if not options_df.empty:
            options_file = os.path.join(output_dir, 'options.csv')
            options_df.to_csv(options_file, index=False)
            print(f"Options exported to {options_file}")

    def summary(self) -> str:
        """Get portfolio summary"""
        num_stocks = len(self.portfolio['stocks'])
        num_open_options = len([o for o in self.portfolio['options'] if o['status'] == 'open'])
        num_closed_options = len([o for o in self.portfolio['options'] if o['status'] == 'closed'])

        summary = f"""
Portfolio Summary
=================
Stock Positions: {num_stocks}
Open Options: {num_open_options}
Closed Options: {num_closed_options}
Last Updated: {self.portfolio.get('last_updated', 'N/A')}
"""
        return summary
