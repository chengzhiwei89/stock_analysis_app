# Product Requirements Document (PRD)
# Enhancement R1: HTML Visualization Dashboard for Options Strategies

**Version**: 1.0
**Date**: 2025-10-27
**Status**: Draft
**Owner**: Options Analysis System

---

## Executive Summary

Create an interactive HTML dashboard that visualizes the top options trading opportunities across three strategies: Cash Secured Puts (CSP), Covered Calls (CC), and Wheel Strategy. The dashboard will provide traders with an at-a-glance view of opportunities, risk metrics, and actionable insights.

---

## Problem Statement

### Current State
- Analysis results are displayed only in terminal/console output
- No visual comparison across strategies
- Difficult to spot patterns and relationships between opportunities
- No persistent, shareable output for review and decision-making
- Cannot easily compare opportunities side-by-side

### Desired State
- Interactive HTML dashboard with charts, tables, and metrics
- Visual comparison of opportunities across all three strategies
- Risk/reward visualization with color-coded indicators
- Exportable, shareable reports
- Historical tracking and trend analysis

---

## Goals and Objectives

### Primary Goals
1. **Visualization**: Create clear, actionable visualizations of trading opportunities
2. **Accessibility**: Generate shareable HTML reports that work in any browser
3. **Decision Support**: Help traders quickly identify best opportunities with visual risk/reward profiles
4. **Insight Discovery**: Enable pattern recognition through visual data representation

### Success Metrics
- Dashboard loads in < 3 seconds
- All data visualized without information loss
- 100% browser compatibility (Chrome, Firefox, Safari, Edge)
- Mobile-responsive design
- Export functionality works reliably

---

## User Stories

### As a Trader
1. **Dashboard Overview**: "I want to see top 10 opportunities for each strategy on one page so I can quickly decide which trades to execute"
2. **Risk Visualization**: "I want to see risk metrics (probability, delta, IV) visualized with color coding so I can assess risk at a glance"
3. **Comparison**: "I want to compare opportunities side-by-side to choose the best risk/reward"
4. **Filtering**: "I want to filter opportunities by ticker, expiration, or return threshold"
5. **Details**: "I want to drill down into each opportunity to see all metrics and analysis"
6. **Export**: "I want to save the dashboard as HTML to review later or share with my trading group"

### As a Portfolio Manager
1. **Capital Allocation**: "I want to see total capital requirements across all opportunities"
2. **Diversification**: "I want to visualize sector/ticker distribution to ensure diversification"
3. **Historical Context**: "I want to see how current opportunities compare to historical averages"

---

## Functional Requirements

### FR-1: Dashboard Layout
**Priority**: MUST HAVE

#### FR-1.1: Header Section
- App title and version
- Scan timestamp
- Market status indicator (OPEN/CLOSED)
- Summary statistics (total opportunities, total capital required)

#### FR-1.2: Strategy Tabs/Sections
- Three main sections: CSP, CC, Wheel
- Tab navigation or scrollable sections
- Each section shows top N opportunities (configurable, default 10)

#### FR-1.3: Footer Section
- Generation timestamp
- Disclaimer text
- Export button

### FR-2: Cash Secured Put (CSP) Visualization
**Priority**: MUST HAVE

#### FR-2.1: Summary Cards
- Total CSP opportunities found
- Average annual return
- Total capital required
- Highest probability opportunity

#### FR-2.2: Opportunities Table
Columns:
- Ticker
- Strike Price
- Expiration Date
- Days to Expiration
- Premium ($ and %)
- Annual Return %
- Probability OTM %
- Enhanced Probability %
- Distance from Current %
- Volume / Open Interest
- Action button (copy trade details)

Features:
- Sortable by any column
- Color-coded annual return (Green > 20%, Yellow 15-20%, Red < 15%)
- Color-coded probability (Green > 75%, Yellow 65-75%, Red < 65%)
- Hover tooltips with additional details

