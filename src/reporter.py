"""
HTML Report Generator Module
Generates visual monitoring dashboard in HTML format.
"""

from typing import Dict


def generate_report(stats: Dict, output_path: str = 'report.html') -> None:
    """
    Generate an HTML report from log statistics.

    Args:
        stats: Dict containing analysis results with keys:
            - total_logs: int
            - error_count: int
            - error_rate: float
            - services: Dict of service name to {p50, p99, count}
        output_path: Path to output HTML file (default: report.html)
    """
    html_content = _generate_html(stats)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except IOError as e:
        print(f"Error writing report to {output_path}: {str(e)}")
        raise


def _generate_html(stats: Dict) -> str:
    """
    Generate the complete HTML content.

    Args:
        stats: Statistics dictionary

    Returns:
        Complete HTML string
    """
    total_logs = stats.get('total_logs', 0)
    error_rate = stats.get('error_rate', 0.0)
    services = stats.get('services', {})

    # Determine error rate color
    error_rate_color = _get_error_rate_color(error_rate)

    # Calculate overall P99 (max across all services)
    overall_p99 = max(
        s.get('p99', 0) for s in services.values()
    ) if services else 0.0

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Stream Analyzer - Monitoring Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1 {{
            color: white;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}

        .stat-value.error-rate {{
            color: {error_rate_color};
        }}

        .services-section {{
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}

        th {{
            background-color: #667eea;
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}

        tr:hover {{
            background-color: #f5f5f5;
        }}

        td {{
            color: #555;
        }}

        .latency-high {{
            color: #f44336;
            font-weight: bold;
        }}

        .latency-medium {{
            color: #ff9800;
        }}

        .latency-low {{
            color: #4caf50;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Log Stream Analyzer</h1>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Logs</div>
                <div class="stat-value">{total_logs:,}</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Error Rate</div>
                <div class="stat-value error-rate">{error_rate:.2f}%</div>
            </div>

            <div class="stat-card">
                <div class="stat-label">Overall P99 Latency</div>
                <div class="stat-value">{overall_p99:.2f}ms</div>
            </div>
        </div>

        <div class="services-section">
            <h2>Services Performance</h2>
            <table>
                <thead>
                    <tr>
                        <th>Service Name</th>
                        <th>Request Count</th>
                        <th>P50 Latency (ms)</th>
                        <th>P99 Latency (ms)</th>
                    </tr>
                </thead>
                <tbody>
                    {_generate_service_rows(services)}
                </tbody>
            </table>
        </div>

        <div class="footer">
            Generated by Log Stream Analyzer
        </div>
    </div>
</body>
</html>"""

    return html


def _get_error_rate_color(error_rate: float) -> str:
    """
    Determine color based on error rate.

    Args:
        error_rate: Error rate percentage

    Returns:
        CSS color string
    """
    if error_rate < 1.0:
        return '#4caf50'  # Green
    if error_rate < 5.0:
        return '#ff9800'  # Yellow/Orange
    return '#f44336'  # Red


def _generate_service_rows(services: Dict) -> str:
    """
    Generate HTML table rows for services.

    Args:
        services: Dict of service statistics

    Returns:
        HTML string of table rows
    """
    rows = []

    for service_name, stats in sorted(services.items()):
        p50 = stats.get('p50', 0)
        p99 = stats.get('p99', 0)
        count = stats.get('count', 0)

        # Add color coding for P99 latency
        if p99 > 2000:
            p99_class = 'latency-high'
        elif p99 > 500:
            p99_class = 'latency-medium'
        else:
            p99_class = 'latency-low'

        rows.append(f"""
                    <tr>
                        <td><strong>{service_name}</strong></td>
                        <td>{count:,}</td>
                        <td>{p50:.2f}</td>
                        <td class="{p99_class}">{p99:.2f}</td>
                    </tr>""")

    return '\n'.join(rows)
