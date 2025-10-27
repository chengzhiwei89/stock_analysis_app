"""
Run ONLY Cash Secured Put Analysis
Quick script to run just the CSP scan without CC or Wheel
"""
from quick_start import quick_cash_secured_put_scan

if __name__ == "__main__":
    print("\n" + "="*80)
    print("CASH SECURED PUT SCANNER")
    print("Using safer filtering criteria from config.py")
    print("="*80)

    # Run CSP scan
    results = quick_cash_secured_put_scan()

    # Done
    print("\n" + "="*80)
    print("CSP Scan Complete!")
    print("="*80)

    if results is not None and not results.empty:
        print(f"\nFound {len(results)} cash secured put opportunities")
        print("\nRecommendations saved to: data/recommendations/")
    else:
        print("\nNo opportunities found matching your criteria.")
        print("Try adjusting settings in config.py:")
        print("  - Lower min_prob_otm (e.g., 65% instead of 70%)")
        print("  - Lower min_annual_return (e.g., 15% instead of 20%)")
        print("  - Increase max_days (e.g., 60 instead of 45)")
