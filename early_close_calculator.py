"""
Early Close Calculator
Calculate profit targets and track positions for early close strategy
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import os


class EarlyCloseCalculator:
    """Calculate profit targets for early close strategy"""

    def __init__(self):
        self.positions_file = "data/portfolio/early_close_positions.csv"
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create positions tracking file if it doesn't exist"""
        os.makedirs("data/portfolio", exist_ok=True)
        if not os.path.exists(self.positions_file):
            df = pd.DataFrame(columns=[
                'ticker', 'strike', 'expiration', 'opened_date', 'dte_opened',
                'premium_received', 'contracts', 'target_50', 'target_75',
                'close_date', 'close_price', 'profit', 'days_held', 'profit_pct', 'status'
            ])
            df.to_csv(self.positions_file, index=False)

    def calculate_targets(self, premium: float) -> dict:
        """
        Calculate profit targets for an option position

        Args:
            premium: Premium received per share (e.g., 6.00)

        Returns:
            Dictionary with target prices and profit amounts
        """
        return {
            'premium_received': premium,
            'target_50_price': premium * 0.50,  # Close when option = 50% of original
            'target_75_price': premium * 0.25,  # Close when option = 25% of original
            'profit_50_amount': premium * 0.50,  # Profit at 50%
            'profit_75_amount': premium * 0.75,  # Profit at 75%
            'profit_50_total': premium * 0.50 * 100,  # Per contract
            'profit_75_total': premium * 0.75 * 100,  # Per contract
        }

    def add_position(self, ticker: str, strike: float, expiration: str,
                     premium: float, contracts: int = 1, dte: int = None) -> pd.DataFrame:
        """
        Add a new position to track

        Args:
            ticker: Stock ticker
            strike: Strike price
            expiration: Expiration date (YYYY-MM-DD)
            premium: Premium received per share
            contracts: Number of contracts sold
            dte: Days to expiration when opened

        Returns:
            DataFrame with updated positions
        """
        targets = self.calculate_targets(premium)

        new_position = {
            'ticker': ticker,
            'strike': strike,
            'expiration': expiration,
            'opened_date': datetime.now().strftime('%Y-%m-%d'),
            'dte_opened': dte,
            'premium_received': premium,
            'contracts': contracts,
            'target_50': targets['target_50_price'],
            'target_75': targets['target_75_price'],
            'close_date': None,
            'close_price': None,
            'profit': None,
            'days_held': None,
            'profit_pct': None,
            'status': 'OPEN'
        }

        df = pd.read_csv(self.positions_file)
        df = pd.concat([df, pd.DataFrame([new_position])], ignore_index=True)
        df.to_csv(self.positions_file, index=False)

        print(f"\n✓ Position added: {ticker} ${strike} PUT")
        print(f"  Premium: ${premium:.2f} × {contracts} = ${premium * contracts * 100:.0f}")
        print(f"  50% target: Close at ${targets['target_50_price']:.2f} for ${targets['profit_50_total'] * contracts:.0f} profit")
        print(f"  75% target: Close at ${targets['target_75_price']:.2f} for ${targets['profit_75_total'] * contracts:.0f} profit")

        return df

    def close_position(self, ticker: str, strike: float, close_price: float) -> pd.DataFrame:
        """
        Close a position and calculate results

        Args:
            ticker: Stock ticker
            strike: Strike price
            close_price: Price paid to close (per share)

        Returns:
            DataFrame with updated positions
        """
        df = pd.read_csv(self.positions_file)

        # Find the open position
        mask = (df['ticker'] == ticker) & (df['strike'] == strike) & (df['status'] == 'OPEN')

        if not mask.any():
            print(f"❌ No open position found for {ticker} ${strike}")
            return df

        idx = df[mask].index[0]

        # Calculate results
        opened_date = datetime.strptime(df.loc[idx, 'opened_date'], '%Y-%m-%d')
        close_date = datetime.now()
        days_held = (close_date - opened_date).days

        premium = df.loc[idx, 'premium_received']
        contracts = df.loc[idx, 'contracts']
        profit_per_share = premium - close_price
        profit_pct = (profit_per_share / premium) * 100
        profit_total = profit_per_share * contracts * 100

        # Update position
        df.loc[idx, 'close_date'] = close_date.strftime('%Y-%m-%d')
        df.loc[idx, 'close_price'] = close_price
        df.loc[idx, 'profit'] = profit_total
        df.loc[idx, 'days_held'] = days_held
        df.loc[idx, 'profit_pct'] = profit_pct
        df.loc[idx, 'status'] = 'CLOSED'

        df.to_csv(self.positions_file, index=False)

        # Print results
        print(f"\n✓ Position closed: {ticker} ${strike} PUT")
        print(f"  Opened: ${premium:.2f} × {contracts}")
        print(f"  Closed: ${close_price:.2f} × {contracts}")
        print(f"  Profit: ${profit_total:.2f} ({profit_pct:.1f}%)")
        print(f"  Days held: {days_held}")
        print(f"  Annualized return: {(profit_pct / days_held * 365):.1f}%")

        if profit_pct >= 75:
            print(f"  🎯 EXCELLENT! Hit 75% target!")
        elif profit_pct >= 50:
            print(f"  ✓ GOOD! Hit 50% target!")
        elif profit_pct >= 25:
            print(f"  ⚠️ OK. Below target but still profitable")
        else:
            print(f"  ⚠️ Low profit. Consider waiting longer next time.")

        return df

    def get_open_positions(self) -> pd.DataFrame:
        """Get all open positions"""
        df = pd.read_csv(self.positions_file)
        open_positions = df[df['status'] == 'OPEN'].copy()

        if open_positions.empty:
            return open_positions

        # Calculate days held
        today = datetime.now()
        open_positions['days_held'] = open_positions['opened_date'].apply(
            lambda x: (today - datetime.strptime(x, '%Y-%m-%d')).days
        )

        # Calculate days to 21 DTE close
        open_positions['days_to_force_close'] = open_positions.apply(
            lambda row: row['dte_opened'] - 21 - row['days_held'] if pd.notna(row['dte_opened']) else None,
            axis=1
        )

        return open_positions

    def get_closed_positions(self) -> pd.DataFrame:
        """Get all closed positions with statistics"""
        df = pd.read_csv(self.positions_file)
        closed = df[df['status'] == 'CLOSED'].copy()

        if closed.empty:
            return closed

        # Add annualized return
        closed['annualized_return'] = closed.apply(
            lambda row: (row['profit_pct'] / row['days_held'] * 365) if row['days_held'] > 0 else 0,
            axis=1
        )

        return closed

    def print_summary(self):
        """Print summary of all positions"""
        open_pos = self.get_open_positions()
        closed_pos = self.get_closed_positions()

        print("\n" + "="*80)
        print("EARLY CLOSE STRATEGY - POSITION SUMMARY")
        print("="*80)

        # Open positions
        if not open_pos.empty:
            print(f"\n📊 OPEN POSITIONS ({len(open_pos)}):")
            print("-" * 80)
            for _, pos in open_pos.iterrows():
                print(f"\n{pos['ticker']} ${pos['strike']} PUT - Exp: {pos['expiration']}")
                print(f"  Opened: {pos['opened_date']} ({pos['days_held']} days ago)")
                print(f"  Premium: ${pos['premium_received']:.2f} × {pos['contracts']} = ${pos['premium_received'] * pos['contracts'] * 100:.0f}")
                print(f"  Targets: 50% @ ${pos['target_50']:.2f} | 75% @ ${pos['target_75']:.2f}")

                if pd.notna(pos['days_to_force_close']) and pos['days_to_force_close'] <= 7:
                    print(f"  ⚠️ ALERT: Force close in {int(pos['days_to_force_close'])} days (21 DTE rule)")
                elif pd.notna(pos['days_to_force_close']):
                    print(f"  Force close in: {int(pos['days_to_force_close'])} days")
        else:
            print("\n📊 OPEN POSITIONS: None")

        # Closed positions summary
        if not closed_pos.empty:
            print(f"\n\n📈 CLOSED POSITIONS ({len(closed_pos)}):")
            print("-" * 80)

            total_profit = closed_pos['profit'].sum()
            avg_profit_pct = closed_pos['profit_pct'].mean()
            avg_days = closed_pos['days_held'].mean()
            avg_annual = closed_pos['annualized_return'].mean()
            win_rate = (closed_pos['profit'] > 0).sum() / len(closed_pos) * 100

            print(f"\nSTATISTICS:")
            print(f"  Total Profit: ${total_profit:.2f}")
            print(f"  Average Profit %: {avg_profit_pct:.1f}%")
            print(f"  Average Days Held: {avg_days:.1f}")
            print(f"  Average Annualized Return: {avg_annual:.1f}%")
            print(f"  Win Rate: {win_rate:.1f}%")

            # Hit rate for targets
            hit_75 = (closed_pos['profit_pct'] >= 75).sum()
            hit_50 = (closed_pos['profit_pct'] >= 50).sum()
            print(f"\nTARGET HIT RATE:")
            print(f"  75% Target: {hit_75}/{len(closed_pos)} ({hit_75/len(closed_pos)*100:.1f}%)")
            print(f"  50% Target: {hit_50}/{len(closed_pos)} ({hit_50/len(closed_pos)*100:.1f}%)")

            # Recent trades
            print(f"\nRECENT CLOSED POSITIONS:")
            recent = closed_pos.tail(5)[['ticker', 'strike', 'close_date', 'profit', 'profit_pct', 'days_held', 'annualized_return']]
            for _, pos in recent.iterrows():
                print(f"  {pos['ticker']} ${pos['strike']}: ${pos['profit']:.0f} ({pos['profit_pct']:.1f}%) in {pos['days_held']} days | {pos['annualized_return']:.0f}% annual")
        else:
            print("\n\n📈 CLOSED POSITIONS: None yet")

        print("\n" + "="*80 + "\n")

    def print_alerts(self):
        """Print current positions with alert levels for broker"""
        open_pos = self.get_open_positions()

        if open_pos.empty:
            print("\nNo open positions to set alerts for.")
            return

        print("\n" + "="*80)
        print("SET THESE ALERTS IN YOUR BROKER")
        print("="*80)

        for _, pos in open_pos.iterrows():
            print(f"\n{pos['ticker']} ${pos['strike']} PUT (Exp: {pos['expiration']})")
            print(f"  Alert 1: Price = ${pos['target_50']:.2f} → Close for 50% profit")
            print(f"  Alert 2: Price = ${pos['target_75']:.2f} → Close for 75% profit")

            profit_50 = pos['premium_received'] * 0.50 * pos['contracts'] * 100
            profit_75 = pos['premium_received'] * 0.75 * pos['contracts'] * 100
            print(f"  Expected profit: ${profit_50:.0f} (50%) or ${profit_75:.0f} (75%)")

        print("\n" + "="*80 + "\n")


