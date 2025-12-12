"""
Position Analyzer
Analyzes existing option positions and generates management recommendations
"""
import sys
import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import config
from src.data.option_extractor import OptionDataExtractor
from src.analysis.enhanced_probability import EnhancedProbabilityAnalyzer


@dataclass
class RollingOpportunity:
    """Represents a rolling opportunity for a position"""
    # Current position
    current_strike: float
    current_expiration: str
    close_cost: float

    # Roll target
    new_strike: float
    new_expiration: str
    new_premium: float
    new_days_to_expiration: int

    # Economics
    net_credit: float
    roll_type: str  # 'roll_out', 'roll_up', 'roll_down', 'roll_out_and_up'

    # Analysis
    new_annual_return: float
    new_prob_otm: float
    improvement_score: float
    reasoning: str


@dataclass
class PositionRecommendation:
    """Complete analysis and recommendation for a position"""
    # Position identity and entry data
    position_index: int
    ticker: str
    option_type: str  # 'call' or 'put'
    strike: float
    expiration: str
    contracts: int
    strategy: str
    entry_date: str
    entry_premium: float
    days_held: int

    # Current market state
    current_price: float  # Stock price
    current_option_price: float  # Option mid/last price
    days_remaining: int

    # P&L metrics
    unrealized_pnl: float  # Current P&L (premium received - buyback cost)
    unrealized_pnl_pct: float  # % of max profit captured
    total_premium_dollars: float  # Total $ collected (contracts * 100 * premium)
    capital_deployed: float  # Capital tied up in position

    # Probability analysis (original vs current)
    entry_prob_otm: Optional[float] = None  # Probability at entry (if tracked)
    current_prob_otm: float = 0.0  # Current probability
    prob_change: float = 0.0  # Change in probability

    # Enhanced score comparison
    entry_technical_score: Optional[float] = None
    current_technical_score: float = 0.0
    technical_score_change: float = 0.0

    entry_composite_score: Optional[float] = None
    current_composite_score: float = 0.0
    composite_score_change: float = 0.0

    # Risk factors
    event_risk_score: float = 0.0  # Current event risk (earnings, etc.)
    days_to_next_earnings: Optional[int] = None
    implied_volatility: float = 0.0
    iv_change_pct: float = 0.0  # IV change since entry

    # Position health
    health_score: float = 0.0  # 0-100, higher is better
    health_status: str = "unknown"  # 'healthy', 'warning', 'critical'
    moneyness: str = "unknown"  # 'ITM', 'ATM', 'OTM'

    # Recommendation
    action: str = "HOLD"  # 'HOLD', 'CLOSE_EARLY', 'ROLL', 'ADJUST_TARGETS'
    urgency: int = 1  # 1-5 (5 = urgent, 1 = low priority)
    confidence: str = "medium"  # 'high', 'medium', 'low'

    # Reasoning
    primary_reason: str = ""
    supporting_reasons: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)

    # Action details
    suggested_close_price: Optional[float] = None
    profit_target_price: Optional[float] = None
    stop_loss_price: Optional[float] = None

    # Rolling details (if action = ROLL)
    roll_recommendation: Optional[RollingOpportunity] = None

    # Metadata
    analysis_timestamp: str = ""
    data_quality: str = "medium"  # 'high', 'medium', 'low'


