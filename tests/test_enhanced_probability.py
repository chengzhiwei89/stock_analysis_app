# tests/test_enhanced_probability.py

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.analysis.enhanced_probability import EnhancedProbabilityAnalyzer

# --- Fixtures ---

@pytest.fixture
def analyzer():
    """Returns a clean instance of the analyzer for each test."""
    return EnhancedProbabilityAnalyzer()

@pytest.fixture
def mock_yfinance(mocker):
    """Fixture to mock the yfinance.Ticker object."""
    mock = mocker.patch('src.analysis.enhanced_probability.yf.Ticker', autospec=True)
    instance = mock.return_value
    instance.info = {
        'fiftyTwoWeekLow': 100.0, 'fiftyTwoWeekHigh': 200.0, 'regularMarketVolume': 1_000_000,
        'averageVolume': 800_000, 'beta': 1.1, 'trailingPE': 25.0, 'forwardPE': 20.0,
        'profitMargins': 0.2, 'returnOnEquity': 0.18, 'revenueGrowth': 0.15, 'earningsGrowth': 0.12,
        'debtToEquity': 80.0, 'recommendationKey': 'buy', 'recommendationMean': 2.2,
        'targetMeanPrice': 210.0, 'numberOfAnalystOpinions': 25, 'dividendYield': 0.015
    }
    hist_dates = pd.to_datetime(pd.date_range(end=datetime.now(), periods=120, freq='D'))
    hist_df = pd.DataFrame({'Close': np.linspace(140, 180, 120)}, index=hist_dates)
    hist_df.iloc[-1, hist_df.columns.get_loc('Close')] = hist_df.iloc[-2]['Close'] + 1 
    instance.history.return_value = hist_df
    instance.calendar = {'Earnings Date': [datetime.now() + timedelta(days=50)]}
    return mock

@pytest.fixture
def baseline_tech_data():
    return {
        'current_price': 150, 'sma_20': 145, 'sma_50': 140, 'sma_200': 130, '52w_low': 100,
        '52w_high': 160, 'volume': 1_000_000, 'avg_volume': 800_000, 'hist': None
    }

@pytest.fixture
def baseline_fundamental_data():
    return {
        'trailing_pe': 25.0, 'forward_pe': 20.0, 'profit_margins': 0.2, 'roe': 0.18,
        'revenue_growth': 0.15, 'earnings_growth': 0.12, 'debt_to_equity': 80.0, 'beta': 1.1
    }

@pytest.fixture
def baseline_sentiment_data():
    return {
        'recommendation_mean': 2.2, 'target_mean_price': 180.0, 
        'current_price': 150.0, 'num_analysts': 25
    }

# --- Tests for get_stock_data ---

def test_get_stock_data_happy_path(analyzer, mock_yfinance):
    data = analyzer.get_stock_data('TEST')
    assert data is not None
    assert 'sma_50' in data
    analyzer.get_stock_data('TEST')
    mock_yfinance.assert_called_once()
    analyzer.get_stock_data('TEST', force_refresh=True)
    assert mock_yfinance.call_count == 2

def test_get_stock_data_empty_history(analyzer, mock_yfinance):
    mock_yfinance.return_value.history.return_value = pd.DataFrame()
    data = analyzer.get_stock_data('NOHIST')
    assert data is None

# --- Tests for calculate_technical_score ---

def test_technical_score_neutral(analyzer):
    assert analyzer.calculate_technical_score(None, strike=100) == 50

def test_technical_score_strong_uptrend(analyzer, baseline_tech_data):
    score = analyzer.calculate_technical_score(baseline_tech_data, strike=130)
    assert score == 80 # 50 + 15 (trend) + 5 (dist) + 5 (range) + 5 (strike)

def test_technical_score_strong_downtrend(analyzer, baseline_tech_data):
    data = baseline_tech_data.copy()
    data.update({'current_price': 130, 'sma_20': 135, 'sma_50': 140})
    score = analyzer.calculate_technical_score(data, strike=120)
    assert score == 38

def test_technical_score_itm_put(analyzer, baseline_tech_data):
    score = analyzer.calculate_technical_score(baseline_tech_data, strike=160)
    assert score == 65

def test_technical_score_volume(analyzer, baseline_tech_data):
    base_score = analyzer.calculate_technical_score(baseline_tech_data.copy(), strike=130)
    
    # Test Rally
    rally_data = baseline_tech_data.copy()
    rally_data['volume'] = 2_000_000
    rally_data['hist'] = pd.DataFrame({'Close': [148, 150]})
    rally_score = analyzer.calculate_technical_score(rally_data, strike=130)
    assert rally_score == base_score + 5

    # Test Selloff
    selloff_data = baseline_tech_data.copy()
    selloff_data['volume'] = 2_000_000
    selloff_data['hist'] = pd.DataFrame({'Close': [152, 150]})
    selloff_score = analyzer.calculate_technical_score(selloff_data, strike=130)
    assert selloff_score == base_score - 5