#### FR-2.3: CSP Charts
1. **Return Distribution Chart** (Bar/Histogram)
   - X-axis: Annual return buckets (0-10%, 10-20%, 20-30%, 30%+)
   - Y-axis: Count of opportunities

2. **Risk/Reward Scatter Plot**
   - X-axis: Annual Return %
   - Y-axis: Probability OTM %
   - Bubble size: Premium amount
   - Color: Ticker
   - Quadrant lines at 15% return, 70% prob

3. **Capital Requirements Pie Chart**
   - Show top 5 tickers by capital required
   - "Others" for remaining

### FR-3: Covered Call (CC) Visualization
**Priority**: MUST HAVE

#### FR-3.1: Summary Cards
- Total CC opportunities
- Average annual return
- Average downside protection %
- Best opportunity (highest return + protection)

#### FR-3.2: Opportunities Table
Columns:
- Ticker
- Strike Price
- Current Price
- Expiration Date
- Days to Expiration
- Premium ($ and %)
- Annual Return %
- Downside Protection %
- Distance from Strike %
- Probability OTM %
- Volume / Open Interest
- Action button

Features:
- Same sorting and color-coding as CSP
- Downside protection highlighted (Green > 5%, Yellow 3-5%, Red < 3%)

#### FR-3.3: CC Charts
1. **Return vs Protection Scatter**
   - X-axis: Annual Return %
   - Y-axis: Downside Protection %
   - Identify "sweet spot" opportunities

2. **Strike Distribution Chart**
   - Show ITM vs OTM vs ATM breakdown

### FR-4: Wheel Strategy Visualization
**Priority**: MUST HAVE

#### FR-4.1: Summary Cards
- Total wheel candidates
- Average entry discount %
- Average put phase annual return
- Total potential positions

#### FR-4.2: Opportunities Table
Columns:
- Ticker
- Current Price
- PUT Strike
- PUT Expiration
- PUT Premium
- Entry Discount %
- Net Entry Price
- Annual Return (PUT phase)
- Probability of Assignment
- Volume / Open Interest
- Suggested CALL Strike (for phase 2)
- Action button

#### FR-4.3: Wheel Charts
1. **Entry Discount Distribution**
   - Bar chart showing discount buckets

2. **PUT Phase Timeline**
   - Gantt-style chart showing when each PUT expires
   - Color by ticker

### FR-5: Cross-Strategy Comparison
**Priority**: SHOULD HAVE

#### FR-5.1: Strategy Comparison Table
- Side-by-side comparison of best opportunity from each strategy
- Metrics: Return, Risk, Capital Required, Time Horizon

#### FR-5.2: Unified Risk/Reward Chart
- All opportunities from all strategies on one scatter plot
- Different marker shapes for each strategy (circle=CSP, square=CC, triangle=Wheel)

### FR-6: Filtering and Interaction
**Priority**: SHOULD HAVE

#### FR-6.1: Global Filters (Top of Dashboard)
- Ticker search/filter (multi-select)
- Minimum annual return slider
- Maximum days to expiration slider
- Minimum probability OTM slider
- Strategy selector (show/hide sections)

#### FR-6.2: Table Interactions
- Click to expand row for full details
- Copy trade details to clipboard
- Export individual strategy to CSV

#### FR-6.3: Chart Interactions
- Hover tooltips with full details
- Click data point to highlight corresponding table row
- Zoom/pan on scatter plots

### FR-7: Enhanced Probability Analysis Display
**Priority**: MUST HAVE

#### FR-7.1: Probability Comparison
- Visual indicator showing Black-Scholes vs Enhanced probability
- Delta display (arrow up/down) with percentage adjustment
- Color coding: Green (safer), Yellow (neutral), Red (riskier)

