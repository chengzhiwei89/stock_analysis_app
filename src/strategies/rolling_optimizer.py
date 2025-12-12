"""
Rolling Optimizer
Find and evaluate opportunities to roll option positions
"""
import sys
import os
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.data.option_extractor import OptionDataExtractor
from src.data.greeks_calculator import GreeksCalculator


class RollingOpportunityFinder:
    """Find and evaluate rolling opportunities for existing positions"""

    def __init__(self):
        """Initialize rolling optimizer"""
        self.option_extractor = OptionDataExtractor()
        self.greeks_calc = GreeksCalculator()

        # Load rolling criteria from config
        if hasattr(config, 'POSITION_ANALYSIS_SETTINGS'):
            self.roll_criteria = config.POSITION_ANALYSIS_SETTINGS.get('roll_criteria', {})
        else:
            # Fallback defaults
            self.roll_criteria = {
                'min_net_credit': 0.25,
                'min_annual_return_improvement': 5.0,
                'prefer_similar_dte': True,
                'max_roll_cost': 1.00,
            }

    def find_roll_opportunities(
        self,
        position: Dict,
        min_credit: Optional[float] = None,
        max_candidates: int = 5
    ) -> List[Dict]:
        """
        Find rolling opportunities for a position

        Args:
            position: Current position dict with ticker, strike, expiration, etc.
            min_credit: Minimum net credit required (overrides config)
            max_candidates: Maximum number of candidates to return

        Returns:
            List of rolling opportunity dictionaries, sorted by improvement_score
        """
        ticker = position['ticker']
        current_strike = position['strike']
        current_expiration = position['expiration']
        option_type = position['option_type']
        contracts = position['contracts']
        current_premium = position['premium']

        min_credit = min_credit or self.roll_criteria['min_net_credit']

        # Fetch current stock price
        current_price = self.option_extractor.get_current_price(ticker)
        if not current_price:
            return []

        # Calculate close cost for current position
        # Estimate current option value (would fetch from chain in production)
        close_cost = self._estimate_close_cost(
            position, current_price
        )

        # Fetch available expirations
        try:
            expirations = self.option_extractor.get_available_expirations(ticker)
            if not expirations:
                return []
        except:
            return []

        # Filter for later expirations only
        try:
            current_exp_date = datetime.strptime(current_expiration, '%Y-%m-%d')
            future_expirations = [
                exp for exp in expirations
                if datetime.strptime(exp, '%Y-%m-%d') > current_exp_date
            ]
        except:
            future_expirations = expirations

        if not future_expirations:
            return []

        # Evaluate roll candidates
        candidates = []

        for new_expiration in future_expirations[:6]:  # Limit to 6 expirations
            # Fetch option chain for this expiration
            try:
                chain = self.option_extractor.get_option_chain(ticker, new_expiration)
                if chain.empty:
                    continue

                # Filter for correct option type
                chain = chain[chain['option_type'] == option_type]
                if chain.empty:
                    continue

                # Enrich with Greeks
                chain = self.greeks_calc.enrich_option_data(chain)

                # Evaluate strikes around current strike
                for _, option in chain.iterrows():
                    new_strike = option['strike']

                    # For puts: Can roll same, down, or slightly up
                    # For calls: Can roll same, up, or slightly down
                    if option_type == 'put':
                        if new_strike > current_strike * 1.05:  # Don't roll too far up
                            continue
                    else:  # call
                        if new_strike < current_strike * 0.95:  # Don't roll too far down
                            continue

                    # Calculate roll economics
                    new_premium = option.get('bid', 0)
                    if new_premium <= 0:
                        new_premium = option.get('lastPrice', 0)

                    if new_premium <= 0:
                        continue

                    net_credit = new_premium - close_cost

                    # Only consider rolls that meet minimum credit
                    if net_credit < min_credit:
                        continue

                    # Calculate roll metrics
                    roll_type = self._classify_roll_type(
                        current_strike, new_strike,
                        current_expiration, new_expiration,
                        option_type
                    )

                    new_days_to_exp = option.get('days_to_expiration', 0)

                    # Calculate annual return for new position
                    if new_strike > 0 and new_days_to_exp > 0:
                        capital_required = new_strike * 100  # For CSP
                        new_annual_return = (new_premium / new_strike) * (365 / new_days_to_exp) * 100
                    else:
                        new_annual_return = 0

                    # Get probability OTM
                    new_prob_otm = option.get('prob_otm', 0)

                    # Calculate improvement score
                    improvement_score = self._calculate_improvement_score(
                        net_credit, new_annual_return, new_prob_otm,
                        new_days_to_exp, roll_type
                    )

                    # Create candidate
                    candidate = {
                        'current_strike': current_strike,
                        'current_expiration': current_expiration,
                        'close_cost': close_cost,
                        'new_strike': new_strike,
                        'new_expiration': new_expiration,
                        'new_premium': new_premium,
                        'new_days_to_expiration': new_days_to_exp,
                        'net_credit': net_credit,
                        'roll_type': roll_type,
                        'new_annual_return': new_annual_return,
                        'new_prob_otm': new_prob_otm,
                        'improvement_score': improvement_score,
                        'reasoning': self._generate_roll_reasoning(
                            net_credit, new_annual_return, new_prob_otm,
                            roll_type, new_days_to_exp
                        )
                    }

                    candidates.append(candidate)

            except Exception as e:
                continue

        # Sort by improvement score (descending)
        candidates.sort(key=lambda x: x['improvement_score'], reverse=True)

        return candidates[:max_candidates]

    def _estimate_close_cost(
        self,
        position: Dict,
        current_price: float
    ) -> float:
        """
        Estimate cost to close current position
        In production, would fetch actual bid/ask from option chain
        """
        entry_premium = position['premium']

        try:
            exp_date = datetime.strptime(position['expiration'], '%Y-%m-%d')
            days_remaining = (exp_date - datetime.now()).days
        except:
            days_remaining = 0

        if days_remaining <= 0:
            # Check intrinsic value
            strike = position['strike']
            if position['option_type'] == 'put':
                intrinsic = max(0, strike - current_price)
            else:
                intrinsic = max(0, current_price - strike)
            return intrinsic

        # Estimate with simple decay model
        # Assume 50-70% decay depending on moneyness
        strike = position['strike']
        if position['option_type'] == 'put':
            moneyness = current_price / strike
        else:
            moneyness = strike / current_price

        # Closer to ITM = less decay
        if moneyness < 0.95:  # Well OTM
            decay_factor = 0.3  # 70% decay
        elif moneyness < 1.0:  # Slightly OTM
            decay_factor = 0.5  # 50% decay
        else:  # ITM
            decay_factor = 0.7  # 30% decay

        estimated_close_cost = entry_premium * decay_factor
        return max(0, estimated_close_cost)

    def _classify_roll_type(
        self,
        current_strike: float,
        new_strike: float,
        current_exp: str,
        new_exp: str,
        option_type: str
    ) -> str:
        """Classify the type of roll"""
        try:
            current_exp_date = datetime.strptime(current_exp, '%Y-%m-%d')
            new_exp_date = datetime.strptime(new_exp, '%Y-%m-%d')
            time_extended = (new_exp_date - current_exp_date).days > 7
        except:
            time_extended = True

        strike_threshold = 0.02  # 2%

        strike_diff = (new_strike - current_strike) / current_strike

        if abs(strike_diff) < strike_threshold:
            # Same strike
            return "roll_out" if time_extended else "roll_same"
        elif option_type == 'put':
            if new_strike < current_strike:
                # Rolling down (safer for puts)
                return "roll_out_and_down" if time_extended else "roll_down"
            else:
                # Rolling up (less safe for puts)
                return "roll_out_and_up" if time_extended else "roll_up"
        else:  # call
            if new_strike > current_strike:
                # Rolling up (more upside for calls)
                return "roll_out_and_up" if time_extended else "roll_up"
            else:
                # Rolling down (less upside for calls)
                return "roll_out_and_down" if time_extended else "roll_down"

    def _calculate_improvement_score(
        self,
        net_credit: float,
        new_annual_return: float,
        new_prob_otm: float,
        new_days: int,
        roll_type: str
    ) -> float:
        """
        Calculate improvement score for a roll (0-100)

        Factors:
        - Net credit amount (40%)
        - Annual return (30%)
        - Probability OTM (20%)
        - Roll type preference (10%)
        """
        score = 0.0

        # 1. Net credit (0-40 points)
        # $0.25 = 10 points, $0.50 = 20, $1.00 = 30, $1.50+ = 40
        credit_score = min(40, (net_credit / 1.5) * 40)
        score += credit_score

        # 2. Annual return (0-30 points)
        # 20% = 15 points, 30% = 20, 40%+ = 30
        if new_annual_return >= 40:
            score += 30
        elif new_annual_return >= 30:
            score += 25
        elif new_annual_return >= 20:
            score += 20
        else:
            score += (new_annual_return / 20) * 20

        # 3. Probability OTM (0-20 points)
        # Linear: 50% = 10 points, 70% = 14, 80%+ = 20
        prob_score = (new_prob_otm / 100) * 20
        score += prob_score

        # 4. Roll type preference (0-10 points)
        roll_type_scores = {
            'roll_out_and_down': 10,  # Best for puts (safer + time)
            'roll_out': 9,            # Good (more time)
            'roll_down': 8,           # Decent (safer)
            'roll_out_and_up': 7,     # Neutral
            'roll_up': 5,             # Less ideal
            'roll_same': 6            # Neutral
        }
        score += roll_type_scores.get(roll_type, 5)

        return min(100, score)

    def _generate_roll_reasoning(
        self,
        net_credit: float,
        new_annual_return: float,
        new_prob_otm: float,
        roll_type: str,
        new_days: int
    ) -> str:
        """Generate human-readable reasoning for roll"""
        reasons = []

        reasons.append(f"Collect ${net_credit:.2f} net credit")
        reasons.append(f"New annual return: {new_annual_return:.1f}%")
        reasons.append(f"Probability OTM: {new_prob_otm:.0f}%")
        reasons.append(f"Extends {new_days} days")

        roll_type_descriptions = {
            'roll_out_and_down': "Safer strike with more time",
            'roll_out': "More time for premium decay",
            'roll_down': "Safer strike",
            'roll_out_and_up': "Higher strike with more time",
            'roll_up': "Higher strike",
            'roll_same': "Same strike"
        }

        if roll_type in roll_type_descriptions:
            reasons.append(roll_type_descriptions[roll_type])

        return " | ".join(reasons)

    def compare_roll_vs_close(
        self,
        position: Dict,
        roll_opportunity: Dict,
        current_pnl: float
    ) -> Dict:
        """
        Compare rolling vs. closing position

        Returns:
            Dictionary with recommendation and analysis
        """
        close_benefit = current_pnl  # Realize current P&L
        roll_benefit = roll_opportunity['net_credit'] * 100 * position['contracts']

        # Calculate total outcomes
        # If close: Get current P&L now
        # If roll: Get current P&L (by closing) + new premium - close cost
        # Simplified: Just compare net credits

        analysis = {
            'recommendation': '',
            'close_benefit': close_benefit,
            'roll_benefit': roll_benefit,
            'net_advantage': roll_benefit - close_benefit,
            'reasoning': []
        }

        if roll_opportunity['improvement_score'] >= 70:
            analysis['recommendation'] = 'ROLL'
            analysis['reasoning'].append(f"Excellent roll opportunity (score: {roll_opportunity['improvement_score']:.0f}/100)")
            analysis['reasoning'].append(f"Additional ${roll_benefit:.0f} premium potential")
        elif roll_opportunity['improvement_score'] >= 50:
            analysis['recommendation'] = 'ROLL'
            analysis['reasoning'].append(f"Good roll opportunity (score: {roll_opportunity['improvement_score']:.0f}/100)")
        else:
            analysis['recommendation'] = 'CLOSE'
            analysis['reasoning'].append("Roll opportunity marginal - consider closing")
            analysis['reasoning'].append(f"Current profit: ${close_benefit:.2f}")

        return analysis