# --- Tests for calculate_fundamental_score ---

def test_fundamental_score_neutral(analyzer):
    assert analyzer.calculate_fundamental_score(None) == 50

def test_fundamental_score_good_fundamentals(analyzer, baseline_fundamental_data):
    score = analyzer.calculate_fundamental_score(baseline_fundamental_data)
    assert score == 81 # 50 + 10(val) + 5(margin) + 3(roe) + 3(rev) + 5(earn) + 5(debt) + 5(beta)

def test_fundamental_score_poor_fundamentals(analyzer):
    data = {'forward_pe': 60, 'profit_margins': 0.02, 'roe': 0.01, 'revenue_growth': -0.1, 
            'earnings_growth': -0.1, 'debt_to_equity': 250, 'beta': 1.8}
    score = analyzer.calculate_fundamental_score(data)
    assert score == 10

# --- Tests for calculate_sentiment_score ---

def test_sentiment_score_neutral(analyzer):
    assert analyzer.calculate_sentiment_score(None) == 50

def test_sentiment_score_positive_sentiment(analyzer, baseline_sentiment_data):
    score = analyzer.calculate_sentiment_score(baseline_sentiment_data)
    assert score == 73 # 50 + 10 (rec) + 10 (upside) + 3 (analysts)

def test_sentiment_score_negative_sentiment(analyzer, baseline_sentiment_data):
    data = baseline_sentiment_data.copy()
    data.update({'recommendation_mean': 4.8, 'target_mean_price': 130.0, 'num_analysts': 3})
    score = analyzer.calculate_sentiment_score(data)
    assert score == 10 # 50 - 20 - 15 - 5

# --- Tests for calculate_event_risk_score ---

def test_event_risk_score_neutral(analyzer):
    assert analyzer.calculate_event_risk_score(None, 30) == 50

def test_event_risk_no_risk(analyzer):
    assert analyzer.calculate_event_risk_score({'next_earnings': None}, 30) == 100
    assert analyzer.calculate_event_risk_score({'next_earnings': datetime.now() + timedelta(days=100)}, 30) == 100

@pytest.mark.parametrize("days_to_earnings, expected_penalty", [
    (25, 10), (10, 20), (5, 30)
])
def test_event_risk_various_scenarios(analyzer, days_to_earnings, expected_penalty):
    data = {'next_earnings': datetime.now() + timedelta(days=days_to_earnings)}
    score = analyzer.calculate_event_risk_score(data, days_to_expiration=40)
    assert score == 100 - expected_penalty

# --- Tests for Orchestrator Methods ---

def test_calculate_enhanced_probability(analyzer, mocker):
    mocker.patch.object(analyzer, 'get_stock_data', return_value={'stub': 'data'})
    mocker.patch.object(analyzer, 'calculate_technical_score', return_value=80)
    mocker.patch.object(analyzer, 'calculate_fundamental_score', return_value=70)
    mocker.patch.object(analyzer, 'calculate_sentiment_score', return_value=60)
    mocker.patch.object(analyzer, 'calculate_event_risk_score', return_value=90)

    result = analyzer.calculate_enhanced_probability('TICK', 100, 110, 30, 'put', 75.0)

    # composite = 80*0.35 + 70*0.25 + 60*0.20 + 90*0.20 = 28 + 17.5 + 12 + 18 = 75.5
    # adjustment = ((75.5 - 50) / 50) * 15 = 7.65
    # enhanced_prob = 75.0 + 7.65 = 82.65
    assert result['composite_score'] == 75.5
    assert abs(result['adjustment'] - 7.65) < 0.01
    assert abs(result['enhanced_prob_otm'] - 82.65) < 0.01

def test_enrich_options_dataframe(analyzer, mocker):
    mock_calc = mocker.patch.object(analyzer, 'calculate_enhanced_probability', return_value={'enhanced_prob_otm': 85.0, 'adjustment': 10.0, 'composite_score': 83.3, 'technical_score': 80, 'fundamental_score': 70, 'sentiment_score': 60, 'event_risk_score': 90, 'confidence': 'high'})
    
    df = pd.DataFrame({
        'ticker': ['TICK1'], 'strike': [100], 'current_stock_price': [110], 
        'days_to_expiration': [30], 'option_type': ['put'], 'prob_otm': [75.0]
    })
    
    result_df = analyzer.enrich_options_dataframe(df)

    mock_calc.assert_called_once()
    assert 'enhanced_prob_otm' in result_df.columns
    assert result_df.iloc[0]['enhanced_prob_otm'] == 85.0