# tests/test_recommendations_manager.py

import pytest
import pandas as pd
from datetime import datetime, timedelta
import json
import os

from src.data.recommendations_manager import RecommendationsManager

@pytest.fixture
def sample_df():
    """A sample DataFrame to use for saving."""
    return pd.DataFrame({'ticker': ['TEST'], 'strike': [100], 'premium': [1.5]})

def test_save_and_load_csp(tmp_path, sample_df):
    """
    Tests the basic save and load functionality for CSP recommendations.
    tmp_path is a pytest fixture that provides a temporary directory.
    """
    # 1. Setup
    reco_dir = tmp_path / "recommendations"
    manager = RecommendationsManager(recommendations_dir=str(reco_dir))
    
    # 2. Save the recommendations
    csv_path = manager.save_cash_secured_put_recommendations(
        results=sample_df,
        tickers=['TEST'],
        criteria={'min_premium': 1.0}
    )
    
    assert csv_path != ""
    
    # 3. Verify files were created
    filename_base = os.path.basename(csv_path).replace('.csv', '')
    meta_path = reco_dir / f"{filename_base}_meta.json"

    assert os.path.exists(csv_path)
    assert os.path.exists(meta_path)
    
    # 4. Verify metadata content
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
    
    assert metadata['strategy'] == 'cash_secured_put'
    assert metadata['num_opportunities'] == 1
    assert metadata['tickers'] == ['TEST']
    
    # 5. Load the recommendation and verify its content
    loaded_df = manager.load_recommendation(os.path.basename(csv_path))
    
    assert not loaded_df.empty
    pd.testing.assert_frame_equal(sample_df, loaded_df)

def test_save_empty_dataframe(tmp_path):
    """
    Tests that saving an empty DataFrame does nothing and returns an empty string.
    """
    manager = RecommendationsManager(recommendations_dir=str(tmp_path))
    result_path = manager.save_cash_secured_put_recommendations(
        results=pd.DataFrame(),
        tickers=['TEST'],
        criteria={}
    )
    assert result_path == ""

def test_load_nonexistent_file(tmp_path):
    """
    Tests that trying to load a file that doesn't exist returns an empty DataFrame.
    """
    manager = RecommendationsManager(recommendations_dir=str(tmp_path))
    loaded_df = manager.load_recommendation("nonexistent_file.csv")
    assert loaded_df.empty

@pytest.fixture
def setup_files(tmp_path):
    """Creates a set of dummy recommendation files for load/list testing."""
    reco_dir = tmp_path / "recommendations"
    os.makedirs(reco_dir)
    
    # Create some files with different timestamps
    # Old file
    (reco_dir / "csp_OLD_20230101_120000.csv").touch()
    with open(reco_dir / "csp_OLD_20230101_120000_meta.json", 'w') as f:
        json.dump({'strategy': 'cash_secured_put', 'tickers': ['OLD'], 'timestamp': '20230101_120000', 'csv_file': 'csp_OLD_20230101_120000.csv', 'num_opportunities': 1}, f)

    # Newer file
    (reco_dir / "csp_NEW_20230102_120000.csv").touch()
    with open(reco_dir / "csp_NEW_20230102_120000_meta.json", 'w') as f:
        json.dump({'strategy': 'cash_secured_put', 'tickers': ['NEW'], 'timestamp': '20230102_120000', 'csv_file': 'csp_NEW_20230102_120000.csv', 'num_opportunities': 1}, f)
        
    # A different strategy
    (reco_dir / "cc_TICK_20230102_130000.csv").touch()
    with open(reco_dir / "cc_TICK_20230102_130000_meta.json", 'w') as f:
        json.dump({'strategy': 'covered_call', 'tickers': ['TICK'], 'timestamp': '20230102_130000', 'csv_file': 'cc_TICK_20230102_130000.csv', 'num_opportunities': 1}, f)
        
    return reco_dir

def test_save_all_recommendations(tmp_path, sample_df):
    """Tests that an excel file is created with the correct sheets."""
    manager = RecommendationsManager(recommendations_dir=str(tmp_path))
    manager.save_all_recommendations(
        cc_results=sample_df, 
        csp_results=sample_df,
        tickers=['TEST']
    )
    
    # Find the created excel file
    excel_files = list(tmp_path.glob("*.xlsx"))
    assert len(excel_files) == 1
    
    # Check if it has the correct sheets
    xls = pd.ExcelFile(excel_files[0])
    assert 'Covered_Calls' in xls.sheet_names
    assert 'Cash_Secured_Puts' in xls.sheet_names
    assert 'Wheel_Strategy' not in xls.sheet_names

def test_list_and_load_latest(setup_files, mocker):
    """Tests listing and loading the latest recommendations."""
    manager = RecommendationsManager(recommendations_dir=str(setup_files))
    
    # Mock the csv reader to avoid EmptyDataError with our dummy files
    mock_read = mocker.patch('pandas.read_csv', return_value=pd.DataFrame({'a': [1]}))
    
    # List all
    all_recs = manager.list_recommendations()
    assert len(all_recs) == 3
    
    # Filter by strategy
    csp_recs = manager.list_recommendations(strategy='csp')
    assert len(csp_recs) == 2
    
    # Filter by ticker
    new_recs = manager.list_recommendations(ticker='NEW')
    assert len(new_recs) == 1
    assert new_recs[0]['tickers'] == ['NEW']
    
    # Load latest csp - should be the 'NEW' one from 2023-01-02
    latest_df = manager.load_latest_recommendation(strategy='csp')
    
    assert not latest_df.empty
    # Check that read_csv was called with the path of the NEWEST file
    mock_read.assert_called_once()
    call_args = mock_read.call_args[0]
    assert 'csp_NEW_20230102_120000.csv' in call_args[0]

def test_get_summary(setup_files):
    """Tests the get_summary method."""
    manager = RecommendationsManager(recommendations_dir=str(setup_files))
    summary = manager.get_summary()
    assert "Total Recommendations: 3" in summary
    assert "CASH SECURED PUT" in summary
    assert "COVERED CALL" in summary

def test_cleanup_old_recommendations(setup_files):
    """Tests that old files are correctly removed."""
    manager = RecommendationsManager(recommendations_dir=str(setup_files))
    
    # Files are from 2023, so keeping anything from the last year should delete them.
    # Keep days is calculated from datetime.now()
    days_since_2023 = (datetime.now() - datetime(2023, 1, 3)).days
    manager.cleanup_old_recommendations(keep_days=days_since_2023 - 1)
    
    # All files should be gone
    remaining_files = os.listdir(setup_files)
    assert len(remaining_files) == 0
