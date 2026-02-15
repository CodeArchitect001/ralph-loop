"""
HTML 报告生成器模块

生成包含统计信息的 HTML 监控面板。
"""

from datetime import datetime
from typing import Dict, Any


def _get_error_rate_color(error_rate: float) -> str:
    """
    根据错误率返回对应的颜色。

    Args:
        error_rate: 错误率百分比

    Returns:
        CSS 颜色值
    """
    if error_rate < 1:
        return '#28a745'  # 绿色
    if error_rate <= 5:
        return '#ffc107'  # 黄色
    return '#dc3545'  # 红色


def _format_latency(value: float) -> str:
    """
    格式化延迟值。

    Args:
        value: 延迟毫秒数

    Returns:
        格式化后的字符串
    """
    return f'{value:.2f} ms'


def generate_report(stats: Dict[str, Any], output_path: str = 'report.html') -> None:
    """
    生成 HTML 报告文件。

    Args:
        stats: 统计数据字典，包含 total_logs, error_count, error_rate, services 等字段
        output_path: 输出 HTML 文件路径，默认为 report.html
    """
    # 提取统计数据
    total_logs = stats.get('total_logs', 0)
    error_rate = stats.get('error_rate', 0.0)
    services = stats.get('services', {})

    # 计算全局 P99（所有服务中的最大 P99）
    global_p99 = 0.0
    if services:
        global_p99 = max(
            svc.get('p99', 0) for svc in services.values()
        )

    # 获取错误率颜色
    error_rate_color = _get_error_rate_color(error_rate)

    # 生成服务表格行
    service_rows = ''
    for service_name, service_stats in sorted(services.items()):
        service_rows += f'''
            <tr>
                <td>{service_name}</td>
                <td>{service_stats.get('count', 0)}</td>
                <td>{_format_latency(service_stats.get('p50', 0))}</td>
                <td>{_format_latency(service_stats.get('p99', 0))}</td>
                <td>{_format_latency(service_stats.get('min', 0))}</td>
                <td>{_format_latency(service_stats.get('max', 0))}</td>
            </tr>'''

    # 生成完整 HTML
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Stream Analyzer - 监控报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        .header .timestamp {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card .label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}
        .card.error-rate .value {{
            color: {error_rate_color};
        }}
        .card.p99 .value {{
            color: #17a2b8;
        }}
        .table-container {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        .table-container h2 {{
            margin-bottom: 20px;
            color: #333;
            font-size: 1.5em;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        td {{
            color: #333;
        }}
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Log Stream Analyzer</h1>
            <p class="timestamp">报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="summary-cards">
            <div class="card">
                <div class="label">日志总数</div>
                <div class="value">{total_logs:,}</div>
            </div>
            <div class="card error-rate">
                <div class="label">错误率</div>
                <div class="value">{error_rate:.2f}%</div>
            </div>
            <div class="card p99">
                <div class="label">全局 P99 延迟</div>
                <div class="value">{_format_latency(global_p99)}</div>
            </div>
        </div>

        <div class="table-container">
            <h2>各服务延迟详情</h2>
            {'<table><thead><tr><th>服务名称</th><th>日志数</th><th>P50 延迟</th><th>P99 延迟</th><th>最小延迟</th><th>最大延迟</th></tr></thead><tbody>' + service_rows + '</tbody></table>' if services else '<div class="no-data">暂无服务数据</div>'}
        </div>
    </div>
</body>
</html>'''

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
