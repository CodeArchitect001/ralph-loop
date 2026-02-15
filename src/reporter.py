"""HTML report generator for log stream analyzer."""

from typing import Dict


def _get_error_rate_color(error_rate: float) -> str:
    """
    Get color based on error rate.

    Args:
        error_rate: Error percentage (0-100)

    Returns:
        CSS color string
    """
    if error_rate < 1:
        return '#28a745'  # Green
    elif error_rate <= 5:
        return '#ffc107'  # Yellow
    else:
        return '#dc3545'  # Red


def _get_max_p99(services: Dict) -> int:
    """Get the maximum P99 latency across all services."""
    if not services:
        return 0
    return max(s.get('p99', 0) for s in services.values())


def generate_report(stats: Dict, output_path: str = "report.html") -> None:
    """
    Generate an HTML report from statistics.

    Args:
        stats: Dictionary containing analysis results
        output_path: Path to write the HTML file (default: report.html)
    """
    total_logs = stats.get('total_logs', 0)
    error_count = stats.get('error_count', 0)
    error_rate = stats.get('error_rate', 0)
    services = stats.get('services', {})

    error_rate_color = _get_error_rate_color(error_rate)
    max_p99 = _get_max_p99(services)

    # Build services table rows
    service_rows = ""
    for service_name, service_data in sorted(services.items()):
        service_rows += f"""
        <tr>
            <td style="padding: 12px; border-bottom: 1px solid #ddd;">{service_name}</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{service_data.get('count', 0)}</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{service_data.get('p50', 0)} ms</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{service_data.get('p99', 0)} ms</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{service_data.get('min', 0)} ms</td>
            <td style="padding: 12px; border-bottom: 1px solid #ddd; text-align: center;">{service_data.get('max', 0)} ms</td>
        </tr>"""

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Stream Analyzer Report</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 1200px; margin: 0 auto;">
        <h1 style="color: #333; margin-bottom: 30px;">Log Stream Analyzer Report</h1>

        <!-- Summary Cards -->
        <div style="display: flex; gap: 20px; margin-bottom: 30px; flex-wrap: wrap;">
            <!-- Total Logs Card -->
            <div style="background: white; border-radius: 8px; padding: 20px; flex: 1; min-width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #666; font-size: 14px; margin-bottom: 8px;">Total Logs</div>
                <div style="font-size: 32px; font-weight: bold; color: #333;">{total_logs:,}</div>
            </div>

            <!-- Error Rate Card -->
            <div style="background: white; border-radius: 8px; padding: 20px; flex: 1; min-width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #666; font-size: 14px; margin-bottom: 8px;">Error Rate</div>
                <div style="font-size: 32px; font-weight: bold; color: {error_rate_color};">{error_rate:.2f}%</div>
                <div style="color: #888; font-size: 12px; margin-top: 4px;">{error_count} errors</div>
            </div>

            <!-- Max P99 Latency Card -->
            <div style="background: white; border-radius: 8px; padding: 20px; flex: 1; min-width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #666; font-size: 14px; margin-bottom: 8px;">Max P99 Latency</div>
                <div style="font-size: 32px; font-weight: bold; color: #333;">{max_p99} ms</div>
            </div>

            <!-- Services Count Card -->
            <div style="background: white; border-radius: 8px; padding: 20px; flex: 1; min-width: 200px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <div style="color: #666; font-size: 14px; margin-bottom: 8px;">Services</div>
                <div style="font-size: 32px; font-weight: bold; color: #333;">{len(services)}</div>
            </div>
        </div>

        <!-- Services Table -->
        <div style="background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <h2 style="color: #333; margin-top: 0;">Service Details</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">Service</th>
                        <th style="padding: 12px; text-align: center; border-bottom: 2px solid #ddd;">Count</th>
                        <th style="padding: 12px; text-align: center; border-bottom: 2px solid #ddd;">P50 Latency</th>
                        <th style="padding: 12px; text-align: center; border-bottom: 2px solid #ddd;">P99 Latency</th>
                        <th style="padding: 12px; text-align: center; border-bottom: 2px solid #ddd;">Min</th>
                        <th style="padding: 12px; text-align: center; border-bottom: 2px solid #ddd;">Max</th>
                    </tr>
                </thead>
                <tbody>
                    {service_rows}
                </tbody>
            </table>
        </div>

        <!-- Footer -->
        <div style="margin-top: 30px; color: #888; font-size: 12px; text-align: center;">
            Generated by Log Stream Analyzer
        </div>
    </div>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
