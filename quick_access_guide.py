"""
QUICK ACCESS GUIDE - Copy and paste these examples
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# ============================================================================
# EXAMPLE 1: Run Analysis and Get Results (DataFrame in memory)
# ============================================================================
def example_1_run_analysis():
    """Most common use case"""
    from src.data.option_extractor import OptionDataExtractor
    from src.strategies.covered_call import CoveredCallAnalyzer

    # Fetch options
    extractor = OptionDataExtractor()
    options_data = extractor.fetch_and_store_options(['NVDA'], num_expirations=3)

    # Analyze covered calls - returns DataFrame
    analyzer = CoveredCallAnalyzer()
    cc_results = analyzer.get_top_opportunities(
        options_data,
        min_premium=1.0,
        min_annual_return=20.0,
        max_days=45
    )

    # cc_results is now a DataFrame in memory
    print(f"Found {len(cc_results)} opportunities")
    print(cc_results.head())

    # IMPORTANT: This DataFrame is NOT saved automatically!
    # To save it:
    cc_results.to_csv('my_cc_results.csv', index=False)

    return cc_results


# ============================================================================
# EXAMPLE 2: Load Previously Fetched Data (avoid re-fetching)
# ============================================================================
def example_2_load_saved_options():
    """Use already-fetched data"""
    from src.data.option_extractor import OptionDataExtractor
    from src.strategies.covered_call import CoveredCallAnalyzer

    # Load the latest saved options data (from data/option_chains/)
    extractor = OptionDataExtractor()
    options_data = extractor.load_latest_data()

    # Now analyze it
    analyzer = CoveredCallAnalyzer()
    cc_results = analyzer.get_top_opportunities(
        options_data,
        min_premium=1.0,
        min_annual_return=20.0,
        max_days=45
    )

    return cc_results


# ============================================================================
# EXAMPLE 3: For Your NVDA Position
# ============================================================================
def example_3_nvda_covered_calls():
    """Analyze covered calls for your NVDA position"""
    from src.data.option_extractor import OptionDataExtractor
    from src.strategies.covered_call import CoveredCallAnalyzer

    extractor = OptionDataExtractor()
    analyzer = CoveredCallAnalyzer()

    # Fetch NVDA options
    print("Fetching NVDA options...")
    options_data = extractor.fetch_and_store_options(['NVDA'], num_expirations=4)

    # Filter for NVDA calls only
    nvda_calls = options_data[
        (options_data['ticker'] == 'NVDA') &
        (options_data['option_type'] == 'call')
    ]

    # Analyze
    results = analyzer.get_top_opportunities(
        options_data,
        min_premium=1.0,
        min_annual_return=15.0,
        max_days=45,
        top_n=20
    )

    # Print results
    print(f"\nTop NVDA Covered Call Opportunities:")
    print("="*80)
    for idx, row in results.head(10).iterrows():
        print(f"{row['expiration']:12} ${row['strike']:6.0f} strike: "
              f"${row['premium_received']:5.2f} premium, "
              f"{row['annual_return']:5.1f}% annual return")

    # Save for Excel
    results.to_excel('nvda_covered_calls.xlsx', index=False)
    print(f"\nSaved to: nvda_covered_calls.xlsx")

    return results


# ============================================================================
# EXAMPLE 4: Access Your Portfolio
# ============================================================================
def example_4_access_portfolio():
    """Access your portfolio data"""
    from src.portfolio.portfolio_manager import PortfolioManager

    portfolio = PortfolioManager()

    # Get stocks as DataFrame
    stocks = portfolio.get_stocks_dataframe()
    print("Your stocks:")
    print(stocks)

    # Get options as DataFrame
    options = portfolio.get_options_dataframe(status='open')
    print("\nYour open options:")
    print(options)

    # These are DataFrames you can work with
    if not stocks.empty:
        total_shares = stocks['shares'].sum()
        print(f"\nTotal shares across all positions: {total_shares}")

    return stocks, options


# ============================================================================
# EXAMPLE 5: Check What Files Exist
# ============================================================================
def example_5_list_saved_files():
    """See what data files you have"""
    import glob

    print("Saved options data files:")
    print("="*80)
    options_files = glob.glob('data/option_chains/options_data_*.csv')
    for f in sorted(options_files)[-5:]:  # Show last 5
        print(f"  {f}")

    print("\nPortfolio files:")
    print("="*80)
    portfolio_files = glob.glob('data/portfolio/*.json')
    for f in portfolio_files:
        print(f"  {f}")


# ============================================================================
# RUN EXAMPLES
# ============================================================================
if __name__ == "__main__":
    print("\n" + "#"*80)
    print("# QUICK ACCESS GUIDE")
    print("#"*80)

    print("\n[Example 1] Run fresh analysis...")
    # results = example_1_run_analysis()

    print("\n[Example 2] Load saved options data...")
    # results = example_2_load_saved_options()

    print("\n[Example 3] Analyze NVDA covered calls (YOUR POSITION)...")
    results = example_3_nvda_covered_calls()

    print("\n[Example 4] Access portfolio...")
    # stocks, options = example_4_access_portfolio()

    print("\n[Example 5] List saved files...")
    example_5_list_saved_files()

    print("\n" + "#"*80)
    print("# DONE!")
    print("#"*80)
