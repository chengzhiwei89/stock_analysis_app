"""
Portfolio Management Script
Close option positions and remove stock positions interactively
"""
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.portfolio.portfolio_manager import PortfolioManager
from tabulate import tabulate


def view_portfolio_summary():
    """Display portfolio summary"""
    portfolio = PortfolioManager()

    print("\n" + "="*80)
    print("CURRENT PORTFOLIO")
    print("="*80)

    # Show stocks
    stocks = portfolio.get_stocks_dataframe()
    if not stocks.empty:
        print(f"\n📊 STOCK POSITIONS ({len(stocks)}):")
        print("-"*80)

        table_data = []
        for idx, stock in stocks.iterrows():
            total_value = stock['shares'] * stock['cost_basis']
            contracts = stock['shares'] // 100
            table_data.append([
                idx,
                stock['ticker'],
                stock['shares'],
                f"${stock['cost_basis']:.2f}",
                f"${total_value:,.2f}",
                stock['purchase_date'],
                f"{contracts} contracts" if contracts > 0 else "N/A"
            ])

        print(tabulate(table_data,
                      headers=['Index', 'Ticker', 'Shares', 'Cost Basis', 'Total Value', 'Purchase Date', 'CC Available'],
                      tablefmt='grid'))
    else:
        print("\n📊 STOCK POSITIONS: None")

    # Show options
    open_options = portfolio.get_options_dataframe(status='open')
    if not open_options.empty:
        print(f"\n\n📈 OPEN OPTION POSITIONS ({len(open_options)}):")
        print("-"*80)

        table_data = []
        for idx, pos in open_options.iterrows():
            capital = pos['strike'] * 100 * pos['contracts'] if pos['strategy'] == 'cash_secured_put' else 0
            table_data.append([
                idx,
                pos['ticker'],
                f"${pos['strike']:.0f}",
                pos['option_type'].upper(),
                pos['expiration'],
                pos['contracts'],
                f"${pos['premium']:.2f}",
                pos['strategy'].replace('_', ' ').title(),
                f"${capital:,.0f}" if capital > 0 else "N/A"
            ])

        print(tabulate(table_data,
                      headers=['Index', 'Ticker', 'Strike', 'Type', 'Expiration', 'Contracts', 'Premium', 'Strategy', 'Capital'],
                      tablefmt='grid'))
    else:
        print(f"\n\n📈 OPEN OPTION POSITIONS: None")

    # Show closed options
    closed_options = portfolio.get_options_dataframe(status='closed')
    if not closed_options.empty:
        print(f"\n\n📝 CLOSED OPTION POSITIONS ({len(closed_options)}):")
        print("-"*80)

        table_data = []
        for idx, pos in closed_options.iterrows():
            realized_pnl = (pos['premium'] - pos.get('close_premium', 0)) * 100 * pos['contracts']
            table_data.append([
                idx,
                pos['ticker'],
                f"${pos['strike']:.0f}",
                pos['option_type'].upper(),
                pos.get('close_date', 'N/A'),
                pos.get('outcome', 'N/A'),
                f"${realized_pnl:.2f}"
            ])

        print(tabulate(table_data,
                      headers=['Index', 'Ticker', 'Strike', 'Type', 'Close Date', 'Outcome', 'Realized P&L'],
                      tablefmt='grid'))