#### FR-7.2: Factor Scores Visualization
For each opportunity (in expanded detail view):
- Technical Score (0-100) - Progress bar
- Fundamental Score (0-100) - Progress bar
- Sentiment Score (0-100) - Progress bar
- Event Risk Score (0-100) - Progress bar
- Composite Score (0-100) - Overall rating

#### FR-7.3: Recommendation Badge
- "EXCELLENT" - Green badge
- "GOOD" - Blue badge
- "FAIR" - Yellow badge
- "CAUTION" - Red badge

### FR-8: Export and Sharing
**Priority**: MUST HAVE

#### FR-8.1: Export Options
- Save as standalone HTML file (includes all CSS/JS inline)
- Export individual strategy as CSV
- Export all strategies as Excel workbook (multiple sheets)

#### FR-8.2: Report Metadata
- Scan timestamp
- Configuration used (min_return, max_days, etc.)
- Market conditions (open/closed, price source used)

---

## Technical Requirements

### TR-1: Technology Stack
**Priority**: MUST HAVE

#### TR-1.1: HTML/CSS Framework
- Use Bootstrap 5 or Tailwind CSS for responsive layout
- No external CDN dependencies (embed all CSS)
- Mobile-first responsive design
- Dark mode support (optional toggle)

#### TR-1.2: JavaScript Libraries
- **Charts**: Chart.js or Plotly.js (for interactive charts)
- **Tables**: DataTables.js (for sorting, filtering, pagination)
- **Data Management**: No dependencies, use vanilla JS or lightweight library
- All libraries embedded inline (no CDN dependencies)

#### TR-1.3: Python Backend
- New module: `src/visualization/html_generator.py`
- Template engine: Jinja2 for HTML templating
- Data preparation: Convert pandas DataFrames to JSON for charts

### TR-2: File Structure
**Priority**: MUST HAVE

```
src/visualization/
├── __init__.py
├── html_generator.py          # Main generator class
├── templates/
│   ├── base.html              # Base template with header/footer
│   ├── csp_section.html       # CSP opportunities section
│   ├── cc_section.html        # CC opportunities section
│   ├── wheel_section.html     # Wheel opportunities section
│   ├── charts.html            # Chart templates
│   └── components/
│       ├── summary_card.html  # Reusable summary card
│       ├── table.html         # Reusable table component
│       └── filters.html       # Filter controls
├── static/
│   ├── css/
│   │   └── dashboard.css      # Custom styles
│   └── js/
│       ├── dashboard.js       # Interactive functionality
│       └── charts.js          # Chart generation code
└── utils/
    ├── data_transformer.py    # Transform analysis results to chart data
    └── color_schemes.py       # Color coding logic
```

### TR-3: Data Flow
**Priority**: MUST HAVE

```
run_scan.py
  ↓
CSPAnalyzer.get_top_opportunities() → DataFrame
CCAnalyzer.get_top_opportunities() → DataFrame
WheelAnalyzer.get_top_opportunities() → DataFrame
  ↓
HTMLDashboardGenerator.generate()
  ↓
├── Transform DataFrames to JSON
├── Calculate summary statistics
├── Generate chart data structures
├── Render Jinja2 templates
└── Embed CSS/JS inline
  ↓
output/dashboard_YYYYMMDD_HHMMSS.html
```

### TR-4: Performance Requirements
**Priority**: MUST HAVE

- Dashboard generation: < 2 seconds for 50 opportunities
- HTML file size: < 2MB (with embedded libraries)
- Page load time: < 3 seconds on average hardware
- Smooth scrolling and interaction (60fps)

### TR-5: Browser Compatibility
**Priority**: MUST HAVE

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Android)

---

## Design Specifications

### DS-1: Color Scheme

#### Primary Colors
- Background: `#1a1a2e` (dark) or `#ffffff` (light)
- Primary: `#0f4c81` (blue)
- Success: `#10b981` (green)
- Warning: `#f59e0b` (yellow)
- Danger: `#ef4444` (red)
- Info: `#3b82f6` (light blue)