def main():
    """Interactive CLI for managing early close positions"""
    calc = EarlyCloseCalculator()

    while True:
        print("\n" + "="*80)
        print("EARLY CLOSE POSITION MANAGER")
        print("="*80)
        print("\n1. Add new position")
        print("2. Close position")
        print("3. View open positions")
        print("4. View closed positions")
        print("5. Print summary")
        print("6. Print broker alerts")
        print("7. Quick calculator")
        print("8. Exit")

        choice = input("\nSelect option (1-8): ").strip()

        if choice == '1':
            print("\n--- ADD NEW POSITION ---")
            ticker = input("Ticker: ").upper()
            strike = float(input("Strike price: "))
            expiration = input("Expiration (YYYY-MM-DD): ")
            premium = float(input("Premium received per share: "))
            contracts = int(input("Number of contracts (default 1): ") or "1")
            dte = int(input("Days to expiration when opened: ") or "0")

            calc.add_position(ticker, strike, expiration, premium, contracts, dte)

        elif choice == '2':
            print("\n--- CLOSE POSITION ---")
            open_pos = calc.get_open_positions()
            if open_pos.empty:
                print("No open positions to close.")
                continue

            print("\nOpen positions:")
            for i, (_, pos) in enumerate(open_pos.iterrows(), 1):
                print(f"{i}. {pos['ticker']} ${pos['strike']} PUT")

            pos_num = int(input("\nSelect position to close (number): ")) - 1
            if 0 <= pos_num < len(open_pos):
                pos = open_pos.iloc[pos_num]
                close_price = float(input(f"Close price per share for {pos['ticker']} ${pos['strike']}: "))
                calc.close_position(pos['ticker'], pos['strike'], close_price)
            else:
                print("Invalid selection.")

        elif choice == '3':
            open_pos = calc.get_open_positions()
            if open_pos.empty:
                print("\nNo open positions.")
            else:
                print("\n" + "="*80)
                print("OPEN POSITIONS")
                print("="*80)
                print(open_pos[['ticker', 'strike', 'expiration', 'premium_received',
                               'target_50', 'target_75', 'days_held']].to_string(index=False))

        elif choice == '4':
            closed_pos = calc.get_closed_positions()
            if closed_pos.empty:
                print("\nNo closed positions yet.")
            else:
                print("\n" + "="*80)
                print("CLOSED POSITIONS")
                print("="*80)
                print(closed_pos[['ticker', 'strike', 'close_date', 'profit',
                                 'profit_pct', 'days_held', 'annualized_return']].to_string(index=False))

        elif choice == '5':
            calc.print_summary()

        elif choice == '6':
            calc.print_alerts()

        elif choice == '7':
            print("\n--- QUICK CALCULATOR ---")
            premium = float(input("Premium received per share: "))
            contracts = int(input("Number of contracts (default 1): ") or "1")

            targets = calc.calculate_targets(premium)

            print(f"\nPREMIUM RECEIVED: ${premium:.2f} × {contracts} = ${premium * contracts * 100:.0f}")
            print(f"\n50% PROFIT TARGET:")
            print(f"  Close when option = ${targets['target_50_price']:.2f}")
            print(f"  Profit = ${targets['profit_50_total'] * contracts:.0f}")
            print(f"\n75% PROFIT TARGET:")
            print(f"  Close when option = ${targets['target_75_price']:.2f}")
            print(f"  Profit = ${targets['profit_75_total'] * contracts:.0f}")

        elif choice == '8':
            print("\nGoodbye!")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
