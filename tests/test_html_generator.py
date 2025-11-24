# tests/test_html_generator.py

import pytest
import pandas as pd
from src.visualization.html_generator import HTMLDashboardGenerator

@pytest.fixture
def generator():
    return HTMLDashboardGenerator()

def test_generate_with_empty_and_mixed_data(generator, tmp_path):
    """
    Tests that the generate method handles a mix of empty and non-empty dataframes.
    This will cover many of the 'if df.empty' branches.
    """
    output_path = tmp_path / "dashboard.html"
    
    csp_df = pd.DataFrame({
        'ticker': ['CSP'], 
        'annual_return': [20], 
        'strike': [100], 
        'expiration': ['2025-12-19'],
        'days_to_expiration': [30],
        'premium_received': [2.5],
        'prob_otm': [75],
        'distance_pct': [-5.0]
    })
    # cc_df is empty
    wheel_df = pd.DataFrame({
        'ticker': ['WHEEL'], 'discount_pct': [8], 'current_price': [200], 'strike': [190], 
        'expiration': ['2025-12-26'], 'premium': [5.0], 'net_entry': [185.0], 'annual_return': [15.0]
    })
    # leaps_df is empty
    
    path = generator.generate(
        csp_results=csp_df,
        cc_results=pd.DataFrame(),
        wheel_results=wheel_df,
        leaps_results=None, # Explicitly test None
        output_path=str(output_path)
    )
    
    assert path == str(output_path)
    assert output_path.exists()
    
    # Check that the output contains titles for the non-empty sections
    content = output_path.read_text()
    assert "Cash Secured Puts" in content
    assert "Wheel Strategy" in content
    # Check that it contains the empty state message for the empty sections
    assert "No Covered Call opportunities" in content
    assert "No LEAPS Call Bet opportunities" in content

@pytest.mark.parametrize("formatter, invalid_input, expected", [
    (HTMLDashboardGenerator._format_currency, "not-a-number", "$0.00"),
    (HTMLDashboardGenerator._format_currency, None, "$0.00"),
    (HTMLDashboardGenerator._format_percent, "not-a-number", "0.0%"),
    (HTMLDashboardGenerator._format_percent, None, "0.0%"),
    (HTMLDashboardGenerator._format_date, "invalid-date", "invalid-date"),
    (HTMLDashboardGenerator._format_date, 123, "123"),
    (HTMLDashboardGenerator._get_risk_color, "not-a-number", "text-secondary"),
    (HTMLDashboardGenerator._get_risk_color, None, "text-secondary"),
])
def test_formatters_error_handling(formatter, invalid_input, expected):
    """Tests the except blocks in the static formatting methods."""
    assert formatter(invalid_input) == expected

def test_prepare_charts_with_missing_columns(generator):
    """
    Tests that chart preparation methods don't fail with missing columns.
    """
    # Test CSP charts
    csp_df = pd.DataFrame({'ticker': ['A'], 'strike': [100]}) # Missing annual_return, prob_otm
    csp_charts = generator._prepare_csp_charts(csp_df)
    assert 'return_distribution' not in csp_charts
    assert 'risk_reward_scatter' not in csp_charts
    # This part of the test will still run, as it only needs ticker and strike
    assert 'capital_requirements' in csp_charts

    # Test CC charts
    cc_df = pd.DataFrame({'ticker': ['B']}) # Missing annual_return
    cc_charts = generator._prepare_cc_charts(cc_df)
    assert 'return_distribution' not in cc_charts

    # Test Wheel charts
    wheel_df = pd.DataFrame({'ticker': ['C']}) # Missing discount_pct
    wheel_charts = generator._prepare_wheel_charts(wheel_df)
    assert 'discount_distribution' not in wheel_charts
