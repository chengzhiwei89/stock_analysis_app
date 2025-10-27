"""
Explore what data yfinance provides beyond options chains
This shows ALL available technical and fundamental data
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def explore_stock_data(ticker: str = "AAPL"):
    """Explore all available data for a stock"""

    print("="*80)
    print(f"EXPLORING YFINANCE DATA FOR {ticker}")
    print("="*80)

    stock = yf.Ticker(ticker)

    # =========================================================================
    # 1. BASIC INFO
    # =========================================================================
    print("\n" + "="*80)
    print("1. BASIC COMPANY INFO")
    print("="*80)

    info = stock.info
    basic_fields = [
        'longName', 'sector', 'industry', 'marketCap', 'employees',
        'city', 'state', 'country', 'website'
    ]

    for field in basic_fields:
        if field in info:
            print(f"{field:20}: {info[field]}")

    # =========================================================================
    # 2. PRICE & VALUATION METRICS
    # =========================================================================
    print("\n" + "="*80)
    print("2. PRICE & VALUATION METRICS (Most Important!)")
    print("="*80)

    price_fields = [
        'currentPrice', 'previousClose', 'open', 'dayHigh', 'dayLow',
        'regularMarketVolume', 'averageVolume', 'averageVolume10days',
        'fiftyDayAverage', 'twoHundredDayAverage',
        'fiftyTwoWeekLow', 'fiftyTwoWeekHigh',
    ]

    for field in price_fields:
        if field in info:
            print(f"{field:30}: {info[field]}")

    # =========================================================================
    # 3. FUNDAMENTAL RATIOS
    # =========================================================================
    print("\n" + "="*80)
    print("3. FUNDAMENTAL RATIOS (Quality Assessment)")
    print("="*80)

    fundamental_fields = [
        'trailingPE', 'forwardPE', 'priceToBook', 'priceToSalesTrailing12Months',
        'enterpriseToRevenue', 'enterpriseToEbitda',
        'profitMargins', 'grossMargins', 'operatingMargins',
        'returnOnAssets', 'returnOnEquity',
        'revenueGrowth', 'earningsGrowth',
        'debtToEquity', 'currentRatio', 'quickRatio',
        'beta'  # Volatility vs market
    ]

    for field in fundamental_fields:
        if field in info:
            value = info[field]
            if isinstance(value, float):
                print(f"{field:40}: {value:.4f}")
            else:
                print(f"{field:40}: {value}")

    # =========================================================================
    # 4. ANALYST RECOMMENDATIONS
    # =========================================================================
    print("\n" + "="*80)
    print("4. ANALYST RECOMMENDATIONS")
    print("="*80)

    analyst_fields = [
        'recommendationKey', 'recommendationMean', 'numberOfAnalystOpinions',
        'targetHighPrice', 'targetLowPrice', 'targetMeanPrice', 'targetMedianPrice'
    ]

    for field in analyst_fields:
        if field in info:
            print(f"{field:30}: {info[field]}")

    # Detailed recommendations
    try:
        recommendations = stock.recommendations
        if recommendations is not None and not recommendations.empty:
            print("\nRECENT ANALYST ACTIONS:")
            print(recommendations.tail(10))
    except:
        print("No detailed recommendations available")

    # =========================================================================
    # 5. EARNINGS & EVENTS
    # =========================================================================
    print("\n" + "="*80)
    print("5. EARNINGS & EVENTS (Critical for Options!)")
    print("="*80)

    earnings_fields = [
        'earningsQuarterlyGrowth', 'trailingEps', 'forwardEps',
        'mostRecentQuarter', 'nextFiscalYearEnd', 'lastFiscalYearEnd'
    ]

    for field in earnings_fields:
        if field in info:
            print(f"{field:30}: {info[field]}")

    # Earnings calendar
    try:
        calendar = stock.calendar
        if calendar is not None:
            print("\nEARNINGS CALENDAR:")
            print(calendar)
    except:
        print("No earnings calendar available")

    # Historical earnings
    try:
        earnings_history = stock.earnings_history
        if earnings_history is not None and not earnings_history.empty:
            print("\nRECENT EARNINGS HISTORY:")
            print(earnings_history)
    except:
        print("No earnings history available")

    # =========================================================================
    # 6. DIVIDEND INFO
    # =========================================================================
    print("\n" + "="*80)
    print("6. DIVIDEND INFO")
    print("="*80)

    dividend_fields = [
        'dividendRate', 'dividendYield', 'payoutRatio',
        'exDividendDate', 'lastDividendDate', 'lastDividendValue'
    ]

    for field in dividend_fields:
        if field in info:
            print(f"{field:30}: {info[field]}")

    # =========================================================================
    # 7. TECHNICAL INDICATORS (from historical data)
    # =========================================================================
    print("\n" + "="*80)
    print("7. HISTORICAL PRICE DATA (for Technical Analysis)")
    print("="*80)

    # Get 6 months of historical data
    hist = stock.history(period="6mo")

    if not hist.empty:
        print(f"\nHistorical data available: {len(hist)} days")
        print(f"Date range: {hist.index[0]} to {hist.index[-1]}")
        print("\nRecent prices:")
        print(hist[['Close', 'Volume']].tail(10))

        # Calculate some basic technical indicators
        hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
        hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
        hist['SMA_200'] = hist['Close'].rolling(window=100).mean()

        current_price = hist['Close'].iloc[-1]
        sma_20 = hist['SMA_20'].iloc[-1]
        sma_50 = hist['SMA_50'].iloc[-1]

        print(f"\nTECHNICAL INDICATORS:")
        print(f"Current Price: ${current_price:.2f}")
        print(f"20-day SMA: ${sma_20:.2f} ({'Above' if current_price > sma_20 else 'Below'})")
        print(f"50-day SMA: ${sma_50:.2f} ({'Above' if current_price > sma_50 else 'Below'})")

        # Trend
        if current_price > sma_20 > sma_50:
            trend = "UPTREND"
        elif current_price < sma_20 < sma_50:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"

        print(f"Trend: {trend}")

        # Volatility (30-day historical)
        returns = hist['Close'].pct_change().dropna()
        hist_vol_30d = returns.tail(30).std() * (252 ** 0.5)  # Annualized

        print(f"30-day Historical Volatility: {hist_vol_30d:.2%}")

    # =========================================================================
    # 8. INSTITUTIONAL & INSIDER HOLDINGS
    # =========================================================================
    print("\n" + "="*80)
    print("8. INSTITUTIONAL & INSIDER HOLDINGS")
    print("="*80)

    holding_fields = [
        'heldPercentInsiders', 'heldPercentInstitutions',
        'floatShares', 'sharesOutstanding', 'sharesShort',
        'shortRatio', 'shortPercentOfFloat'
    ]

    for field in holding_fields:
        if field in info:
            value = info[field]
            if isinstance(value, float) and 0 <= value <= 1:
                print(f"{field:30}: {value:.2%}")
            else:
                print(f"{field:30}: {value}")

    # Major holders
    try:
        major_holders = stock.major_holders
        if major_holders is not None and not major_holders.empty:
            print("\nMAJOR HOLDERS:")
            print(major_holders)
    except:
        print("No major holders data available")

    # =========================================================================
    # 9. FINANCIAL STATEMENTS
    # =========================================================================
    print("\n" + "="*80)
    print("9. FINANCIAL STATEMENTS (Available but detailed)")
    print("="*80)

    try:
        # Income statement
        income_stmt = stock.income_stmt
        if income_stmt is not None and not income_stmt.empty:
            print(f"\nIncome Statement available: {income_stmt.shape}")
            print("Recent revenue and earnings:")
            if 'Total Revenue' in income_stmt.index:
                print(income_stmt.loc['Total Revenue'])
    except Exception as e:
        print(f"Income statement not available: {e}")

    # =========================================================================
    # 10. RISK METRICS
    # =========================================================================
    print("\n" + "="*80)
    print("10. RISK METRICS")
    print("="*80)

    risk_fields = [
        'beta', 'impliedSharesOutstanding', 'bookValue',
        'auditRisk', 'boardRisk', 'compensationRisk', 'shareHolderRightsRisk', 'overallRisk'
    ]

    for field in risk_fields:
        if field in info:
            print(f"{field:30}: {info[field]}")

    # =========================================================================
    # SUMMARY: WHAT'S MOST USEFUL FOR OPTIONS
    # =========================================================================
    print("\n" + "="*80)
    print("SUMMARY: MOST USEFUL DATA FOR OPTIONS TRADING")
    print("="*80)

    print("\n✓ TECHNICAL FACTORS (from historical data):")
    print("  - Price trends (SMA crossovers)")
    print("  - Support/resistance levels (52-week high/low)")
    print("  - Volume analysis")
    print("  - Historical volatility")
    print("  - RSI, MACD (can calculate)")

    print("\n✓ FUNDAMENTAL FACTORS (from info):")
    print("  - Valuation ratios (PE, PB)")
    print("  - Profitability (margins, ROE)")
    print("  - Growth rates")
    print("  - Financial health (debt ratios)")
    print("  - Beta (market correlation)")

    print("\n✓ EVENT FACTORS (from calendar/info):")
    print("  - Earnings dates (high volatility!)")
    print("  - Dividend dates")
    print("  - Analyst upgrades/downgrades")

    print("\n✓ SENTIMENT FACTORS (from recommendations):")
    print("  - Analyst consensus")
    print("  - Target prices")
    print("  - Recent rating changes")

    print("\n" + "="*80)
    print("ALL DATA STORED IN: stock.info, stock.history(), stock.recommendations, etc.")
    print("="*80 + "\n")


def compare_tickers(tickers: list):
    """Compare key metrics across multiple tickers"""

    print("\n" + "="*80)
    print(f"COMPARING TICKERS: {', '.join(tickers)}")
    print("="*80 + "\n")

    data = []

    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="3mo")

            # Calculate technical indicators
            returns = hist['Close'].pct_change().dropna()
            hist_vol = returns.std() * (252 ** 0.5) if not returns.empty else None

            current = hist['Close'].iloc[-1] if not hist.empty else None
            sma_50 = hist['Close'].rolling(50).mean().iloc[-1] if len(hist) >= 50 else None

            data.append({
                'Ticker': ticker,
                'Price': info.get('currentPrice', current),
                'PE': info.get('trailingPE'),
                'Beta': info.get('beta'),
                'Hist_Vol': hist_vol,
                '52W_Low': info.get('fiftyTwoWeekLow'),
                '52W_High': info.get('fiftyTwoWeekHigh'),
                'Above_50SMA': 'Yes' if (current and sma_50 and current > sma_50) else 'No',
                'Analyst_Rating': info.get('recommendationKey'),
                'Target_Price': info.get('targetMeanPrice'),
            })
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

    df = pd.DataFrame(data)
    print(df.to_string(index=False))


if __name__ == "__main__":
    # Explore one stock in detail
    explore_stock_data("AAPL")

    # Compare multiple stocks
    print("\n\n")
    compare_tickers(['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'QQQ'])
