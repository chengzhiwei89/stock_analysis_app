"""
Recommendations Manager
Automatically save and retrieve analysis recommendations
"""
import pandas as pd
import os
from datetime import datetime
from typing import Optional, Dict, List
import json


class RecommendationsManager:
    """Manage saving and loading of analysis recommendations"""

    def __init__(self, recommendations_dir: str = "data/recommendations"):
        """
        Initialize recommendations manager

        Args:
            recommendations_dir: Directory to store recommendations
        """
        self.recommendations_dir = recommendations_dir
        os.makedirs(recommendations_dir, exist_ok=True)

    def save_covered_call_recommendations(self, results: pd.DataFrame,
                                         tickers: List[str],
                                         criteria: Dict,
                                         notes: str = "") -> str:
        """
        Save covered call recommendations

        Args:
            results: DataFrame with CC recommendations
            tickers: List of tickers analyzed
            criteria: Dictionary of criteria used (min_premium, min_annual_return, etc.)
            notes: Optional notes about this analysis

        Returns:
            Path to saved file
        """
        if results.empty:
            print("No results to save")
            return ""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ticker_str = "_".join(tickers) if len(tickers) <= 3 else f"{len(tickers)}tickers"

        # Save CSV
        csv_filename = f"cc_{ticker_str}_{timestamp}.csv"
        csv_path = os.path.join(self.recommendations_dir, csv_filename)
        results.to_csv(csv_path, index=False)

        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'strategy': 'covered_call',
            'tickers': tickers,
            'num_opportunities': len(results),
            'criteria': criteria,
            'notes': notes,
            'csv_file': csv_filename
        }

        metadata_filename = f"cc_{ticker_str}_{timestamp}_meta.json"
        metadata_path = os.path.join(self.recommendations_dir, metadata_filename)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Saved {len(results)} covered call recommendations to: {csv_path}")
        return csv_path

    def save_cash_secured_put_recommendations(self, results: pd.DataFrame,
                                             tickers: List[str],
                                             criteria: Dict,
                                             notes: str = "") -> str:
        """
        Save cash secured put recommendations

        Args:
            results: DataFrame with CSP recommendations
            tickers: List of tickers analyzed
            criteria: Dictionary of criteria used
            notes: Optional notes

        Returns:
            Path to saved file
        """
        if results.empty:
            print("No results to save")
            return ""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ticker_str = "_".join(tickers) if len(tickers) <= 3 else f"{len(tickers)}tickers"

        # Save CSV
        csv_filename = f"csp_{ticker_str}_{timestamp}.csv"
        csv_path = os.path.join(self.recommendations_dir, csv_filename)
        results.to_csv(csv_path, index=False)

        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'strategy': 'cash_secured_put',
            'tickers': tickers,
            'num_opportunities': len(results),
            'criteria': criteria,
            'notes': notes,
            'csv_file': csv_filename
        }

        metadata_filename = f"csp_{ticker_str}_{timestamp}_meta.json"
        metadata_path = os.path.join(self.recommendations_dir, metadata_filename)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Saved {len(results)} cash secured put recommendations to: {csv_path}")
        return csv_path

    def save_wheel_recommendations(self, results: pd.DataFrame,
                                  tickers: List[str],
                                  criteria: Dict,
                                  notes: str = "") -> str:
        """
        Save wheel strategy recommendations

        Args:
            results: DataFrame with Wheel recommendations
            tickers: List of tickers analyzed
            criteria: Dictionary of criteria used
            notes: Optional notes

        Returns:
            Path to saved file
        """
        if results.empty:
            print("No results to save")
            return ""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ticker_str = "_".join(tickers) if len(tickers) <= 3 else f"{len(tickers)}tickers"

        # Save CSV
        csv_filename = f"wheel_{ticker_str}_{timestamp}.csv"
        csv_path = os.path.join(self.recommendations_dir, csv_filename)
        results.to_csv(csv_path, index=False)

        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'strategy': 'wheel',
            'tickers': tickers,
            'num_opportunities': len(results),
            'criteria': criteria,
            'notes': notes,
            'csv_file': csv_filename
        }

        metadata_filename = f"wheel_{ticker_str}_{timestamp}_meta.json"
        metadata_path = os.path.join(self.recommendations_dir, metadata_filename)
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Saved {len(results)} wheel strategy recommendations to: {csv_path}")
        return csv_path

    def save_all_recommendations(self, cc_results: Optional[pd.DataFrame] = None,
                                csp_results: Optional[pd.DataFrame] = None,
                                wheel_results: Optional[pd.DataFrame] = None,
                                tickers: List[str] = None,
                                criteria: Dict = None,
                                notes: str = ""):
        """
        Save multiple recommendation types at once

        Args:
            cc_results: Covered call results
            csp_results: Cash secured put results
            wheel_results: Wheel strategy results
            tickers: List of tickers
            criteria: Criteria used
            notes: Optional notes
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ticker_str = "_".join(tickers) if tickers and len(tickers) <= 3 else "multi"

        saved_files = []

        if cc_results is not None and not cc_results.empty:
            path = self.save_covered_call_recommendations(cc_results, tickers, criteria, notes)
            saved_files.append(('Covered Calls', path, len(cc_results)))

        if csp_results is not None and not csp_results.empty:
            path = self.save_cash_secured_put_recommendations(csp_results, tickers, criteria, notes)
            saved_files.append(('Cash Secured Puts', path, len(csp_results)))

        if wheel_results is not None and not wheel_results.empty:
            path = self.save_wheel_recommendations(wheel_results, tickers, criteria, notes)
            saved_files.append(('Wheel Strategy', path, len(wheel_results)))

        # Create a combined Excel file
        if saved_files:
            excel_filename = f"all_strategies_{ticker_str}_{timestamp}.xlsx"
            excel_path = os.path.join(self.recommendations_dir, excel_filename)

            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                if cc_results is not None and not cc_results.empty:
                    cc_results.to_excel(writer, sheet_name='Covered_Calls', index=False)
                if csp_results is not None and not csp_results.empty:
                    csp_results.to_excel(writer, sheet_name='Cash_Secured_Puts', index=False)
                if wheel_results is not None and not wheel_results.empty:
                    wheel_results.to_excel(writer, sheet_name='Wheel_Strategy', index=False)

            print(f"\n✓ Saved combined Excel file: {excel_path}")

            # Summary
            print("\nSummary of saved recommendations:")
            print("-" * 80)
            for strategy, path, count in saved_files:
                print(f"  {strategy:20} {count:3} opportunities -> {os.path.basename(path)}")

    def list_recommendations(self, strategy: Optional[str] = None,
                           ticker: Optional[str] = None) -> List[Dict]:
        """
        List saved recommendations

        Args:
            strategy: Filter by strategy ('cc', 'csp', 'wheel', or None for all)
            ticker: Filter by ticker (or None for all)

        Returns:
            List of recommendation metadata
        """
        import glob

        # Find all metadata files
        meta_files = glob.glob(os.path.join(self.recommendations_dir, "*_meta.json"))

        def get_sort_key(filepath):
            # Extracts timestamp from filenames like 'csp_TICK_20230101_120000_meta.json'
            filename = os.path.basename(filepath)
            parts = filename.split('_')
            if len(parts) >= 4:
                return parts[-2] + parts[-1].split('.')[0]
            return filename # Fallback

        recommendations = []
        for meta_file in sorted(meta_files, key=get_sort_key, reverse=True):
            try:
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)

                # Apply filters
                if strategy:
                    strategy_map = {'cc': 'covered_call', 'csp': 'cash_secured_put', 'wheel': 'wheel'}
                    if metadata.get('strategy') != strategy_map.get(strategy, strategy):
                        continue

                if ticker:
                    if ticker.upper() not in [t.upper() for t in metadata.get('tickers', [])]:
                        continue

                recommendations.append(metadata)
            except Exception as e:
                print(f"Error reading {meta_file}: {e}")

        return recommendations

    def load_recommendation(self, csv_filename: str) -> pd.DataFrame:
        """
        Load a specific recommendation file

        Args:
            csv_filename: Name of CSV file to load

        Returns:
            DataFrame with recommendations
        """
        csv_path = os.path.join(self.recommendations_dir, csv_filename)
        if not os.path.exists(csv_path):
            print(f"File not found: {csv_path}")
            return pd.DataFrame()

        return pd.read_csv(csv_path)

    def load_latest_recommendation(self, strategy: str, ticker: Optional[str] = None) -> pd.DataFrame:
        """
        Load the most recent recommendation for a strategy

        Args:
            strategy: 'cc', 'csp', or 'wheel'
            ticker: Optional ticker filter

        Returns:
            DataFrame with recommendations
        """
        recommendations = self.list_recommendations(strategy=strategy, ticker=ticker)

        if not recommendations:
            print(f"No {strategy} recommendations found")
            return pd.DataFrame()

        latest = recommendations[0]
        print(f"Loading latest {strategy} recommendations from {latest['timestamp']}")
        return self.load_recommendation(latest['csv_file'])

    def get_summary(self) -> str:
        """
        Get summary of all saved recommendations

        Returns:
            Summary string
        """
        recommendations = self.list_recommendations()

        if not recommendations:
            return "No saved recommendations found."

        # Group by strategy
        by_strategy = {}
        for rec in recommendations:
            strategy = rec.get('strategy', 'unknown')
            if strategy not in by_strategy:
                by_strategy[strategy] = []
            by_strategy[strategy].append(rec)

        summary = f"Total Recommendations: {len(recommendations)}\n"
        summary += "=" * 60 + "\n\n"

        for strategy, recs in by_strategy.items():
            summary += f"{strategy.upper().replace('_', ' ')}:\n"
            summary += f"  Files: {len(recs)}\n"
            summary += f"  Most recent: {recs[0]['timestamp']}\n"
            summary += f"  Total opportunities: {sum(r['num_opportunities'] for r in recs)}\n\n"

        return summary

    def cleanup_old_recommendations(self, keep_days: int = 7):
        """
        Remove recommendations older than specified days

        Args:
            keep_days: Number of days to keep
        """
        import glob
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=keep_days)
        cutoff_str = cutoff_date.strftime('%Y%m%d')

        # Find all files
        all_files = glob.glob(os.path.join(self.recommendations_dir, "*"))

        removed_count = 0
        for file_path in all_files:
            filename = os.path.basename(file_path)

            # Extract date from filename (format: strategy_ticker_YYYYMMDD_HHMMSS.ext)
            parts = filename.split('_')
            if len(parts) >= 3:
                try:
                    file_date = parts[-2]  # YYYYMMDD part
                    if file_date < cutoff_str:
                        os.remove(file_path)
                        removed_count += 1
                except:
                    pass

        print(f"Removed {removed_count} old recommendation files (older than {keep_days} days)")
