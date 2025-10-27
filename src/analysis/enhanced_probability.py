"""
Enhanced Probability Calculator
Combines options data with technical and fundamental factors
to improve probability estimates beyond basic Black-Scholes
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Optional


class EnhancedProbabilityAnalyzer:
    """
    Calculate enhanced probabilities using technical and fundamental factors

    This goes beyond standard Black-Scholes prob_otm by incorporating:
    - Technical factors (trend, momentum, support/resistance)
    - Fundamental factors (valuation, growth, quality)
    - Event factors (earnings dates, dividends)
    - Sentiment factors (analyst ratings)
    """

    def __init__(self):
        self.cache = {}  # Cache stock data to avoid repeated API calls

    def get_stock_data(self, ticker: str, force_refresh: bool = False) -> Dict:
        """
        Fetch and cache comprehensive stock data

        Args:
            ticker: Stock ticker
            force_refresh: Force refresh cached data

        Returns:
            Dictionary with all relevant data
        """
        if ticker in self.cache and not force_refresh:
            return self.cache[ticker]

        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="6mo")

            if hist.empty:
                return None

            # Technical indicators
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            hist['SMA_200'] = hist['Close'].rolling(window=100).mean()

            returns = hist['Close'].pct_change().dropna()
            hist_vol_30d = returns.tail(30).std() * (252 ** 0.5) if len(returns) >= 30 else None

            current_price = hist['Close'].iloc[-1]
            sma_20 = hist['SMA_20'].iloc[-1]
            sma_50 = hist['SMA_50'].iloc[-1]
            sma_200 = hist['SMA_200'].iloc[-1] if len(hist) >= 100 else None

            # Get earnings calendar
            try:
                calendar = stock.calendar
                next_earnings = None
                if calendar and 'Earnings Date' in calendar:
                    earnings_dates = calendar['Earnings Date']
                    if earnings_dates:
                        next_earnings = earnings_dates[0] if isinstance(earnings_dates, list) else earnings_dates
            except:
                next_earnings = None

            data = {
                'ticker': ticker,
                'current_price': current_price,

                # Technical factors
                'sma_20': sma_20,
                'sma_50': sma_50,
                'sma_200': sma_200,
                'hist_vol_30d': hist_vol_30d,
                '52w_low': info.get('fiftyTwoWeekLow'),
                '52w_high': info.get('fiftyTwoWeekHigh'),
                'volume': info.get('regularMarketVolume'),
                'avg_volume': info.get('averageVolume'),

                # Fundamental factors
                'beta': info.get('beta'),
                'trailing_pe': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'profit_margins': info.get('profitMargins'),
                'roe': info.get('returnOnEquity'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'debt_to_equity': info.get('debtToEquity'),

                # Sentiment factors
                'recommendation': info.get('recommendationKey'),
                'recommendation_mean': info.get('recommendationMean'),
                'target_mean_price': info.get('targetMeanPrice'),
                'num_analysts': info.get('numberOfAnalystOpinions'),

                # Event factors
                'next_earnings': next_earnings,
                'dividend_yield': info.get('dividendYield'),

                # Historical data
                'hist': hist,
            }

            self.cache[ticker] = data
            return data

        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def calculate_technical_score(self, ticker_data: Dict, strike: float,
                                  option_type: str = 'put') -> float:
        """
        Calculate technical analysis score (0-100)
        Higher = more bullish (good for puts below price)

        Factors:
        - Trend (SMA positions)
        - Momentum (price vs SMAs)
        - Support/Resistance (52-week levels)
        - Volume
        """
        if not ticker_data:
            return 50  # Neutral

        score = 50  # Start neutral
        current = ticker_data['current_price']

        # 1. TREND ANALYSIS (±15 points)
        sma_20 = ticker_data.get('sma_20')
        sma_50 = ticker_data.get('sma_50')
        sma_200 = ticker_data.get('sma_200')

        if sma_20 and sma_50:
            if current > sma_20 > sma_50:
                score += 15  # Strong uptrend (good for puts OTM)
            elif current > sma_20 and sma_20 < sma_50:
                score += 5  # Early uptrend
            elif current < sma_20 > sma_50:
                score -= 5  # Possible reversal
            elif current < sma_20 < sma_50:
                score -= 15  # Downtrend (bad for puts OTM)

        # 2. DISTANCE FROM SMAs (±10 points)
        if sma_50:
            pct_from_sma50 = (current - sma_50) / sma_50 * 100
            if pct_from_sma50 > 10:
                score += 10  # Well above support
            elif pct_from_sma50 > 5:
                score += 5
            elif pct_from_sma50 < -10:
                score -= 10  # Well below resistance
            elif pct_from_sma50 < -5:
                score -= 5

        # 3. 52-WEEK RANGE (±10 points)
        w52_low = ticker_data.get('52w_low')
        w52_high = ticker_data.get('52w_high')

        if w52_low and w52_high:
            position_in_range = (current - w52_low) / (w52_high - w52_low) * 100

            if position_in_range > 80:
                score += 5  # Near highs (strong, but risky)
            elif position_in_range > 60:
                score += 10  # Upper range (strong)
            elif position_in_range > 40:
                score += 5  # Mid range
            elif position_in_range < 20:
                score -= 5  # Near lows (weak)

        # 4. VOLUME (±5 points)
        volume = ticker_data.get('volume')
        avg_volume = ticker_data.get('avg_volume')

        if volume and avg_volume:
            volume_ratio = volume / avg_volume
            if volume_ratio > 1.5:
                # High volume - check if price is up or down
                hist = ticker_data.get('hist')
                if hist is not None and len(hist) >= 2:
                    price_change = (hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]
                    if price_change > 0:
                        score += 5  # High volume rally (bullish)
                    else:
                        score -= 5  # High volume selloff (bearish)

        # 5. STRIKE-SPECIFIC ADJUSTMENT for PUTS
        if option_type == 'put':
            distance_pct = ((current - strike) / current) * 100

            if distance_pct > 10:
                score += 5  # Far OTM (very safe)
            elif distance_pct > 5:
                score += 3  # Comfortably OTM
            elif distance_pct < -5:
                score -= 10  # ITM (dangerous)

        return max(0, min(100, score))  # Clamp to 0-100

    def calculate_fundamental_score(self, ticker_data: Dict) -> float:
        """
        Calculate fundamental quality score (0-100)
        Higher = higher quality company (more stable)

        Factors:
        - Valuation (PE ratios)
        - Profitability (margins, ROE)
        - Growth
        - Financial health (debt)
        """
        if not ticker_data:
            return 50

        score = 50

        # 1. VALUATION (±10 points)
        trailing_pe = ticker_data.get('trailing_pe')
        forward_pe = ticker_data.get('forward_pe')

        if trailing_pe and forward_pe:
            # Reasonable PE is good (15-30 range)
            if 15 <= forward_pe <= 30:
                score += 10  # Fairly valued
            elif forward_pe < 15:
                score += 5  # Undervalued
            elif forward_pe > 50:
                score -= 10  # Overvalued (risky)
            elif forward_pe > 35:
                score -= 5

        # 2. PROFITABILITY (±15 points)
        margins = ticker_data.get('profit_margins')
        roe = ticker_data.get('roe')

        if margins:
            if margins > 0.25:
                score += 10  # Excellent margins
            elif margins > 0.15:
                score += 5  # Good margins
            elif margins < 0.05:
                score -= 10  # Poor margins

        if roe:
            if roe > 0.20:
                score += 5  # Excellent ROE
            elif roe > 0.10:
                score += 3  # Good ROE
            elif roe < 0.05:
                score -= 5  # Poor ROE

        # 3. GROWTH (±10 points)
        revenue_growth = ticker_data.get('revenue_growth')
        earnings_growth = ticker_data.get('earnings_growth')

        if revenue_growth:
            if revenue_growth > 0.20:
                score += 5  # Strong growth
            elif revenue_growth > 0.10:
                score += 3  # Good growth
            elif revenue_growth < 0:
                score -= 5  # Declining revenue

        if earnings_growth:
            if earnings_growth > 0.15:
                score += 5  # Strong earnings growth
            elif earnings_growth < 0:
                score -= 5  # Declining earnings

        # 4. FINANCIAL HEALTH (±10 points)
        debt_to_equity = ticker_data.get('debt_to_equity')

        if debt_to_equity is not None:
            if debt_to_equity < 50:
                score += 10  # Low debt (very healthy)
            elif debt_to_equity < 100:
                score += 5  # Moderate debt
            elif debt_to_equity > 200:
                score -= 10  # High debt (risky)
            elif debt_to_equity > 150:
                score -= 5

        # 5. BETA (VOLATILITY) (±5 points)
        beta = ticker_data.get('beta')

        if beta:
            if 0.8 <= beta <= 1.2:
                score += 5  # Market-like volatility (predictable)
            elif beta > 1.5:
                score -= 5  # High volatility (riskier)

        return max(0, min(100, score))

    def calculate_sentiment_score(self, ticker_data: Dict) -> float:
        """
        Calculate analyst sentiment score (0-100)
        Higher = more bullish sentiment

        Factors:
        - Analyst recommendations
        - Price targets
        - Number of analysts covering
        """
        if not ticker_data:
            return 50

        score = 50

        # 1. RECOMMENDATION (±20 points)
        rec_key = ticker_data.get('recommendation')
        rec_mean = ticker_data.get('recommendation_mean')

        # recommendationMean: 1=Strong Buy, 2=Buy, 3=Hold, 4=Sell, 5=Strong Sell
        if rec_mean:
            if rec_mean < 2.0:
                score += 20  # Strong Buy consensus
            elif rec_mean < 2.5:
                score += 10  # Buy consensus
            elif rec_mean < 3.5:
                score += 0  # Hold consensus
            elif rec_mean < 4.5:
                score -= 10  # Sell consensus
            else:
                score -= 20  # Strong Sell consensus

        # 2. PRICE TARGET (±15 points)
        target = ticker_data.get('target_mean_price')
        current = ticker_data.get('current_price')

        if target and current:
            upside = (target - current) / current * 100

            if upside > 20:
                score += 15  # Significant upside
            elif upside > 10:
                score += 10  # Good upside
            elif upside > 0:
                score += 5  # Some upside
            elif upside < -10:
                score -= 15  # Downside risk

        # 3. ANALYST COVERAGE (±5 points)
        num_analysts = ticker_data.get('num_analysts')

        if num_analysts:
            if num_analysts > 30:
                score += 5  # Well covered (more reliable)
            elif num_analysts > 15:
                score += 3
            elif num_analysts < 5:
                score -= 5  # Limited coverage

        return max(0, min(100, score))

    def calculate_event_risk_score(self, ticker_data: Dict, days_to_expiration: int) -> float:
        """
        Calculate event risk score (0-100)
        Lower score = higher risk from upcoming events

        Factors:
        - Earnings dates
        - Dividend dates
        """
        if not ticker_data:
            return 50

        score = 100  # Start with no risk

        # 1. EARNINGS RISK (major factor)
        next_earnings = ticker_data.get('next_earnings')

        if next_earnings:
            today = datetime.now().date()

            if isinstance(next_earnings, datetime):
                earnings_date = next_earnings.date()
            else:
                earnings_date = next_earnings

            days_to_earnings = (earnings_date - today).days

            # If earnings is within option period, reduce score
            if 0 <= days_to_earnings <= days_to_expiration:
                # Earnings during option period is HIGH RISK
                if days_to_earnings < 7:
                    score -= 30  # Earnings very soon
                elif days_to_earnings < 14:
                    score -= 20  # Earnings soon
                else:
                    score -= 10  # Earnings within period

        return max(0, min(100, score))

    def calculate_enhanced_probability(self, ticker: str, strike: float,
                                      current_price: float, days_to_expiration: int,
                                      option_type: str = 'put',
                                      black_scholes_prob: Optional[float] = None) -> Dict:
        """
        Calculate enhanced probability incorporating all factors

        Args:
            ticker: Stock ticker
            strike: Strike price
            current_price: Current stock price
            days_to_expiration: Days until expiration
            option_type: 'put' or 'call'
            black_scholes_prob: Optional BS probability (will be calculated if not provided)

        Returns:
            Dictionary with probabilities and scores
        """
        # Get comprehensive stock data
        ticker_data = self.get_stock_data(ticker)

        if not ticker_data:
            # Return BS probability only if available
            return {
                'enhanced_prob_otm': black_scholes_prob,
                'black_scholes_prob_otm': black_scholes_prob,
                'adjustment': 0,
                'technical_score': 50,
                'fundamental_score': 50,
                'sentiment_score': 50,
                'event_risk_score': 50,
                'confidence': 'low'
            }

        # Calculate component scores
        technical_score = self.calculate_technical_score(ticker_data, strike, option_type)
        fundamental_score = self.calculate_fundamental_score(ticker_data)
        sentiment_score = self.calculate_sentiment_score(ticker_data)
        event_risk_score = self.calculate_event_risk_score(ticker_data, days_to_expiration)

        # Weighted composite score (0-100)
        composite_score = (
            technical_score * 0.35 +      # 35% weight on technicals
            fundamental_score * 0.25 +    # 25% weight on fundamentals
            sentiment_score * 0.20 +      # 20% weight on sentiment
            event_risk_score * 0.20       # 20% weight on event risk
        )

        # Convert composite score to probability adjustment (-15% to +15%)
        # Score 50 = neutral (0% adjustment)
        # Score 100 = +15% adjustment
        # Score 0 = -15% adjustment
        adjustment_pct = ((composite_score - 50) / 50) * 15

        # Apply adjustment to Black-Scholes probability
        if black_scholes_prob:
            enhanced_prob = black_scholes_prob + adjustment_pct
            enhanced_prob = max(0, min(100, enhanced_prob))  # Clamp to 0-100
        else:
            enhanced_prob = None

        # Confidence level based on data quality
        confidence = 'high' if all([
            ticker_data.get('sma_50'),
            ticker_data.get('trailing_pe'),
            ticker_data.get('recommendation_mean')
        ]) else 'medium' if ticker_data.get('sma_50') else 'low'

        return {
            'enhanced_prob_otm': enhanced_prob,
            'black_scholes_prob_otm': black_scholes_prob,
            'adjustment': adjustment_pct,
            'composite_score': composite_score,
            'technical_score': technical_score,
            'fundamental_score': fundamental_score,
            'sentiment_score': sentiment_score,
            'event_risk_score': event_risk_score,
            'confidence': confidence,
            'ticker_data': ticker_data,
        }

    def enrich_options_dataframe(self, options_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add enhanced probability columns to options DataFrame

        Args:
            options_df: DataFrame with options data (must have prob_otm already)

        Returns:
            DataFrame with additional enhanced probability columns
        """
        if options_df.empty:
            return options_df

        results = []

        for idx, row in options_df.iterrows():
            enhanced = self.calculate_enhanced_probability(
                ticker=row['ticker'],
                strike=row['strike'],
                current_price=row['current_stock_price'],
                days_to_expiration=row['days_to_expiration'],
                option_type=row['option_type'],
                black_scholes_prob=row.get('prob_otm')
            )

            results.append(enhanced)

        # Add new columns
        options_df['enhanced_prob_otm'] = [r['enhanced_prob_otm'] for r in results]
        options_df['prob_adjustment'] = [r['adjustment'] for r in results]
        options_df['composite_score'] = [r['composite_score'] for r in results]
        options_df['technical_score'] = [r['technical_score'] for r in results]
        options_df['fundamental_score'] = [r['fundamental_score'] for r in results]
        options_df['sentiment_score'] = [r['sentiment_score'] for r in results]
        options_df['event_risk_score'] = [r['event_risk_score'] for r in results]
        options_df['prob_confidence'] = [r['confidence'] for r in results]

        return options_df


if __name__ == "__main__":
    # Example usage
    analyzer = EnhancedProbabilityAnalyzer()

    # Test with a single option
    result = analyzer.calculate_enhanced_probability(
        ticker='AAPL',
        strike=250,
        current_price=260,
        days_to_expiration=45,
        option_type='put',
        black_scholes_prob=75.0  # Assume BS says 75% prob OTM
    )

    print("\nENHANCED PROBABILITY ANALYSIS")
    print("="*80)
    print(f"Black-Scholes Prob OTM: {result['black_scholes_prob_otm']:.1f}%")
    print(f"Enhanced Prob OTM: {result['enhanced_prob_otm']:.1f}%")
    print(f"Adjustment: {result['adjustment']:+.1f}%")
    print(f"\nComponent Scores:")
    print(f"  Technical Score: {result['technical_score']:.1f}/100")
    print(f"  Fundamental Score: {result['fundamental_score']:.1f}/100")
    print(f"  Sentiment Score: {result['sentiment_score']:.1f}/100")
    print(f"  Event Risk Score: {result['event_risk_score']:.1f}/100")
    print(f"  Composite Score: {result['composite_score']:.1f}/100")
    print(f"\nConfidence: {result['confidence'].upper()}")
