"""
Add Stock Position to Portfolio - Interactive Script
Simple way to add stock positions to your portfolio for covered call analysis
"""
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.portfolio.portfolio_manager import PortfolioManager


def add_stock_interactive():
    """Interactive stock position entry"""
    portfolio = PortfolioManager()

    print("\n" + "="*80)
    print("ADD STOCK POSITION TO PORTFOLIO")
    print("="*80)

    # Get position details
    print("\nEnter stock position details:")

    ticker = input("  Ticker (e.g., AAPL, NVDA): ").upper().strip()

    shares = int(input("  Number of Shares (e.g., 100): ").strip())

    cost_basis = float(input(f"  Cost Basis per share (e.g., 150.00): $").strip())

    purchase_date = input("  Purchase Date (YYYY-MM-DD, or press Enter for today): ").strip()
    if not purchase_date:
        purchase_date = datetime.now().strftime('%Y-%m-%d')

    notes = input("  Notes (optional, press Enter to skip): ").strip()

    # Calculate metrics
    total_cost = shares * cost_basis
    contracts_available = shares // 100

    # Confirm
    print("\n" + "-"*80)
    print("STOCK POSITION SUMMARY:")
    print(f"  Ticker: {ticker}")
    print(f"  Shares: {shares:,}")
    print(f"  Cost Basis: ${cost_basis:.2f} per share")
    print(f"  Total Cost: ${total_cost:,.2f}")
    print(f"  Purchase Date: {purchase_date}")

    if contracts_available > 0:
        print(f"\n  Covered Calls Available: {contracts_available} contract(s)")
        print(f"  (You can sell covered calls on this position)")
    else:
        print(f"\n  ⚠ Note: You need 100+ shares to sell covered calls")
        print(f"        Currently {100 - shares} shares short of 1 contract")

    if notes:
        print(f"\n  Notes: {notes}")
    print("-"*80)

    confirm = input("\nAdd this stock position to portfolio? (y/n): ").lower().strip()

    if confirm == 'y':
        portfolio.add_stock_position(
            ticker=ticker,
            shares=shares,
            cost_basis=cost_basis,
            purchase_date=purchase_date,
            notes=notes
        )
        print("\n✓ Stock position added successfully!")

        # Show covered call opportunities
        print("\n" + "="*80)
        print("COVERED CALL OPPORTUNITIES")
        print("="*80)

        cc_opps = portfolio.get_covered_call_opportunities()
        if not cc_opps.empty:
            print(f"\nYou can sell covered calls on these stocks:")
            for idx, stock in cc_opps.iterrows():
                print(f"\n  • {stock['ticker']}")
                print(f"    Shares: {stock['shares']:,} ({stock['contracts_available']} contracts available)")
                print(f"    Cost Basis: ${stock['cost_basis']:.2f}")
        else:
            print("\nNo stocks with 100+ shares for covered calls yet.")
            print("Add more shares to enable covered call strategies.")
    else:
        print("\nStock position not added.")

    # Ask if want to add another
    print("\n" + "="*80)
    another = input("Add another stock position? (y/n): ").lower().strip()
    if another == 'y':
        add_stock_interactive()


def view_portfolio():
    """View current stock and option portfolio"""
    portfolio = PortfolioManager()

    print("\n" + "="*80)
    print("CURRENT PORTFOLIO")
    print("="*80)

    # Show stocks
    stocks = portfolio.get_stocks_dataframe()
    if not stocks.empty:
        print(f"\n📊 STOCK POSITIONS ({len(stocks)}):")
        print("-"*80)
        for idx, stock in stocks.iterrows():
            total_value = stock['shares'] * stock['cost_basis']
            contracts = stock['shares'] // 100
            print(f"\n  {idx + 1}. {stock['ticker']}")
            print(f"     Shares: {stock['shares']:,} | Cost: ${stock['cost_basis']:.2f}")
            print(f"     Total Value: ${total_value:,.2f}")
            print(f"     Purchase Date: {stock['purchase_date']}")
            if contracts > 0:
                print(f"     ✓ Can sell {contracts} covered call contract(s)")
            if stock.get('notes'):
                print(f"     Notes: {stock['notes']}")
    else:
        print("\n📊 STOCK POSITIONS: None")
        print("     Use option 1 to add stock positions")

    # Show options
    options = portfolio.get_options_dataframe(status='open')
    if not options.empty:
        print(f"\n\n📈 OPTION POSITIONS ({len(options)} open):")
        print("-"*80)
        for idx, pos in options.iterrows():
            capital = pos['strike'] * 100 * pos['contracts'] if pos['strategy'] == 'cash_secured_put' else 0
            print(f"\n  {idx + 1}. {pos['ticker']} ${pos['strike']:.0f} {pos['option_type'].upper()}")
            print(f"     Expires: {pos['expiration']} | {pos['contracts']} contracts")
            print(f"     Premium: ${pos['premium']:.2f}/share (${pos['premium'] * 100 * pos['contracts']:.2f} total)")
            print(f"     Strategy: {pos['strategy'].replace('_', ' ').title()}")
            if capital > 0:
                print(f"     Capital Required: ${capital:,.0f}")
    else:
        print(f"\n\n📈 OPTION POSITIONS: None")
        print("     Use add_options_position.py to add option positions")

    # Show covered call opportunities
    cc_opps = portfolio.get_covered_call_opportunities()
    if not cc_opps.empty:
        print(f"\n\n💡 COVERED CALL OPPORTUNITIES ({len(cc_opps)}):")
        print("-"*80)
        for idx, stock in cc_opps.iterrows():
            print(f"\n  • {stock['ticker']}: {stock['contracts_available']} contract(s) available")
            print(f"    ({stock['shares']} shares @ ${stock['cost_basis']:.2f})")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("STOCK POSITION MANAGER")
    print("="*80)
    print("\nManage your stock holdings for covered call strategies")
    print("\nChoose an option:")
    print("  1. Add stock position (for covered calls)")
    print("  2. View current portfolio")
    print("  3. Exit")

    choice = input("\nYour choice (1-3): ").strip()

    if choice == '1':
        add_stock_interactive()
    elif choice == '2':
        view_portfolio()
    elif choice == '3':
        print("\nExiting...")
    else:
        print("\nInvalid choice.")

    print("\n" + "="*80)
    print("\nNext steps:")
    print("  • Add options: python add_options_position.py")
    print("  • Analyze positions: python run_position_analysis.py")
    print("  • Find covered calls: python main.py")
    print("="*80 + "\n")