def close_option_position():
    """Interactively close an option position"""
    portfolio = PortfolioManager()

    print("\n" + "="*80)
    print("CLOSE OPTION POSITION")
    print("="*80)

    # Show open positions
    open_options = portfolio.get_options_dataframe(status='open')

    if open_options.empty:
        print("\nNo open option positions to close.")
        return

    print("\nOpen option positions:")
    for idx, pos in open_options.iterrows():
        print(f"\n  [{idx}] {pos['ticker']} ${pos['strike']:.0f} {pos['option_type'].upper()}")
        print(f"      Expires: {pos['expiration']} | {pos['contracts']} contracts @ ${pos['premium']:.2f}")
        print(f"      Strategy: {pos['strategy'].replace('_', ' ').title()}")
        print(f"      Opened: {pos['open_date']}")

    # Get position to close
    print("\n" + "-"*80)
    index_input = input("Enter the index of the position to close (or 'c' to cancel): ").strip()

    if index_input.lower() == 'c':
        print("Cancelled.")
        return

    try:
        index = int(index_input)
        if index not in open_options.index:
            print(f"Invalid index: {index}")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    position = open_options.loc[index]

    # Get close details
    print("\n" + "-"*80)
    print("Enter closing details:")

    close_date = input("  Close Date (YYYY-MM-DD, or press Enter for today): ").strip()
    if not close_date:
        close_date = datetime.now().strftime('%Y-%m-%d')

    print("\n  Outcome:")
    print("    1. Expired worthless (kept full premium)")
    print("    2. Bought back (closed early)")
    print("    3. Assigned (stock assigned/delivered)")
    outcome_choice = input("  Choice (1-3): ").strip()

    if outcome_choice == '1':
        outcome = 'expired'
        close_premium = 0.0
        print("  → Position expired worthless (full premium kept)")
    elif outcome_choice == '2':
        outcome = 'bought_back'
        close_premium = float(input("  Premium paid to buy back ($ per share): $").strip())
    elif outcome_choice == '3':
        outcome = 'assigned'
        close_premium = 0.0
        print("  → Position was assigned")
    else:
        print("Invalid choice. Using 'expired' as default.")
        outcome = 'expired'
        close_premium = 0.0

    # Calculate P&L
    open_premium = position['premium'] * 100 * position['contracts']
    close_cost = close_premium * 100 * position['contracts']
    realized_pnl = open_premium - close_cost

    # Confirm
    print("\n" + "-"*80)
    print("CLOSE POSITION SUMMARY:")
    print(f"  Position: {position['ticker']} ${position['strike']:.0f} {position['option_type'].upper()}")
    print(f"  Opened: {position['open_date']} @ ${position['premium']:.2f}")
    print(f"  Close Date: {close_date}")
    print(f"  Outcome: {outcome}")
    if close_premium > 0:
        print(f"  Close Premium: ${close_premium:.2f} per share")
    print(f"\n  Realized P&L: ${realized_pnl:.2f}")
    print("-"*80)

    confirm = input("\nClose this position? (y/n): ").lower().strip()

    if confirm == 'y':
        portfolio.close_option_position(index, close_date, close_premium, outcome)
        print("\n✓ Position closed successfully!")
        print(f"  Realized P&L: ${realized_pnl:.2f}")
    else:
        print("\nPosition not closed.")


def remove_stock_position():
    """Interactively remove a stock position"""
    portfolio = PortfolioManager()

    print("\n" + "="*80)
    print("REMOVE STOCK POSITION")
    print("="*80)

    # Show stock positions
    stocks = portfolio.get_stocks_dataframe()

    if stocks.empty:
        print("\nNo stock positions to remove.")
        return

    print("\nStock positions:")
    for idx, stock in stocks.iterrows():
        total_value = stock['shares'] * stock['cost_basis']
        contracts = stock['shares'] // 100
        print(f"\n  [{idx}] {stock['ticker']}")
        print(f"      Shares: {stock['shares']:,} | Cost: ${stock['cost_basis']:.2f}")
        print(f"      Total Value: ${total_value:,.2f}")
        print(f"      Purchase Date: {stock['purchase_date']}")
        if contracts > 0:
            print(f"      CC Contracts Available: {contracts}")
        if stock.get('notes'):
            print(f"      Notes: {stock['notes']}")

    # Get position to remove
    print("\n" + "-"*80)
    index_input = input("Enter the index of the position to remove (or 'c' to cancel): ").strip()

    if index_input.lower() == 'c':
        print("Cancelled.")
        return

    try:
        index = int(index_input)
        if index not in stocks.index:
            print(f"Invalid index: {index}")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    stock = stocks.loc[index]

    # Confirm
    print("\n" + "-"*80)
    print("⚠️  WARNING: This will permanently remove this stock position!")
    print(f"  {stock['ticker']}: {stock['shares']:,} shares @ ${stock['cost_basis']:.2f}")
    print("-"*80)

    confirm = input("\nAre you sure you want to remove this position? (y/n): ").lower().strip()

    if confirm == 'y':
        portfolio.remove_stock_position(index)
        print("\n✓ Stock position removed successfully!")
    else:
        print("\nPosition not removed.")


def main_menu():
    """Main menu"""
    while True:
        print("\n" + "="*80)
        print("PORTFOLIO MANAGEMENT")
        print("="*80)
        print("\nChoose an option:")
        print("  1. View portfolio summary")
        print("  2. Close option position")
        print("  3. Remove stock position")
        print("  4. Exit")

        choice = input("\nYour choice (1-4): ").strip()

        if choice == '1':
            view_portfolio_summary()
        elif choice == '2':
            close_option_position()
        elif choice == '3':
            remove_stock_position()
        elif choice == '4':
            print("\nExiting...")
            break
        else:
            print("\nInvalid choice. Please select 1-4.")

        if choice in ['1', '2', '3']:
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main_menu()
