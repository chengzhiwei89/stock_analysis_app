"""
HTML Dashboard Generator
Generates interactive HTML dashboards for options trading opportunities
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape


class HTMLDashboardGenerator:
    """Generate interactive HTML dashboard for options strategies"""

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the dashboard generator

        Args:
            config: Optional configuration dictionary with settings like:
                - theme: 'light' or 'dark' (default: 'light')
                - max_opportunities: Max items to show per strategy (default: 20)
                - output_dir: Directory for output files (default: 'output/dashboards')
        """
        self.config = config or {}
        self.theme = self.config.get('theme', 'light')
        self.max_opportunities = self.config.get('max_opportunities', 20)
        self.output_dir = self.config.get('output_dir', 'output/dashboards')

        # Set up Jinja2 template environment
        self.template_env = self._setup_jinja_env()

    def _setup_jinja_env(self) -> Environment:
        """Set up Jinja2 template environment"""
        # Get the templates directory relative to this file
        template_dir = Path(__file__).parent / 'templates'

        env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        env.filters['format_currency'] = self._format_currency
        env.filters['format_percent'] = self._format_percent
        env.filters['format_date'] = self._format_date
        env.filters['risk_color'] = self._get_risk_color

        return env

    def generate(
        self,
        csp_results: Optional[pd.DataFrame] = None,
        cc_results: Optional[pd.DataFrame] = None,
        wheel_results: Optional[pd.DataFrame] = None,
        leaps_results: Optional[pd.DataFrame] = None,
        metadata: Optional[Dict] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate complete HTML dashboard

        Args:
            csp_results: DataFrame with cash secured put opportunities
            cc_results: DataFrame with covered call opportunities
            wheel_results: DataFrame with wheel strategy opportunities
            leaps_results: DataFrame with LEAPS call bet opportunities
            metadata: Dictionary with scan metadata (timestamp, market status, etc.)
            output_path: Optional custom output path

        Returns:
            Path to generated HTML file
        """
        # Use empty DataFrames if None provided
        csp_results = csp_results if csp_results is not None else pd.DataFrame()
        cc_results = cc_results if cc_results is not None else pd.DataFrame()
        wheel_results = wheel_results if wheel_results is not None else pd.DataFrame()
        leaps_results = leaps_results if leaps_results is not None else pd.DataFrame()

        metadata = metadata or {}

        # Limit number of opportunities
        csp_results = csp_results.head(self.max_opportunities) if not csp_results.empty else csp_results
        cc_results = cc_results.head(self.max_opportunities) if not cc_results.empty else cc_results
        wheel_results = wheel_results.head(self.max_opportunities) if not wheel_results.empty else wheel_results
        leaps_results = leaps_results.head(self.max_opportunities) if not leaps_results.empty else leaps_results

        # Calculate summary statistics
        summary = self._calculate_summary_stats(csp_results, cc_results, wheel_results, leaps_results)

        # Prepare chart data
        csp_chart_data = self._prepare_csp_charts(csp_results)
        cc_chart_data = self._prepare_cc_charts(cc_results)
        wheel_chart_data = self._prepare_wheel_charts(wheel_results)

        # Convert DataFrames to list of dicts for templates
        csp_data = csp_results.to_dict('records') if not csp_results.empty else []
        cc_data = cc_results.to_dict('records') if not cc_results.empty else []
        wheel_data = wheel_results.to_dict('records') if not wheel_results.empty else []
        leaps_data = leaps_results.to_dict('records') if not leaps_results.empty else []

        # Render template
        html = self._render_dashboard(
            csp_data=csp_data,
            cc_data=cc_data,
            wheel_data=wheel_data,
            leaps_data=leaps_data,
            csp_charts=csp_chart_data,
            cc_charts=cc_chart_data,
            wheel_charts=wheel_chart_data,
            summary=summary,
            metadata=metadata,
            theme=self.theme
        )

        # Save to file
        output_path = output_path or self._generate_filename()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_path

    def _calculate_summary_stats(
        self,
        csp_df: pd.DataFrame,
        cc_df: pd.DataFrame,
        wheel_df: pd.DataFrame,
        leaps_df: pd.DataFrame
    ) -> Dict:
        """Calculate summary statistics across all strategies"""

        summary = {
            'total_opportunities': len(csp_df) + len(cc_df) + len(wheel_df) + len(leaps_df),
            'csp_count': len(csp_df),
            'cc_count': len(cc_df),
            'wheel_count': len(wheel_df),
            'leaps_count': len(leaps_df),
        }

        # CSP stats
        if not csp_df.empty and 'annual_return' in csp_df.columns:
            summary['csp_avg_return'] = csp_df['annual_return'].mean()
            summary['csp_max_return'] = csp_df['annual_return'].max()

            if 'strike' in csp_df.columns:
                summary['csp_total_capital'] = (csp_df['strike'] * 100).sum()
        else:
            summary['csp_avg_return'] = 0
            summary['csp_max_return'] = 0
            summary['csp_total_capital'] = 0

        # CC stats
        if not cc_df.empty and 'annual_return' in cc_df.columns:
            summary['cc_avg_return'] = cc_df['annual_return'].mean()
            summary['cc_max_return'] = cc_df['annual_return'].max()
        else:
            summary['cc_avg_return'] = 0
            summary['cc_max_return'] = 0

        # Wheel stats
        if not wheel_df.empty and 'annual_return' in wheel_df.columns:
            summary['wheel_avg_return'] = wheel_df['annual_return'].mean()
            summary['wheel_max_return'] = wheel_df['annual_return'].max()
        else:
            summary['wheel_avg_return'] = 0
            summary['wheel_max_return'] = 0

        # Overall stats
        all_returns = []
        if not csp_df.empty and 'annual_return' in csp_df.columns:
            all_returns.extend(csp_df['annual_return'].tolist())
        if not cc_df.empty and 'annual_return' in cc_df.columns:
            all_returns.extend(cc_df['annual_return'].tolist())
        if not wheel_df.empty and 'annual_return' in wheel_df.columns:
            all_returns.extend(wheel_df['annual_return'].tolist())

        summary['avg_return_all'] = sum(all_returns) / len(all_returns) if all_returns else 0
        summary['total_capital'] = summary.get('csp_total_capital', 0)

        return summary

    def _prepare_csp_charts(self, csp_df: pd.DataFrame) -> Dict:
        """Prepare chart data for CSP section"""
        if csp_df.empty:
            return {}

        chart_data = {}

        # Return distribution histogram
        if 'annual_return' in csp_df.columns:
            returns = csp_df['annual_return'].tolist()
            chart_data['return_distribution'] = {
                'labels': ['0-10%', '10-20%', '20-30%', '30%+'],
                'data': [
                    sum(1 for r in returns if r < 10),
                    sum(1 for r in returns if 10 <= r < 20),
                    sum(1 for r in returns if 20 <= r < 30),
                    sum(1 for r in returns if r >= 30)
                ]
            }

        # Risk/Reward scatter plot
        if 'annual_return' in csp_df.columns and 'prob_otm' in csp_df.columns:
            scatter_data = []
            for _, row in csp_df.iterrows():
                scatter_data.append({
                    'x': row.get('annual_return', 0),
                    'y': row.get('prob_otm', 0),
                    'label': row.get('ticker', 'N/A'),
                    'strike': row.get('strike', 0),
                    'premium': row.get('premium_received', 0)
                })
            chart_data['risk_reward_scatter'] = scatter_data

        # Capital requirements pie chart (top 5 tickers by capital)
        if 'ticker' in csp_df.columns and 'strike' in csp_df.columns:
            # Calculate capital required for each opportunity (strike * 100)
            capital_by_ticker = {}
            for _, row in csp_df.iterrows():
                ticker = row.get('ticker', 'N/A')
                strike = row.get('strike', 0)
                capital = strike * 100  # Each contract = 100 shares

                if ticker in capital_by_ticker:
                    capital_by_ticker[ticker] += capital
                else:
                    capital_by_ticker[ticker] = capital

            # Sort by capital and take top 5
            sorted_capital = sorted(capital_by_ticker.items(), key=lambda x: x[1], reverse=True)
            top_5 = sorted_capital[:5]
            others = sorted_capital[5:]

            labels = [ticker for ticker, _ in top_5]
            data = [capital for _, capital in top_5]

            # Add "Others" category if there are more than 5 tickers
            if others:
                labels.append('Others')
                data.append(sum(capital for _, capital in others))

            chart_data['capital_requirements'] = {
                'labels': labels,
                'data': data
            }

        return chart_data

    def _prepare_cc_charts(self, cc_df: pd.DataFrame) -> Dict:
        """Prepare chart data for CC section"""
        if cc_df.empty:
            return {}

        chart_data = {}

        # Similar structure to CSP charts
        if 'annual_return' in cc_df.columns:
            returns = cc_df['annual_return'].tolist()
            chart_data['return_distribution'] = {
                'labels': ['0-10%', '10-20%', '20-30%', '30%+'],
                'data': [
                    sum(1 for r in returns if r < 10),
                    sum(1 for r in returns if 10 <= r < 20),
                    sum(1 for r in returns if 20 <= r < 30),
                    sum(1 for r in returns if r >= 30)
                ]
            }

        return chart_data

    def _prepare_wheel_charts(self, wheel_df: pd.DataFrame) -> Dict:
        """Prepare chart data for Wheel section"""
        if wheel_df.empty:
            return {}

        chart_data = {}

        # Entry discount distribution
        if 'discount_pct' in wheel_df.columns:
            discounts = wheel_df['discount_pct'].tolist()
            chart_data['discount_distribution'] = {
                'labels': ['0-5%', '5-10%', '10-15%', '15%+'],
                'data': [
                    sum(1 for d in discounts if d < 5),
                    sum(1 for d in discounts if 5 <= d < 10),
                    sum(1 for d in discounts if 10 <= d < 15),
                    sum(1 for d in discounts if d >= 15)
                ]
            }

        return chart_data

    def _render_dashboard(
        self,
        csp_data: List[Dict],
        cc_data: List[Dict],
        wheel_data: List[Dict],
        leaps_data: List[Dict],
        csp_charts: Dict,
        cc_charts: Dict,
        wheel_charts: Dict,
        summary: Dict,
        metadata: Dict,
        theme: str
    ) -> str:
        """Render the complete dashboard HTML"""

        template = self.template_env.get_template('base.html')

        html = template.render(
            csp_data=csp_data,
            cc_data=cc_data,
            wheel_data=wheel_data,
            leaps_data=leaps_data,
            csp_charts=csp_charts,
            cc_charts=cc_charts,
            wheel_charts=wheel_charts,
            summary=summary,
            metadata=metadata,
            theme=theme,
            generated_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )

        return html

    def _generate_filename(self) -> str:
        """Generate output filename with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'dashboard_{timestamp}.html'
        return os.path.join(self.output_dir, filename)

    # Jinja2 filter functions
    @staticmethod
    def _format_currency(value) -> str:
        """Format value as currency"""
        try:
            return f"${float(value):,.2f}"
        except (ValueError, TypeError):
            return "$0.00"

    @staticmethod
    def _format_percent(value, decimals=1) -> str:
        """Format value as percentage"""
        try:
            return f"{float(value):.{decimals}f}%"
        except (ValueError, TypeError):
            return "0.0%"

    @staticmethod
    def _format_date(value) -> str:
        """Format date value"""
        if isinstance(value, str):
            try:
                dt = pd.to_datetime(value)
                return dt.strftime('%Y-%m-%d')
            except:
                return value
        elif hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')
        return str(value)

    @staticmethod
    def _get_risk_color(value, metric_type='return') -> str:
        """Get color class based on risk metric"""
        try:
            val = float(value)
        except (ValueError, TypeError):
            return 'text-secondary'

        if metric_type == 'return':
            if val >= 30:
                return 'text-success'  # Green
            elif val >= 20:
                return 'text-success-light'  # Lime
            elif val >= 15:
                return 'text-warning'  # Yellow
            else:
                return 'text-danger'  # Red
        elif metric_type == 'probability':
            if val >= 75:
                return 'text-success'
            elif val >= 65:
                return 'text-warning'
            else:
                return 'text-danger'

        return 'text-secondary'
