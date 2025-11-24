# src/analysis/leaps_analysis.py

import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict

from src.data.option_extractor import OptionDataExtractor

def fetch_leaps_calls(ticker: str, extractor: OptionDataExtractor, min_days: int) -> pd.DataFrame:
    """
    Fetches all LEAPS call options for a given ticker.
    """
    print(f"Fetching LEAPS data for {ticker}...")
    
    current_price = extractor.get_current_price(ticker)
    if not current_price:
        print(f"Could not get current price for {ticker}. Skipping.")
        return pd.DataFrame()

    expirations = extractor.get_available_expirations(ticker)
    if not expirations:
        print(f"Could not get expirations for {ticker}. Skipping.")
        return pd.DataFrame()

    leaps_expirations = []
    today = datetime.now().date()
    min_expiration_date = today + timedelta(days=min_days)

    for exp_str in expirations:
        exp_date = datetime.strptime(exp_str, '%Y-%m-%d').date()
        if exp_date > min_expiration_date:
            leaps_expirations.append(exp_str)
    
    if not leaps_expirations:
        print(f"No LEAPS expirations found for {ticker}.")
        return pd.DataFrame()

    all_leaps_calls = []
    for exp_date in leaps_expirations:
        print(f"  Fetching {exp_date}...")
        chain = extractor.get_option_chain(ticker, exp_date)
        if not chain['calls'].empty:
            all_leaps_calls.append(chain['calls'])

    if not all_leaps_calls:
        print(f"No call options found in LEAPS expirations for {ticker}.")
        return pd.DataFrame()

    combined_df = pd.concat(all_leaps_calls, ignore_index=True)
    combined_df['current_stock_price'] = current_price
    
    return combined_df

def find_leaps_opportunities(
    watchlist: List[str], 
    config: Dict
) -> pd.DataFrame:
    """
    Analyzes a watchlist of tickers to find potential LEAPS call option bets.
    """
    extractor = OptionDataExtractor()
    all_opportunities = []

    for ticker in watchlist:
        leaps_df = fetch_leaps_calls(ticker, extractor, config['days_to_expiration_min'])
        
        if leaps_df.empty:
            print(f"No LEAPS data found for {ticker}.")
            continue
            
        print(f"Found {len(leaps_df)} total LEAPS calls for {ticker}. Now filtering...")

        leaps_df['expiration_date'] = pd.to_datetime(leaps_df['expiration'])
        leaps_df['days_to_expiration'] = (leaps_df['expiration_date'] - datetime.now()).dt.days

        min_strike = leaps_df['current_stock_price'] * (1 + config['otm_percentage_min'] / 100)
        filtered_df = leaps_df[leaps_df['strike'] > min_strike].copy()

        filtered_df = filtered_df[filtered_df['ask'] <= config['max_ask_price']]

        filtered_df = filtered_df[
            (filtered_df['openInterest'] >= config['min_open_interest']) &
            (filtered_df['volume'] >= config['min_volume'])
        ]

        if filtered_df.empty:
            print(f"No opportunities found for {ticker} after filtering.")
            continue

        print(f"Found {len(filtered_df)} potential opportunities for {ticker} after filtering.")
        
        columns_to_show = [
            'ticker', 'current_stock_price', 'strike', 'expiration', 'days_to_expiration',
            'ask', 'delta', 'volume', 'openInterest'
        ]
        
        for col in columns_to_show:
            if col not in filtered_df.columns:
                filtered_df[col] = 'N/A'

        final_df = filtered_df[columns_to_show].sort_values(by=['days_to_expiration', 'strike'])
        all_opportunities.append(final_df)

    if not all_opportunities:
        return pd.DataFrame()

    return pd.concat(all_opportunities, ignore_index=True)
