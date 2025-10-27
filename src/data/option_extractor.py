"""
Options Data Extractor
Fetches option chain data from Yahoo Finance using yfinance
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import os


class OptionDataExtractor:
    """Extract and store option chain data from Yahoo Finance"""

    def __init__(self, data_dir: str = "data/option_chains"):
        """
        Initialize the extractor

        Args:
            data_dir: Directory to store option chain data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def get_option_chain(self, ticker: str, expiration_date: str) -> Dict[str, pd.DataFrame]:
        """
        Get option chain for a specific ticker and expiration date

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
            expiration_date: Expiration date in YYYY-MM-DD format

        Returns:
            Dictionary with 'calls' and 'puts' DataFrames
        """
        try:
            stock = yf.Ticker(ticker)
            options = stock.option_chain(expiration_date)

            calls = options.calls.copy()
            puts = options.puts.copy()

            # Add metadata
            calls['ticker'] = ticker
            calls['expiration'] = expiration_date
            calls['option_type'] = 'call'
            calls['fetch_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            puts['ticker'] = ticker
            puts['expiration'] = expiration_date
            puts['option_type'] = 'put'
            puts['fetch_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            return {'calls': calls, 'puts': puts}

        except Exception as e:
            print(f"Error fetching options for {ticker} on {expiration_date}: {str(e)}")
            return {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}

    def get_available_expirations(self, ticker: str) -> List[str]:
        """
        Get list of available expiration dates for a ticker

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of expiration dates
        """
        try:
            stock = yf.Ticker(ticker)
            return list(stock.options)
        except Exception as e:
            print(f"Error fetching expirations for {ticker}: {str(e)}")
            return []

    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current stock price

        Args:
            ticker: Stock ticker symbol

        Returns:
            Current stock price or None if error
        """
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            if not data.empty:
                return float(data['Close'].iloc[-1])
            return None
        except Exception as e:
            print(f"Error fetching price for {ticker}: {str(e)}")
            return None

    def get_stock_info(self, ticker: str) -> Dict:
        """
        Get basic stock information

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with stock info
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                'ticker': ticker,
                'price': self.get_current_price(ticker),
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 1.0),
                'market_cap': info.get('marketCap', 0)
            }
        except Exception as e:
            print(f"Error fetching info for {ticker}: {str(e)}")
            return {'ticker': ticker, 'price': self.get_current_price(ticker)}

    def fetch_and_store_options(self, tickers: List[str],
                                expiration_dates: Optional[List[str]] = None,
                                num_expirations: int = 4) -> pd.DataFrame:
        """
        Fetch option chains for multiple tickers and expirations

        Args:
            tickers: List of ticker symbols
            expiration_dates: Specific expiration dates, or None to use next N expirations
            num_expirations: Number of expiration dates to fetch if expiration_dates is None

        Returns:
            Combined DataFrame with all options data
        """
        all_calls = []
        all_puts = []

        for ticker in tickers:
            print(f"\nFetching options for {ticker}...")

            # Get expiration dates
            if expiration_dates is None:
                available_expirations = self.get_available_expirations(ticker)
                expirations_to_fetch = available_expirations[:num_expirations]
            else:
                expirations_to_fetch = expiration_dates

            # Get current price
            current_price = self.get_current_price(ticker)
            print(f"Current price: ${current_price:.2f}" if current_price else "Price unavailable")

            # Fetch each expiration
            for exp_date in expirations_to_fetch:
                print(f"  Fetching {exp_date}...")
                chain = self.get_option_chain(ticker, exp_date)

                if not chain['calls'].empty:
                    chain['calls']['current_stock_price'] = current_price
                    all_calls.append(chain['calls'])

                if not chain['puts'].empty:
                    chain['puts']['current_stock_price'] = current_price
                    all_puts.append(chain['puts'])

        # Combine all data
        calls_df = pd.concat(all_calls, ignore_index=True) if all_calls else pd.DataFrame()
        puts_df = pd.concat(all_puts, ignore_index=True) if all_puts else pd.DataFrame()
        options_df = pd.concat([calls_df, puts_df], ignore_index=True)

        # Save to file
        if not options_df.empty:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.data_dir, f"options_data_{timestamp}.csv")
            options_df.to_csv(filename, index=False)
            print(f"\nData saved to: {filename}")
            print(f"Total options fetched: {len(options_df)}")

        return options_df

    def load_latest_data(self) -> pd.DataFrame:
        """
        Load the most recent options data file

        Returns:
            DataFrame with options data
        """
        files = [f for f in os.listdir(self.data_dir) if f.startswith('options_data_') and f.endswith('.csv')]

        if not files:
            print("No saved options data found")
            return pd.DataFrame()

        latest_file = sorted(files)[-1]
        filepath = os.path.join(self.data_dir, latest_file)
        print(f"Loading data from: {filepath}")

        return pd.read_csv(filepath)
