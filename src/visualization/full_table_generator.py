"""
Full Interactive Table Generator
Generates an HTML page with an interactive DataTables table featuring
advanced filtering and sorting for all columns
"""
import os
import json
import pandas as pd
from datetime import datetime


class FullTableGenerator:
    """Generates interactive HTML table with DataTables for complete data export"""

    def __init__(self, output_dir='output/tables'):
        """
        Initialize the generator

        Args:
            output_dir: Directory to save HTML tables
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _generate_column_filters(self, df):
        """Generate column filter definitions for DataTables"""
        filter_configs = []

        for col in df.columns:
            dtype = df[col].dtype

            if pd.api.types.is_numeric_dtype(dtype):
                # Numeric columns get range filter
                filter_configs.append({
                    'name': col,
                    'type': 'range',
                    'min': float(df[col].min()) if not df[col].isna().all() else 0,
                    'max': float(df[col].max()) if not df[col].isna().all() else 0
                })
            else:
                # Text columns get search filter
                filter_configs.append({
                    'name': col,
                    'type': 'text'
                })

        return filter_configs

    def _format_dataframe_for_display(self, df):
        """Format DataFrame values for better display"""
        display_df = df.copy()

        # Format numeric columns appropriately
        for col in display_df.columns:
            if pd.api.types.is_numeric_dtype(display_df[col]):
                # Check if column name suggests it's a percentage
                if any(keyword in col.lower() for keyword in ['return', 'pct', 'percent', 'prob', 'delta', 'score', 'adjustment', 'discount', 'protection']):
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                # Check if column name suggests it's a price/premium
                elif any(keyword in col.lower() for keyword in ['price', 'premium', 'strike', 'cost', 'capital']):
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
                else:
                    # Other numeric columns
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")

        return display_df

    def generate(self, df, title="Full Data Table", metadata=None):
        """
        Generate interactive HTML table with all data

        Args:
            df: DataFrame with all data
            title: Title for the table
            metadata: Optional dict with scan metadata

        Returns:
            Path to generated HTML file
        """
        if df.empty:
            raise ValueError("DataFrame is empty, cannot generate table")

        # Format DataFrame
        display_df = self._format_dataframe_for_display(df)

        # Generate column filter configs
        filter_configs = self._generate_column_filters(df)

        # Convert DataFrame to HTML table
        table_html = display_df.to_html(
            index=False,
            classes='display compact',
            table_id='fullDataTable',
            escape=False,
            na_rep=''
        )

        # Build metadata section
        metadata_html = ""
        if metadata:
            metadata_html = "<div class='metadata'>"
            metadata_html += f"<h3>Scan Information</h3>"
            metadata_html += "<div class='metadata-grid'>"

            if 'scan_timestamp' in metadata:
                metadata_html += f"<div><strong>Timestamp:</strong> {metadata['scan_timestamp']}</div>"
            if 'market_status' in metadata:
                status_class = 'open' if metadata['market_status'] == 'OPEN' else 'closed'
                metadata_html += f"<div><strong>Market Status:</strong> <span class='status {status_class}'>{metadata['market_status']}</span></div>"
            if 'scan_type' in metadata:
                metadata_html += f"<div><strong>Scan Type:</strong> {metadata['scan_type']}</div>"
            if 'tickers' in metadata:
                tickers_str = ', '.join(metadata['tickers']) if isinstance(metadata['tickers'], list) else metadata['tickers']
                metadata_html += f"<div><strong>Tickers:</strong> {tickers_str}</div>"

            if 'criteria' in metadata:
                metadata_html += "<div class='criteria'><strong>Criteria:</strong><ul>"
                for key, value in metadata['criteria'].items():
                    metadata_html += f"<li>{key.replace('_', ' ').title()}: {value}</li>"
                metadata_html += "</ul></div>"

            metadata_html += "</div></div>"

        # Generate filter inputs HTML
        filter_html = "<div class='filters-container'>"
        filter_html += "<h3>Column Filters</h3>"
        filter_html += "<div class='filters-grid'>"

        for idx, config in enumerate(filter_configs):
            col_name = config['name']
            filter_html += f"<div class='filter-group'>"
            filter_html += f"<label>{col_name}</label>"

            if config['type'] == 'range':
                filter_html += f"<div class='range-filter'>"
                filter_html += f"<input type='number' id='filter-min-{idx}' placeholder='Min' step='any' class='filter-input'>"
                filter_html += f"<input type='number' id='filter-max-{idx}' placeholder='Max' step='any' class='filter-input'>"
                filter_html += f"</div>"
            else:
                filter_html += f"<input type='text' id='filter-text-{idx}' placeholder='Search...' class='filter-input'>"

            filter_html += "</div>"

        filter_html += "</div>"
        filter_html += "<button id='clearFilters' class='btn-clear'>Clear All Filters</button>"
        filter_html += "</div>"

        # Convert filter configs to JSON for JavaScript
        filter_configs_json = json.dumps(filter_configs)

        # Build complete HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>

    <!-- DataTables CSS -->
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.7/css/jquery.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css">
    <link rel="stylesheet" href="https://cdn.datatables.net/responsive/2.5.0/css/responsive.dataTables.min.css">

    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            padding: 20px;
        }}

        .container {{
            max-width: 100%;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}

        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 28px;
        }}

        .subtitle {{
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 14px;
        }}

        .metadata {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 4px;
        }}

        .metadata h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}

        .metadata-grid div {{
            font-size: 14px;
        }}

        .metadata-grid strong {{
            color: #34495e;
            margin-right: 8px;
        }}

        .status {{
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 12px;
        }}

        .status.open {{
            background: #d4edda;
            color: #155724;
        }}

        .status.closed {{
            background: #fff3cd;
            color: #856404;
        }}

        .criteria ul {{
            margin-top: 10px;
            margin-left: 20px;
        }}

        .criteria li {{
            margin: 5px 0;
            font-size: 13px;
        }}

        .filters-container {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 20px;
            margin-bottom: 30px;
        }}

        .filters-container h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .filters-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
        }}

        .filter-group label {{
            font-weight: 600;
            color: #495057;
            margin-bottom: 5px;
            font-size: 13px;
        }}

        .filter-input {{
            padding: 8px 12px;
            border: 1px solid #ced4da;
            border-radius: 4px;
            font-size: 14px;
            transition: border-color 0.2s;
        }}

        .filter-input:focus {{
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
        }}

        .range-filter {{
            display: flex;
            gap: 8px;
        }}

        .range-filter input {{
            flex: 1;
        }}

        .btn-clear {{
            background: #e74c3c;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: background 0.2s;
        }}

        .btn-clear:hover {{
            background: #c0392b;
        }}

        .table-container {{
            overflow-x: auto;
            margin-top: 20px;
        }}

        #fullDataTable {{
            width: 100% !important;
            font-size: 13px;
        }}

        #fullDataTable thead th {{
            background: #34495e;
            color: white;
            font-weight: 600;
            padding: 12px 8px;
            text-align: left;
            white-space: nowrap;
        }}

        #fullDataTable tbody td {{
            padding: 10px 8px;
            border-bottom: 1px solid #dee2e6;
        }}

        #fullDataTable tbody tr:hover {{
            background: #f8f9fa;
        }}

        .dataTables_wrapper .dataTables_info,
        .dataTables_wrapper .dataTables_paginate {{
            margin-top: 20px;
        }}

        .dataTables_wrapper .dataTables_length,
        .dataTables_wrapper .dataTables_filter {{
            margin-bottom: 15px;
        }}

        .dt-buttons {{
            margin-bottom: 15px;
        }}

        .dt-button {{
            background: #3498db !important;
            color: white !important;
            border: none !important;
            padding: 8px 16px !important;
            border-radius: 4px !important;
            margin-right: 8px !important;
            cursor: pointer !important;
            font-size: 13px !important;
        }}

        .dt-button:hover {{
            background: #2980b9 !important;
        }}

        .info-box {{
            background: #e8f4f8;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }}

        .info-box p {{
            margin: 5px 0;
            font-size: 14px;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}

            .filters-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p class="subtitle">Interactive table with advanced filtering and sorting capabilities</p>

        <div class="info-box">
            <p><strong>How to use:</strong></p>
            <p>• Use the column filters below to narrow down results (supports partial text match, greater than, less than)</p>
            <p>• Click on any column header to sort</p>
            <p>• Use the search box to search across all columns</p>
            <p>• Export data using the buttons above the table</p>
        </div>

        {metadata_html}

        {filter_html}

        <div class="table-container">
            {table_html}
        </div>
    </div>

    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>

    <!-- DataTables JS -->
    <script src="https://cdn.datatables.net/1.13.7/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.print.min.js"></script>
    <script src="https://cdn.datatables.net/responsive/2.5.0/js/dataTables.responsive.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/pdfmake.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/vfs_fonts.js"></script>

    <script>
        $(document).ready(function() {{
            // Initialize DataTable
            var table = $('#fullDataTable').DataTable({{
                pageLength: 25,
                lengthMenu: [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
                responsive: true,
                dom: 'Blfrtip',
                buttons: [
                    {{
                        extend: 'copy',
                        text: 'Copy to Clipboard'
                    }},
                    {{
                        extend: 'csv',
                        text: 'Export CSV'
                    }},
                    {{
                        extend: 'excel',
                        text: 'Export Excel'
                    }},
                    {{
                        extend: 'pdf',
                        text: 'Export PDF',
                        orientation: 'landscape',
                        pageSize: 'LEGAL'
                    }},
                    {{
                        extend: 'print',
                        text: 'Print'
                    }}
                ],
                order: [[0, 'asc']],
                stateSave: true,
                columnDefs: [
                    {{ targets: '_all', className: 'dt-body-left' }}
                ]
            }});

            // Custom filtering function
            $.fn.dataTable.ext.search.push(
                function(settings, data, dataIndex) {{
                    var filterConfigs = {filter_configs_json};

                    for (var i = 0; i < filterConfigs.length; i++) {{
                        var config = filterConfigs[i];
                        var colValue = data[i];

                        if (config.type === 'range') {{
                            var minInput = $('#filter-min-' + i).val();
                            var maxInput = $('#filter-max-' + i).val();

                            if (minInput !== '' || maxInput !== '') {{
                                var numValue = parseFloat(colValue);

                                if (isNaN(numValue)) {{
                                    return false;
                                }}

                                if (minInput !== '' && numValue < parseFloat(minInput)) {{
                                    return false;
                                }}

                                if (maxInput !== '' && numValue > parseFloat(maxInput)) {{
                                    return false;
                                }}
                            }}
                        }} else {{
                            var searchInput = $('#filter-text-' + i).val().toLowerCase();

                            if (searchInput !== '') {{
                                if (!colValue.toLowerCase().includes(searchInput)) {{
                                    return false;
                                }}
                            }}
                        }}
                    }}

                    return true;
                }}
            );

            // Attach filter listeners
            var filterConfigs = {filter_configs_json};

            for (var i = 0; i < filterConfigs.length; i++) {{
                if (filterConfigs[i].type === 'range') {{
                    $('#filter-min-' + i + ', #filter-max-' + i).on('keyup change', function() {{
                        table.draw();
                    }});
                }} else {{
                    $('#filter-text-' + i).on('keyup', function() {{
                        table.draw();
                    }});
                }}
            }}

            // Clear filters button
            $('#clearFilters').on('click', function() {{
                $('input.filter-input').val('');
                table.search('').draw();
            }});
        }});
    </script>
</body>
</html>
"""

        # Save HTML file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'full_table_{timestamp}.html'
        output_path = os.path.join(self.output_dir, filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        return output_path