class PositionAnalyzer:
    """Analyze option positions and generate management recommendations"""

    def __init__(self):
        """Initialize position analyzer with config settings"""
        self.option_extractor = OptionDataExtractor()
        self.prob_analyzer = EnhancedProbabilityAnalyzer()

        # Load settings from config
        if hasattr(config, 'POSITION_ANALYSIS_SETTINGS'):
            self.settings = config.POSITION_ANALYSIS_SETTINGS
        else:
            # Fallback defaults if config not yet updated
            self.settings = {
                'profit_taking_rules': {
                    'aggressive_target_pct': 75,
                    'standard_target_pct': 50,
                    'conservative_target_pct': 30,
                    'stop_loss_pct': -50,
                    'force_close_dte': 21,
                    'min_hold_days': 7,
                },
                'risk_thresholds': {
                    'min_prob_otm_warning': 45,
                    'max_iv_change_pct': 30,
                    'earnings_warning_days': 14,
                    'technical_score_drop': 15,
                }
            }

    def analyze_option_position(
        self,
        position: Dict,
        position_index: int = 0
    ) -> PositionRecommendation:
        """
        Analyze a single option position and generate recommendation

        Args:
            position: Dictionary or Series with position data
            position_index: Index of position in portfolio

        Returns:
            PositionRecommendation with complete analysis
        """
        # Convert Series to dict if needed
        if isinstance(position, pd.Series):
            position = position.to_dict()

        # Fetch current market data
        ticker = position['ticker']
        current_price = self.option_extractor.get_current_price(ticker)

        if current_price is None:
            current_price = 0.0

        # Calculate days remaining
        try:
            exp_date = datetime.strptime(position['expiration'], '%Y-%m-%d')
            days_remaining = (exp_date - datetime.now()).days
        except:
            days_remaining = 0

        # Calculate days held
        try:
            entry_date = datetime.strptime(position['open_date'], '%Y-%m-%d')
            days_held = (datetime.now() - entry_date).days
        except:
            days_held = 0

        # Fetch current option price (approximate)
        # For now, use simple estimate. In production, would fetch actual option chain
        current_option_price = self._estimate_current_option_price(
            position, current_price, days_remaining
        )

        # Calculate P&L metrics
        pnl_metrics = self._calculate_pnl_metrics(
            position, current_option_price
        )

        # Run enhanced probability analysis
        prob_analysis = self._calculate_probability_analysis(
            position, current_price
        )

        # Calculate health score
        health_score, health_status = self._calculate_health_score(
            position, pnl_metrics, prob_analysis, days_remaining
        )

        # Determine moneyness
        moneyness = self._determine_moneyness(
            position, current_price
        )

        # Assess risk factors
        risk_factors = self._assess_risk_factors(
            position, prob_analysis, days_remaining
        )

        # Determine recommended action
        action, urgency, primary_reason, supporting_reasons = self._determine_action(
            position, pnl_metrics, prob_analysis, risk_factors,
            health_score, moneyness, days_remaining, days_held
        )

        # Calculate optimal profit targets
        targets = self.calculate_optimal_profit_target(
            position, pnl_metrics, prob_analysis, days_remaining
        )

        # Get entry analysis if available
        entry_analysis = position.get('entry_analysis', {})

        # Create recommendation
        recommendation = PositionRecommendation(
            position_index=position_index,
            ticker=ticker,
            option_type=position['option_type'],
            strike=position['strike'],
            expiration=position['expiration'],
            contracts=position['contracts'],
            strategy=position['strategy'],
            entry_date=position['open_date'],
            entry_premium=position['premium'],
            days_held=days_held,
            current_price=current_price,
            current_option_price=current_option_price,
            days_remaining=days_remaining,
            unrealized_pnl=pnl_metrics['unrealized_pnl'],
            unrealized_pnl_pct=pnl_metrics['unrealized_pnl_pct'],
            total_premium_dollars=pnl_metrics['total_premium_dollars'],
            capital_deployed=pnl_metrics['capital_deployed'],
            entry_prob_otm=entry_analysis.get('prob_otm_at_entry'),
            current_prob_otm=prob_analysis.get('current_prob_otm', 0),
            prob_change=prob_analysis.get('prob_change', 0),
            entry_technical_score=entry_analysis.get('technical_score_at_entry'),
            current_technical_score=prob_analysis.get('technical_score', 0),
            technical_score_change=prob_analysis.get('technical_score_change', 0),
            entry_composite_score=entry_analysis.get('composite_score_at_entry'),
            current_composite_score=prob_analysis.get('composite_score', 0),
            composite_score_change=prob_analysis.get('composite_score_change', 0),
            event_risk_score=prob_analysis.get('event_risk_score', 0),
            days_to_next_earnings=prob_analysis.get('days_to_earnings'),
            implied_volatility=prob_analysis.get('implied_volatility', 0),
            iv_change_pct=0.0,  # Would need historical IV
            health_score=health_score,
            health_status=health_status,
            moneyness=moneyness,
            action=action,
            urgency=urgency,
            confidence="high" if health_score > 70 or health_score < 40 else "medium",
            primary_reason=primary_reason,
            supporting_reasons=supporting_reasons,
            risk_factors=risk_factors,
            suggested_close_price=targets.get('suggested_close_price'),
            profit_target_price=targets.get('profit_target_price'),
            stop_loss_price=targets.get('stop_loss_price'),
            analysis_timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            data_quality="high" if current_price > 0 else "low"
        )

        return recommendation

    def _estimate_current_option_price(
        self,
        position: Dict,
        current_price: float,
        days_remaining: int
    ) -> float:
        """
        Estimate current option price
        In production, would fetch from live option chain
        For now, use simplified decay model
        """
        entry_premium = position['premium']

        if days_remaining <= 0:
            # Expired, check if ITM
            strike = position['strike']
            if position['option_type'] == 'put':
                return max(0, strike - current_price)
            else:
                return max(0, current_price - strike)

        # Simple decay model: assume 50% decay at midpoint
        # This is a rough approximation
        # In reality, would fetch actual bid/ask from option chain
        try:
            entry_date = datetime.strptime(position['open_date'], '%Y-%m-%d')
            exp_date = datetime.strptime(position['expiration'], '%Y-%m-%d')
            total_days = (exp_date - entry_date).days
            days_elapsed = total_days - days_remaining

            if total_days > 0:
                time_decay_factor = days_remaining / total_days
                # Exponential decay (steeper near expiration)
                estimated_price = entry_premium * (time_decay_factor ** 0.5)
                return max(0, estimated_price)
        except:
            pass

        return entry_premium * 0.5  # Fallback: assume 50% decay

    def _calculate_pnl_metrics(
        self,
        position: Dict,
        current_option_price: float
    ) -> Dict:
        """Calculate P&L metrics for position"""
        entry_premium = position['premium']
        contracts = position['contracts']
        strike = position['strike']

        # For sold options (CSP, CC), we received premium
        # P&L = premium received - current buyback cost
        total_premium_dollars = entry_premium * 100 * contracts
        current_value = current_option_price * 100 * contracts

        unrealized_pnl = total_premium_dollars - current_value

        # % of max profit captured
        # Max profit = premium received (if expires worthless)
        if total_premium_dollars > 0:
            unrealized_pnl_pct = (unrealized_pnl / total_premium_dollars) * 100
        else:
            unrealized_pnl_pct = 0

        # Calculate capital deployed
        if position['strategy'] == 'cash_secured_put':
            capital_deployed = strike * 100 * contracts
        else:
            capital_deployed = 0  # For CC, stock already owned

        return {
            'unrealized_pnl': unrealized_pnl,
            'unrealized_pnl_pct': unrealized_pnl_pct,
            'total_premium_dollars': total_premium_dollars,
            'capital_deployed': capital_deployed,
            'current_value': current_value
        }

    def _calculate_probability_analysis(
        self,
        position: Dict,
        current_price: float
    ) -> Dict:
        """Calculate current probability metrics using enhanced analyzer"""
        result = {}

        try:
            # Create a minimal options dataframe row for analysis
            option_data = pd.Series({
                'ticker': position['ticker'],
                'strike': position['strike'],
                'option_type': position['option_type'],
                'expiration': position['expiration'],
                'current_stock_price': current_price
            })

            # Run enhanced probability analysis
            enhanced_analysis = self.prob_analyzer.calculate_enhanced_probability(
                option_data
            )

            result['current_prob_otm'] = enhanced_analysis.get('enhanced_prob_otm', 0)
            result['technical_score'] = enhanced_analysis.get('technical_score', 50)
            result['composite_score'] = enhanced_analysis.get('composite_score', 50)
            result['event_risk_score'] = enhanced_analysis.get('event_risk_score', 50)
            result['implied_volatility'] = enhanced_analysis.get('implied_volatility', 0)

            # Calculate changes if entry data available
            entry_analysis = position.get('entry_analysis', {})
            if entry_analysis:
                entry_prob = entry_analysis.get('prob_otm_at_entry', 0)
                if entry_prob:
                    result['prob_change'] = result['current_prob_otm'] - entry_prob

                entry_tech = entry_analysis.get('technical_score_at_entry', 0)
                if entry_tech:
                    result['technical_score_change'] = result['technical_score'] - entry_tech

        except Exception as e:
            # If analysis fails, use safe defaults
            result['current_prob_otm'] = 50
            result['technical_score'] = 50
            result['composite_score'] = 50

        return result

    def _calculate_health_score(
        self,
        position: Dict,
        pnl_metrics: Dict,
        prob_analysis: Dict,
        days_remaining: int
    ) -> Tuple[float, str]:
        """
        Calculate position health score (0-100)

        Factors:
        - Profit captured (30 points)
        - Time decay favorable (25 points)
        - Safety margin / moneyness (25 points)
        - Market conditions (20 points)
        """
        score = 0.0

        # 1. Profit factor (0-30 points)
        pnl_pct = pnl_metrics['unrealized_pnl_pct']
        if pnl_pct >= 75:
            score += 30
        elif pnl_pct >= 50:
            score += 25
        elif pnl_pct >= 25:
            score += 20
        elif pnl_pct >= 0:
            score += 15
        else:
            score += max(0, 15 + pnl_pct / 10)  # Negative P&L reduces score

        # 2. Time decay factor (0-25 points)
        # More days remaining = better for seller (more time for decay)
        if days_remaining > 30:
            score += 25
        elif days_remaining > 21:
            score += 20
        elif days_remaining > 14:
            score += 15
        elif days_remaining > 7:
            score += 10
        else:
            score += 5

        # 3. Safety margin (0-25 points)
        prob_otm = prob_analysis.get('current_prob_otm', 50)
        if prob_otm >= 80:
            score += 25
        elif prob_otm >= 70:
            score += 20
        elif prob_otm >= 60:
            score += 15
        elif prob_otm >= 50:
            score += 10
        else:
            score += 5

        # 4. Market conditions (0-20 points)
        technical_score = prob_analysis.get('technical_score', 50)
        composite_score = prob_analysis.get('composite_score', 50)

        # Average of technical and composite
        avg_market_score = (technical_score + composite_score) / 2
        score += (avg_market_score / 100) * 20

        # Classify health status
        if score >= 80:
            status = "healthy"
        elif score >= 60:
            status = "warning"
        else:
            status = "critical"

        return score, status

    def _determine_moneyness(
        self,
        position: Dict,
        current_price: float
    ) -> str:
        """Determine if position is ITM, ATM, or OTM"""
        strike = position['strike']
        option_type = position['option_type']

        # Calculate distance from strike
        distance_pct = abs(current_price - strike) / strike * 100

        if distance_pct < 2:  # Within 2%
            return "ATM"
        elif option_type == 'put':
            if current_price < strike:
                return "ITM"
            else:
                return "OTM"
        else:  # call
            if current_price > strike:
                return "ITM"
            else:
                return "OTM"

    def _assess_risk_factors(
        self,
        position: Dict,
        prob_analysis: Dict,
        days_remaining: int
    ) -> List[str]:
        """Identify risk factors for position"""
        risk_factors = []

        # Check probability deterioration
        prob_change = prob_analysis.get('prob_change', 0)
        if prob_change < -10:
            risk_factors.append(f"Probability dropped {abs(prob_change):.1f}%")

        # Check event risk
        days_to_earnings = prob_analysis.get('days_to_earnings')
        if days_to_earnings and days_to_earnings <= self.settings['risk_thresholds']['earnings_warning_days']:
            risk_factors.append(f"Earnings in {days_to_earnings} days")

        # Check time risk
        if days_remaining <= 7:
            risk_factors.append(f"Only {days_remaining} days to expiration")

        # Check technical deterioration
        tech_change = prob_analysis.get('technical_score_change', 0)
        if tech_change < -self.settings['risk_thresholds']['technical_score_drop']:
            risk_factors.append(f"Technical score declined {abs(tech_change):.0f} points")

        return risk_factors

    def _determine_action(
        self,
        position: Dict,
        pnl_metrics: Dict,
        prob_analysis: Dict,
        risk_factors: List[str],
        health_score: float,
        moneyness: str,
        days_remaining: int,
        days_held: int
    ) -> Tuple[str, int, str, List[str]]:
        """
        Determine recommended action based on position state

        Returns: (action, urgency, primary_reason, supporting_reasons)
        """
        pnl_pct = pnl_metrics['unrealized_pnl_pct']
        prob_otm = prob_analysis.get('current_prob_otm', 50)

        profit_rules = self.settings['profit_taking_rules']

        # CRITICAL URGENCY (5): Immediate action needed
        if moneyness == "ITM" and days_remaining < 7:
            return (
                "CLOSE_EARLY",
                5,
                f"Position ITM with only {days_remaining} days - assignment risk high",
                ["Immediate action to avoid assignment", "Consider rolling if still want exposure"]
            )

        # CLOSE_EARLY: High profit targets hit
        if pnl_pct >= profit_rules['aggressive_target_pct']:
            return (
                "CLOSE_EARLY",
                4,
                f"Hit aggressive profit target ({pnl_pct:.0f}% >= {profit_rules['aggressive_target_pct']}%)",
                [f"Captured ${pnl_metrics['unrealized_pnl']:.2f} profit", "Excellent outcome - take the win"]
            )

        if pnl_pct >= profit_rules['standard_target_pct'] and days_remaining <= profit_rules['force_close_dte']:
            return (
                "CLOSE_EARLY",
                3,
                f"Hit standard target ({pnl_pct:.0f}%) with {days_remaining} days remaining",
                [f"At {days_remaining} DTE (force close threshold)", "Good profit captured"]
            )

        # CLOSE_EARLY: Risk-based
        if prob_otm < self.settings['risk_thresholds']['min_prob_otm_warning']:
            return (
                "CLOSE_EARLY",
                5,
                f"Probability dropped to {prob_otm:.0f}% (below {self.settings['risk_thresholds']['min_prob_otm_warning']}% threshold)",
                ["High risk of finishing ITM", "Cut losses or adjust position"]
            )

        # ROLL: Approaching expiration but profit target not hit
        if days_remaining <= profit_rules['force_close_dte'] and pnl_pct < profit_rules['standard_target_pct']:
            return (
                "ROLL",
                3,
                f"Approaching {profit_rules['force_close_dte']} DTE with only {pnl_pct:.0f}% profit",
                ["Roll to next expiration to collect more premium", "Extend trade duration"]
            )

        # ADJUST_TARGETS: Conditions changed significantly
        prob_change = prob_analysis.get('prob_change', 0)
        tech_change = prob_analysis.get('technical_score_change', 0)

        if abs(prob_change) > 15 or abs(tech_change) > 15:
            return (
                "ADJUST_TARGETS",
                2,
                "Market conditions changed significantly",
                [
                    f"Probability changed {prob_change:+.1f}%",
                    f"Technical score changed {tech_change:+.0f} points",
                    "Adjust profit targets and stop-loss accordingly"
                ]
            )

        # HOLD: Everything looks good
        supporting = [
            f"Health score: {health_score:.0f}/100 ({health_score})",
            f"Current P&L: {pnl_pct:.0f}% (target: {profit_rules['standard_target_pct']}%)",
            f"Probability OTM: {prob_otm:.0f}%",
            f"{days_remaining} days remaining"
        ]

        return (
            "HOLD",
            1,
            "Position healthy - continue monitoring",
            supporting
        )

    def calculate_optimal_profit_target(
        self,
        position: Dict,
        pnl_metrics: Dict,
        prob_analysis: Dict,
        days_remaining: int
    ) -> Dict:
        """
        Calculate dynamic profit targets and stop-loss

        Returns:
            Dictionary with suggested prices and thresholds
        """
        entry_premium = position['premium']
        current_value = pnl_metrics['current_value'] / (position['contracts'] * 100)

        profit_rules = self.settings['profit_taking_rules']

        # Calculate target prices based on profit %
        aggressive_target_price = entry_premium * (1 - profit_rules['aggressive_target_pct'] / 100)
        standard_target_price = entry_premium * (1 - profit_rules['standard_target_pct'] / 100)
        stop_loss_price = entry_premium * (1 + abs(profit_rules['stop_loss_pct']) / 100)

        # Suggest close price based on current conditions
        pnl_pct = pnl_metrics['unrealized_pnl_pct']
        if pnl_pct >= profit_rules['aggressive_target_pct']:
            suggested_close_price = current_value  # Close now at market
        elif pnl_pct >= profit_rules['standard_target_pct']:
            suggested_close_price = standard_target_price
        else:
            suggested_close_price = None  # Not at target yet

        return {
            'aggressive_target_price': aggressive_target_price,
            'standard_target_price': standard_target_price,
            'stop_loss_price': stop_loss_price,
            'suggested_close_price': suggested_close_price,
            'profit_target_price': standard_target_price,
            'force_close_dte': profit_rules['force_close_dte']
        }