if __name__ == '__main__':
    # Quick test
    print("Testing Rolling Optimizer...\n")

    # Create sample position
    sample_position = {
        'ticker': 'AAPL',
        'strike': 170.0,
        'expiration': '2025-12-20',
        'option_type': 'put',
        'premium': 2.50,
        'contracts': 1,
        'strategy': 'cash_secured_put',
        'open_date': '2024-11-20'
    }

    finder = RollingOpportunityFinder()

    print(f"Finding roll opportunities for {sample_position['ticker']} ${sample_position['strike']} {sample_position['option_type']}...")
    print(f"Current expiration: {sample_position['expiration']}\n")

    opportunities = finder.find_roll_opportunities(sample_position, max_candidates=3)

    if opportunities:
        print(f"Found {len(opportunities)} roll opportunities:\n")
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. Roll to ${opp['new_strike']} (exp {opp['new_expiration']})")
            print(f"   Net Credit: ${opp['net_credit']:.2f}")
            print(f"   Roll Type: {opp['roll_type']}")
            print(f"   Annual Return: {opp['new_annual_return']:.1f}%")
            print(f"   Prob OTM: {opp['new_prob_otm']:.0f}%")
            print(f"   Score: {opp['improvement_score']:.0f}/100")
            print(f"   {opp['reasoning']}")
            print()
    else:
        print("No roll opportunities found.")
        print("(May need live market data or different expiration)")
