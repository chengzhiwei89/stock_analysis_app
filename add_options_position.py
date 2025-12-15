"""
Add Position to Portfolio - Interactive Script
Simple way to add option positions to your portfolio
"""
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.portfolio.portfolio_manager import PortfolioManager


def add_position_interactive():
    """Interactive position entry"""
    portfolio = PortfolioManager()

    print("\n" + "="*80)
    print("ADD OPTION POSITION TO PORTFOLIO")
    print("="*80)

    # Get position details
    print("\nEnter position details:")

    ticker = input("  Ticker (e.g., AAPL): ").upper().strip()

    print("\n  Option Type:")
    print("    1. Put (Cash Secured Put)")
    print("    2. Call (Covered Call)")
    option_choice = input("  Choice (1 or 2): ").strip()
    option_type = 'put' if option_choice == '1' else 'call'
    strategy = 'cash_secured_put' if option_type == 'put' else 'covered_call'

    strike = float(input(f"\n  Strike Price (e.g., 160.00): $").strip())

    expiration = input("  Expiration Date (YYYY-MM-DD, e.g., 2025-01-17): ").strip()

    contracts = int(input("  Number of Contracts (e.g., 1): ").strip())

    premium = float(input(f"  Premium Received per share (e.g., 2.50): $").strip())

    open_date = input("  Open Date (YYYY-MM-DD, or press Enter for today): ").strip()
    if not open_date:
        open_date = datetime.now().strftime('%Y-%m-%d')

    notes = input("  Notes (optional, press Enter to skip): ").strip()

    # Confirm
    print("\n" + "-"*80)
    print("POSITION SUMMARY:")
    print(f"  Ticker: {ticker}")
    print(f"  Type: {option_type.upper()} ({strategy.replace('_', ' ').title()})")
    print(f"  Strike: ${strike:.2f}")
    print(f"  Expiration: {expiration}")
    print(f"  Contracts: {contracts}")
    print(f"  Premium: ${premium:.2f} per share")
    print(f"  Total Premium: ${premium * 100 * contracts:.2f}")

    if strategy == 'cash_secured_put':
        capital_required = strike * 100 * contracts
        print(f"  Capital Required: ${capital_required:,.2f}")

    print(f"  Open Date: {open_date}")
    if notes:
        print(f"  Notes: {notes}")
    print("-"*80)

    confirm = input("\nAdd this position to portfolio? (y/n): ").lower().strip()

    if confirm == 'y':
        portfolio.add_option_position(
            ticker=ticker,
            option_type=option_type,
            strike=strike,
            expiration=expiration,
            contracts=contracts,
            premium=premium,
            open_date=open_date,
            strategy=strategy,
            notes=notes
        )
        print("\n✓ Position added successfully!")

        # Show current portfolio
        print("\n" + "="*80)
        print("CURRENT PORTFOLIO")
        print("="*80)

        open_positions = portfolio.get_options_dataframe(status='open')
        if not open_positions.empty:
            print(f"\nOpen Positions: {len(open_positions)}")
            for idx, pos in open_positions.iterrows():
                print(f"\n  {idx + 1}. {pos['ticker']} ${pos['strike']:.0f} {pos['option_type'].upper()}")
                print(f"     Expires: {pos['expiration']} | {pos['contracts']} contracts @ ${pos['premium']:.2f}")
                print(f"     Strategy: {pos['strategy'].replace('_', ' ').title()}")
    else:
        print("\nPosition not added.")

    # Ask if want to add another
    print("\n" + "="*80)
    another = input("Add another position? (y/n): ").lower().strip()
    if another == 'y':
        add_position_interactive()


def quick_add_examples():
    """Quick examples for common positions"""
    portfolio = PortfolioManager()

    print("\n" + "="*80)
    print("QUICK ADD - EXAMPLE POSITIONS")
    print("="*80)

    examples = {
        '1': {
            'name': 'AAPL Cash Secured Put',
            'data': {
                'ticker': 'AAPL',
                'option_type': 'put',
                'strike': 165.0,
                'expiration': '2025-01-17',
                'contracts': 1,
                'premium': 2.50,
                'open_date': '2024-12-10',
                'strategy': 'cash_secured_put',
                'notes': 'Monthly income - 30 DTE'
            }
        },
        '2': {
            'name': 'TSLA Cash Secured Put',
            'data': {
                'ticker': 'TSLA',
                'option_type': 'put',
                'strike': 200.0,
                'expiration': '2025-01-17',
                'contracts': 1,
                'premium': 3.50,
                'open_date': '2024-12-10',
                'strategy': 'cash_secured_put',
                'notes': 'High IV opportunity'
            }
        },
        '3': {
            'name': 'INTC Cash Secured Put (Low Capital)',
            'data': {
                'ticker': 'INTC',
                'option_type': 'put',
                'strike': 25.0,
                'expiration': '2025-01-17',
                'contracts': 2,
                'premium': 0.75,
                'open_date': '2024-12-10',
                'strategy': 'cash_secured_put',
                'notes': 'Low capital requirement - multiple contracts'
            }
        }
    }

    print("\nExample positions you can add:")
    for key, example in examples.items():
        data = example['data']
        capital = data['strike'] * 100 * data['contracts']
        print(f"\n  {key}. {example['name']}")
        print(f"     ${data['strike']:.0f} {data['option_type'].upper()} | ${data['premium']:.2f} premium | {data['contracts']} contracts")
        print(f"     Capital: ${capital:,.0f} | Expires: {data['expiration']}")

    print("\n  4. Add custom position (interactive)")
    print("  0. Exit")

    choice = input("\nSelect option (0-4): ").strip()

    if choice == '0':
        return
    elif choice == '4':
        add_position_interactive()
    elif choice in examples:
        example = examples[choice]
        print(f"\nAdding: {example['name']}")
        portfolio.add_option_position(**example['data'])
        print("✓ Position added!")

        # Show portfolio
        open_positions = portfolio.get_options_dataframe(status='open')
        print(f"\nTotal open positions: {len(open_positions)}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("PORTFOLIO POSITION MANAGER")
    print("="*80)
    print("\nChoose an option:")
    print("  1. Add position interactively (step-by-step)")
    print("  2. Quick add example positions")
    print("  3. View current portfolio")

    choice = input("\nYour choice (1-3): ").strip()

    if choice == '1':
        add_position_interactive()
    elif choice == '2':
        quick_add_examples()
    elif choice == '3':
        portfolio = PortfolioManager()
        open_positions = portfolio.get_options_dataframe(status='open')

        print("\n" + "="*80)
        print("CURRENT PORTFOLIO")
        print("="*80)

        if open_positions.empty:
            print("\nNo open positions.")
            print("\nTo add positions, run: python add_position.py")
        else:
            print(f"\nOpen Positions: {len(open_positions)}")
            for idx, pos in open_positions.iterrows():
                capital = pos['strike'] * 100 * pos['contracts'] if pos['strategy'] == 'cash_secured_put' else 0
                print(f"\n  {idx + 1}. {pos['ticker']} ${pos['strike']:.0f} {pos['option_type'].upper()}")
                print(f"     Expires: {pos['expiration']}")
                print(f"     Contracts: {pos['contracts']} @ ${pos['premium']:.2f} premium")
                print(f"     Strategy: {pos['strategy'].replace('_', ' ').title()}")
                if capital > 0:
                    print(f"     Capital: ${capital:,.0f}")

    print("\n" + "="*80)
    print("\nTo analyze positions, run: python run_position_analysis.py")
    print("="*80 + "\n")
