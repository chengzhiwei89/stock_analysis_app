"""
How to Access and Save DataFrames
Complete guide to working with analysis results
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.data.option_extractor import OptionDataExtractor
from src.strategies.covered_call import CoveredCallAnalyzer
from src.strategies.cash_secured_put import CashSecuredPutAnalyzer
import pandas as pd


# ============================================================================
# METHOD 1: Run Fresh Analysis (Results in Memory)
# ============================================================================
def method_1_fresh_analysis():
    """Run fresh analysis - results are DataFrames in memory"""
    print("="*80)
    print("METHOD 1: FRESH ANALYSIS (DataFrames in Memory)")
    print("="*80 + "\n")

    # Initialize
    extractor = OptionDataExtractor()
    cc_analyzer = CoveredCallAnalyzer()
    csp_analyzer = CashSecuredPutAnalyzer()

    # Fetch fresh options data
    print("Fetching options data...")
    options_data = extractor.fetch_and_store_options(['NVDA'], num_expirations=2)

    # Run covered call analysis - returns DataFrame
    print("Analyzing covered calls...")
    cc_results = cc_analyzer.get_top_opportunities(
        options_data,
        min_premium=1.0,
        min_annual_return=20.0,
        max_days=45,
        top_n=10
    )

    # Run cash secured put analysis - returns DataFrame
    print("Analyzing cash secured puts...")
    csp_results = csp_analyzer.get_top_opportunities(
        options_data,
        min_premium=1.0,
        min_annual_return=20.0,
        max_days=45,
        top_n=10
    )

    print(f"\nCovered Call opportunities: {len(cc_results)} rows")
    print(f"Cash Secured Put opportunities: {len(csp_results)} rows")

    # These are pandas DataFrames - you can work with them directly
    print("\nDataFrame type:", type(cc_results))
    print("Columns:", list(cc_results.columns))

    return cc_results, csp_results


# ============================================================================
# METHOD 2: Load Previously Fetched Raw Data
# ============================================================================
def method_2_load_saved_data():
    """Load previously saved raw options data and analyze it"""
    print("\n" + "="*80)
    print("METHOD 2: LOAD SAVED RAW DATA")
    print("="*80 + "\n")

    extractor = OptionDataExtractor()

    # Load the most recent saved data
    print("Loading latest saved options data...")
    options_data = extractor.load_latest_data()

    if options_data.empty:
        print("No saved data found. Run some analysis first!")
        return None, None

    print(f"Loaded {len(options_data)} options from disk")
    print(f"Tickers: {options_data['ticker'].unique()}")
    print(f"Date fetched: {options_data['fetch_date'].iloc[0]}")

    # Now analyze the loaded data
    cc_analyzer = CoveredCallAnalyzer()
    cc_results = cc_analyzer.get_top_opportunities(
        options_data,
        min_premium=1.0,
        min_annual_return=20.0,
        max_days=45,
        top_n=10
    )

    print(f"\nFound {len(cc_results)} covered call opportunities")

    return options_data, cc_results


# ============================================================================
# METHOD 3: Save Analysis Results for Later
# ============================================================================
def method_3_save_results(cc_results, csp_results):
    """Save analysis results to CSV for later use"""
    print("\n" + "="*80)
    print("METHOD 3: SAVE ANALYSIS RESULTS")
    print("="*80 + "\n")

    if cc_results is None or cc_results.empty:
        print("No results to save")
        return

    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save covered calls
    cc_file = f"data/option_chains/cc_opportunities_{timestamp}.csv"
    cc_results.to_csv(cc_file, index=False)
    print(f"Saved covered calls to: {cc_file}")
    print(f"  Rows: {len(cc_results)}")

    # Save cash secured puts
    if csp_results is not None and not csp_results.empty:
        csp_file = f"data/option_chains/csp_opportunities_{timestamp}.csv"
        csp_results.to_csv(csp_file, index=False)
        print(f"Saved cash secured puts to: {csp_file}")
        print(f"  Rows: {len(csp_results)}")

    # You can also save as Excel
    excel_file = f"data/option_chains/opportunities_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_file) as writer:
        cc_results.to_excel(writer, sheet_name='Covered_Calls', index=False)
        if csp_results is not None and not csp_results.empty:
            csp_results.to_excel(writer, sheet_name='Cash_Secured_Puts', index=False)
    print(f"\nSaved to Excel: {excel_file}")

    return cc_file, csp_file, excel_file


# ============================================================================
# METHOD 4: Load Previously Saved Analysis Results
# ============================================================================
def method_4_load_saved_results():
    """Load previously saved analysis results"""
    print("\n" + "="*80)
    print("METHOD 4: LOAD SAVED ANALYSIS RESULTS")
    print("="*80 + "\n")

    import glob

    # Find most recent saved analysis
    cc_files = glob.glob("data/option_chains/cc_opportunities_*.csv")

    if not cc_files:
        print("No saved analysis files found.")
        print("Run method_3_save_results() first to save some results.")
        return None

    # Load the most recent one
    latest_file = sorted(cc_files)[-1]
    print(f"Loading: {latest_file}")

    cc_results = pd.read_csv(latest_file)
    print(f"Loaded {len(cc_results)} opportunities")
    print(f"Columns: {list(cc_results.columns)}")

    return cc_results


# ============================================================================
# METHOD 5: Working with DataFrames Directly
# ============================================================================
def method_5_dataframe_operations(cc_results):
    """Examples of working with the DataFrames"""
    print("\n" + "="*80)
    print("METHOD 5: WORKING WITH DATAFRAMES")
    print("="*80 + "\n")

    if cc_results is None or cc_results.empty:
        print("No results available")
        return

    # Example 1: Filter for specific ticker
    print("Example 1: Filter for NVDA only")
    nvda_only = cc_results[cc_results['ticker'] == 'NVDA']
    print(f"NVDA opportunities: {len(nvda_only)}")

    # Example 2: Filter by annual return
    print("\nExample 2: Only opportunities > 30% annual return")
    high_return = cc_results[cc_results['annual_return'] > 30]
    print(f"High return opportunities: {len(high_return)}")

    # Example 3: Sort by different criteria
    print("\nExample 3: Top 5 by premium")
    top_premium = cc_results.nlargest(5, 'premium_received')
    print(top_premium[['ticker', 'strike', 'premium_received', 'annual_return']])

    # Example 4: Get specific data
    print("\nExample 4: Get best opportunity details")
    best = cc_results.iloc[0]
    print(f"Ticker: {best['ticker']}")
    print(f"Strike: ${best['strike']:.2f}")
    print(f"Expiration: {best['expiration']}")
    print(f"Premium: ${best['premium_received']:.2f}")
    print(f"Annual Return: {best['annual_return']:.1f}%")

    # Example 5: Calculate custom metrics
    print("\nExample 5: Custom calculations")
    cc_results['premium_per_contract'] = cc_results['premium_received'] * 100
    cc_results['potential_income_5_contracts'] = cc_results['premium_per_contract'] * 5
    print(cc_results[['ticker', 'strike', 'premium_per_contract', 'potential_income_5_contracts']].head(3))

    # Example 6: Export subset
    print("\nExample 6: Export only NVDA opportunities")
    nvda_only.to_csv('data/option_chains/nvda_cc_only.csv', index=False)
    print("Saved NVDA-only opportunities to: data/option_chains/nvda_cc_only.csv")


# ============================================================================
# METHOD 6: Direct Python Access (Interactive Use)
# ============================================================================
def method_6_interactive_example():
    """Example for interactive Python/Jupyter use"""
    print("\n" + "="*80)
    print("METHOD 6: INTERACTIVE PYTHON EXAMPLE")
    print("="*80 + "\n")

    print("""