if __name__ == '__main__':
    # Quick test
    from src.portfolio.portfolio_manager import PortfolioManager

    portfolio = PortfolioManager()
    analyzer = PositionAnalyzer()

    print("Testing Position Analyzer...\n")

    # Get open positions
    open_positions = portfolio.get_options_dataframe(status='open')

    if open_positions.empty:
        print("No open positions to analyze.")
        print("\nTo test, add a position using:")
        print("  portfolio.add_option_position(...)")
    else:
        print(f"Analyzing {len(open_positions)} open position(s)...\n")

        for idx, position in open_positions.iterrows():
            recommendation = analyzer.analyze_option_position(position, idx)

            print(f"{idx + 1}. {recommendation.ticker} ${recommendation.strike} {recommendation.option_type.upper()}")
            print(f"   Expires: {recommendation.expiration} ({recommendation.days_remaining} days)")
            print(f"   P&L: ${recommendation.unrealized_pnl:.2f} ({recommendation.unrealized_pnl_pct:.1f}%)")
            print(f"   Health: {recommendation.health_score:.0f}/100 ({recommendation.health_status})")
            print(f"   RECOMMENDATION: {recommendation.action} (Urgency: {recommendation.urgency}/5)")
            print(f"   Reason: {recommendation.primary_reason}")
            print()