#### Risk Color Coding
- **Annual Return**:
  - Excellent (>30%): `#10b981` (green)
  - Good (20-30%): `#84cc16` (lime)
  - Fair (15-20%): `#f59e0b` (yellow)
  - Poor (<15%): `#ef4444` (red)

- **Probability OTM**:
  - High (>75%): `#10b981` (green)
  - Medium (65-75%): `#f59e0b` (yellow)
  - Low (<65%): `#ef4444` (red)

### DS-2: Typography
- **Headers**: System fonts (San Francisco, Segoe UI, Roboto)
- **Body**: 14-16px, line-height 1.5
- **Monospace** (for numbers): Consolas, Monaco, 'Courier New'

### DS-3: Layout Mockup (ASCII)

```
+------------------------------------------------------------------+
|  OPTIONS TRADING DASHBOARD v1.1        [Market: OPEN]  🔄 Refresh |
|  Generated: 2025-10-27 15:30:45                                   |
+------------------------------------------------------------------+
|                                                                   |
|  [Summary Cards Row]                                             |
|  +---------------+  +---------------+  +---------------+          |
|  | Total Opps    |  | Avg Return    |  | Total Capital |          |
|  |     47        |  |    22.3%      |  |   $847,250    |          |
|  +---------------+  +---------------+  +---------------+          |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  [Filters]                                                       |
|  Ticker: [All ▼]  Min Return: [15%====|====30%]  Max Days: [60] |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  === CASH SECURED PUTS ==========================================  |
|                                                                   |
|  [CSP Summary Cards]                                             |
|                                                                   |
|  [CSP Opportunities Table]                                       |
|  Ticker | Strike | Exp Date | Premium | Annual% | Prob% | Action |
|  -------|--------|----------|---------|---------|-------|--------|
|  GOOGL  | $260   | Nov 21   | $8.20   | 48.0%   | 71.1% | [Copy] |
|  GOOGL  | $255   | Nov 21   | $6.25   | 37.3%   | 78.0% | [Copy] |
|  ...                                                              |
|                                                                   |
|  [CSP Charts Row]                                                |
|  +----------------------+  +----------------------+               |
|  | Return Distribution  |  | Risk/Reward Scatter  |               |
|  |  [Bar Chart]        |  |  [Scatter Plot]     |               |
|  +----------------------+  +----------------------+               |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  === COVERED CALLS ===============================================  |
|  [Similar structure to CSP]                                      |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  === WHEEL STRATEGY ==============================================  |
|  [Similar structure to CSP/CC]                                   |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  === CROSS-STRATEGY COMPARISON ===================================  |
|  [Unified chart with all strategies]                            |
|                                                                   |
+------------------------------------------------------------------+
|                                                                   |
|  [Export] [Refresh Data] [Settings]                             |
|                                                                   |
|  Generated by Options Analysis System | Disclaimer: [link]      |
+------------------------------------------------------------------+
```

### DS-4: Responsive Breakpoints
- Desktop: > 1200px (3-column layout)
- Tablet: 768px - 1200px (2-column layout)
- Mobile: < 768px (1-column layout, stacked sections)

---

## Data Requirements

### DR-1: Input Data Format

#### From CSP Analyzer
```python
{
    'ticker': str,
    'strike': float,
    'current_stock_price': float,
    'expiration': datetime,
    'days_to_expiration': int,
    'premium_received': float,
    'price_source': str,  # 'bid', 'lastPrice', 'ask/2'
    'annual_return': float,
    'prob_otm': float,
    'enhanced_prob_otm': float,
    'prob_adjustment': float,
    'technical_score': float,
    'fundamental_score': float,
    'sentiment_score': float,
    'event_risk_score': float,
    'composite_score': float,
    'recommendation': str,  # 'EXCELLENT', 'GOOD', 'FAIR', 'CAUTION'
    'distance_pct': float,
    'volume': int,
    'openInterest': int,
    'bid': float,
    'ask': float,
    'lastPrice': float
}
```