For interactive use (Python console or Jupyter):

>>> from src.data.option_extractor import OptionDataExtractor
>>> from src.strategies.covered_call import CoveredCallAnalyzer
>>>
>>> # Fetch data
>>> extractor = OptionDataExtractor()
>>> options = extractor.fetch_and_store_options(['NVDA'])
>>>
>>> # Analyze
>>> analyzer = CoveredCallAnalyzer()
>>> results = analyzer.get_top_opportunities(options, min_annual_return=20)
>>>
>>> # Now you have a DataFrame you can explore:
>>> results.head()
>>> results['annual_return'].describe()
>>> results[results['strike'] > 140]
>>> results.to_csv('my_results.csv')
>>>
>>> # Or just work with it in memory:
>>> for idx, row in results.iterrows():
...     print(f"{row['ticker']} ${row['strike']}: {row['annual_return']:.1f}%")
    """)


# ============================================================================
# MAIN DEMO
# ============================================================================
def main():
    """Run all examples"""
    print("\n" + "#"*80)
    print("# HOW TO ACCESS AND SAVE DATAFRAMES")
    print("#"*80)

    # Method 1: Fresh analysis
    cc_results, csp_results = method_1_fresh_analysis()

    # Method 2: Load saved data
    options_data, loaded_results = method_2_load_saved_data()

    # Method 3: Save results
    if cc_results is not None and not cc_results.empty:
        method_3_save_results(cc_results, csp_results)

    # Method 4: Load saved results
    loaded_analysis = method_4_load_saved_results()

    # Method 5: DataFrame operations
    if cc_results is not None and not cc_results.empty:
        method_5_dataframe_operations(cc_results)

    # Method 6: Interactive example
    method_6_interactive_example()

    print("\n\n" + "#"*80)
    print("# SUMMARY: WHERE ARE DATAFRAMES?")
    print("#"*80)
    print("""
1. ANALYSIS RESULTS (CC/CSP/Wheel):
   Location: IN MEMORY (RAM) - not automatically saved
   Access:   Run analysis functions, they return DataFrames
   Save:     Manually with results.to_csv() or results.to_excel()

2. RAW OPTIONS DATA:
   Location: data/option_chains/options_data_YYYYMMDD_HHMMSS.csv
   Access:   extractor.load_latest_data()
   Auto-saved: Yes, every time you fetch options

3. PORTFOLIO DATA:
   Location: data/portfolio/portfolio.json
   Access:   portfolio.get_stocks_dataframe() or get_options_dataframe()
   Auto-saved: Yes, when you add/modify positions

KEY POINT:
Analysis results are TEMPORARY (in memory) unless you save them!
Raw data is AUTOMATICALLY saved for you.

BEST PRACTICE:
- Let raw data auto-save (it does)
- Run fresh analysis when you need it (fast)
- Save important analysis results manually if needed
- Use extractor.load_latest_data() to avoid re-fetching
    """)

    print("\n" + "#"*80)
    print("# QUICK REFERENCE")
    print("#"*80)
    print("""
# Run analysis and get DataFrame:
results = analyzer.get_top_opportunities(options_data, ...)

# Save DataFrame to CSV:
results.to_csv('my_results.csv', index=False)

# Save DataFrame to Excel:
results.to_excel('my_results.xlsx', index=False)

# Load CSV back into DataFrame:
results = pd.read_csv('my_results.csv')

# Load latest raw options data:
options_data = extractor.load_latest_data()

# List all saved files:
import glob
print(glob.glob('data/option_chains/*.csv'))
    """)


if __name__ == "__main__":
    main()