#### From CC Analyzer
```python
{
    'ticker': str,
    'strike': float,
    'current_stock_price': float,
    'expiration': datetime,
    'days_to_expiration': int,
    'premium_received': float,
    'annual_return': float,
    'downside_protection': float,
    'downside_protection_pct': float,
    'distance_pct': float,
    'prob_otm': float,
    'volume': int,
    'openInterest': int
}
```

#### From Wheel Analyzer
```python
{
    'ticker': str,
    'current_price': float,
    'strike': float,
    'expiration': datetime,
    'days': int,
    'premium': float,
    'discount_pct': float,
    'net_entry': float,
    'total_discount_pct': float,
    'annual_return': float,
    'volume': int,
    'prob_assignment': float
}
```

### DR-2: Configuration Data
```python
{
    'scan_timestamp': datetime,
    'market_status': str,  # 'OPEN', 'CLOSED'
    'tickers_scanned': list[str],
    'settings': {
        'min_premium': float,
        'min_annual_return': float,
        'min_days': int,
        'max_days': int,
        'min_prob_otm': float,
        'min_volume': int
    }
}
```

---

## Success Metrics

### Quantitative Metrics
1. **Performance**:
   - Dashboard generation time < 2s
   - HTML file size < 2MB
   - Page load time < 3s

2. **Completeness**:
   - 100% of analysis data visualized
   - Zero data loss in transformation
   - All 3 strategies represented

3. **Usability**:
   - All tables sortable
   - All charts interactive
   - Mobile responsive (passes Google Mobile-Friendly test)

### Qualitative Metrics
1. **User Satisfaction**:
   - Dashboard provides clear visual insights
   - Easy to identify best opportunities
   - Facilitates faster trading decisions

2. **Maintainability**:
   - Code is modular and testable
   - Easy to add new chart types
   - Template system allows quick updates

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Basic HTML generation with static data

- [ ] Create project structure (`src/visualization/`)
- [ ] Set up Jinja2 templating
- [ ] Create base HTML template with Bootstrap
- [ ] Implement `HTMLDashboardGenerator` class skeleton
- [ ] Test with hardcoded sample data

**Deliverable**: Static HTML dashboard with sample data

### Phase 2: CSP Section (Week 1-2)
**Goal**: Complete CSP visualization

- [ ] Implement CSP data transformation
- [ ] Create CSP opportunities table (sortable)
- [ ] Add CSP summary cards
- [ ] Implement Chart.js integration
- [ ] Create CSP charts (return distribution, risk/reward scatter)
- [ ] Add color coding for risk metrics
- [ ] Test with real CSP analyzer output

**Deliverable**: Fully functional CSP section

### Phase 3: CC and Wheel Sections (Week 2)
**Goal**: Complete CC and Wheel visualizations

- [ ] Implement CC opportunities table and charts
- [ ] Implement Wheel opportunities table and charts
- [ ] Add section navigation/tabs
- [ ] Ensure consistent styling across sections

**Deliverable**: All three strategy sections working

### Phase 4: Enhanced Features (Week 3)
**Goal**: Add interactivity and polish

- [ ] Implement global filters
- [ ] Add table row expansion for details
- [ ] Create cross-strategy comparison chart
- [ ] Add enhanced probability factor visualization
- [ ] Implement copy-to-clipboard functionality
- [ ] Add tooltips and hover effects

**Deliverable**: Interactive dashboard with all features

### Phase 5: Export and Integration (Week 3-4)
**Goal**: Production-ready dashboard

- [ ] Implement standalone HTML export (inline all CSS/JS)
- [ ] Add CSV export for each strategy
- [ ] Create Excel multi-sheet export
- [ ] Integrate with existing scan scripts
- [ ] Add command-line flags: `--html`, `--no-html`
- [ ] Write comprehensive tests

**Deliverable**: Production-ready system

### Phase 6: Documentation and Polish (Week 4)
**Goal**: User-ready product

- [ ] Write user documentation
- [ ] Create example dashboards
- [ ] Add configuration guide
- [ ] Update README with dashboard features
- [ ] Performance optimization
- [ ] Cross-browser testing

**Deliverable**: Complete, documented feature

---

## Technical Implementation Details

### Code Architecture

#### Main Generator Class
```python
# src/visualization/html_generator.py

class HTMLDashboardGenerator:
    """Generate interactive HTML dashboard for options strategies"""

    def __init__(self, config=None):
        self.config = config or {}
        self.template_env = self._setup_jinja_env()

    def generate(
        self,
        csp_results: pd.DataFrame,
        cc_results: pd.DataFrame,
        wheel_results: pd.DataFrame,
        metadata: dict,
        output_path: str = None
    ) -> str:
        """
        Generate complete HTML dashboard

        Returns:
            Path to generated HTML file
        """
        # 1. Transform data for charts
        csp_chart_data = self._prepare_csp_charts(csp_results)
        cc_chart_data = self._prepare_cc_charts(cc_results)
        wheel_chart_data = self._prepare_wheel_charts(wheel_results)

        # 2. Calculate summary statistics
        summary = self._calculate_summary_stats(
            csp_results, cc_results, wheel_results
        )

        # 3. Render template
        html = self._render_dashboard(
            csp_data=csp_results.to_dict('records'),
            cc_data=cc_results.to_dict('records'),
            wheel_data=wheel_results.to_dict('records'),
            csp_charts=csp_chart_data,
            cc_charts=cc_chart_data,
            wheel_charts=wheel_chart_data,
            summary=summary,
            metadata=metadata
        )

        # 4. Save to file
        output_path = output_path or self._generate_filename()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_path
```

#### Integration with Scan Scripts
```python
# run_enhanced_csp_scan.py (updated)

from src.visualization.html_generator import HTMLDashboardGenerator

# ... existing code ...

if __name__ == "__main__":
    # Run analysis
    csp_results = csp_analyzer.get_top_opportunities(...)
    cc_results = cc_analyzer.get_top_opportunities(...)
    wheel_results = wheel_analyzer.get_top_opportunities(...)

    # Generate HTML dashboard
    generator = HTMLDashboardGenerator()
    html_path = generator.generate(
        csp_results=csp_results,
        cc_results=cc_results,
        wheel_results=wheel_results,
        metadata={
            'scan_timestamp': datetime.now(),
            'market_status': 'OPEN',
            'tickers': config.WATCHLIST[:5]
        }
    )

    print(f"\nDashboard generated: {html_path}")
    print(f"Open in browser: file://{os.path.abspath(html_path)}")
```

---

## Dependencies

### New Python Libraries Required
```
# requirements.txt additions
jinja2>=3.1.2          # Template engine
plotly>=5.17.0         # Interactive charts (alternative to Chart.js)
```

### JavaScript Libraries (Embedded)
- Chart.js v4.4.0 or Plotly.js v2.26.0
- DataTables.js v1.13.6
- Bootstrap v5.3.2 (CSS only)

---

## Risks and Mitigations

### Risk 1: Large HTML File Size
**Impact**: High (slow loading, hard to share)
**Probability**: Medium
**Mitigation**:
- Minify embedded CSS/JS
- Use SVG charts instead of canvas where possible
- Implement lazy loading for charts
- Provide option to use CDN instead of inline

### Risk 2: Browser Compatibility Issues
**Impact**: Medium (some users can't view)
**Probability**: Low
**Mitigation**:
- Test on all major browsers during development
- Use polyfills for older browsers
- Provide fallback plain HTML tables if JS fails

### Risk 3: Performance with Many Opportunities
**Impact**: Medium (slow rendering)
**Probability**: Medium
**Mitigation**:
- Implement pagination for large datasets (>100 opportunities)
- Lazy load charts (only render when section is visible)
- Optimize data transformation code

### Risk 4: Maintenance Overhead
**Impact**: Medium (harder to maintain)
**Probability**: Medium
**Mitigation**:
- Use templating system for easy updates
- Modular component design
- Comprehensive unit tests
- Clear documentation

---

## Future Enhancements (Out of Scope for R1)

### R2: Real-Time Updates
- WebSocket connection for live price updates
- Auto-refresh every N minutes
- Live market data integration

### R3: Historical Comparison
- Compare current scan to previous scans
- Trend charts showing how opportunities evolve
- Performance tracking of past recommendations

### R4: Advanced Analytics
- Monte Carlo simulation visualization
- Greeks surface plots (3D)
- Correlation heatmaps between tickers

### R5: Customization
- User-configurable dashboard layout
- Save custom filter presets
- Theme customization (colors, fonts)

### R6: Backtesting Visualization
- Visualize historical performance of strategies
- P&L charts
- Win/loss rate analysis

---

## Acceptance Criteria

### Must Have (Required for Release)
- ✅ All three strategies (CSP, CC, Wheel) visualized
- ✅ Interactive tables (sortable, filterable)
- ✅ At least 3 charts per strategy
- ✅ Enhanced probability analysis displayed
- ✅ Color-coded risk metrics
- ✅ Standalone HTML export works
- ✅ Mobile responsive design
- ✅ Dashboard generation < 2 seconds
- ✅ Works in Chrome, Firefox, Safari, Edge
- ✅ No data loss during transformation

### Should Have (Nice to Have)
- ✅ Cross-strategy comparison chart
- ✅ Copy trade details to clipboard
- ✅ CSV/Excel export per strategy
- ✅ Dark mode toggle
- ✅ Chart zoom/pan functionality

### Could Have (Future)
- Historical comparison
- Real-time updates
- Custom themes
- Backtesting visualization

---

## Sign-Off

**Product Owner**: [User]
**Technical Lead**: [Claude Code]
**Approved Date**: [Pending]

---

## Appendix

### A. Example Chart Data Structures

#### Risk/Reward Scatter Plot Data
```json
{
    "type": "scatter",
    "data": {
        "datasets": [{
            "label": "GOOGL",
            "data": [
                {"x": 48.0, "y": 71.1, "r": 8.20},
                {"x": 37.3, "y": 78.0, "r": 6.25}
            ],
            "backgroundColor": "rgba(255, 99, 132, 0.5)"
        }]
    },
    "options": {
        "scales": {
            "x": {"title": {"text": "Annual Return %"}},
            "y": {"title": {"text": "Probability OTM %"}}
        }
    }
}
```

### B. Color Coding Reference Table

| Metric | Excellent | Good | Fair | Poor |
|--------|-----------|------|------|------|
| Annual Return | >30% (Green) | 20-30% (Lime) | 15-20% (Yellow) | <15% (Red) |
| Prob OTM | >75% (Green) | 65-75% (Yellow) | 60-65% (Orange) | <60% (Red) |
| Downside Protection | >5% (Green) | 3-5% (Yellow) | 1-3% (Orange) | <1% (Red) |
| Composite Score | >80 (Green) | 70-80 (Blue) | 60-70 (Yellow) | <60 (Red) |

### C. Sample Configuration
```python
# In config.py
DASHBOARD_SETTINGS = {
    'auto_open_browser': True,
    'output_dir': 'output/dashboards',
    'theme': 'light',  # 'light' or 'dark'
    'max_opportunities_per_strategy': 20,
    'embed_libraries': True,  # False to use CDN
    'enable_filters': True,
    'enable_export': True,
    'chart_library': 'chartjs',  # 'chartjs' or 'plotly'
}
```

---

**End of PRD**
