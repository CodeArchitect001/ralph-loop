"""
HTML 报告生成器 - 生成监控面板风格的 HTML 报告
"""

from typing import Dict, Any


def get_error_rate_color(error_rate: float) -> str:
    """
    根据错误率返回对应的颜色。

    Args:
        error_rate: 错误率百分比

    Returns:
        颜色的十六进制值
    """
    if error_rate < 1:
        return '#28a745'  # 绿色
    elif error_rate < 5:
        return '#ffc107'  # 黄色
    else:
        return '#dc3545'  # 红色


def generate_report(stats: Dict[str, Any], output_path: str = 'report.html') -> None:
    """
    生成 HTML 监控报告。

    Args:
        stats: 统计数据字典，包含 total_logs, error_count, error_rate, services
        output_path: 输出 HTML 文件路径，默认 report.html
    """
    total_logs = stats.get('total_logs', 0)
    error_count = stats.get('error_count', 0)
    error_rate = stats.get('error_rate', 0.0)
    services = stats.get('services', {})

    # 计算全局 P99（所有服务的最大 P99）
    global_p99 = 0.0
    if services:
        global_p99 = max(
            svc.get('p99', 0) for svc in services.values()
        )

    error_rate_color = get_error_rate_color(error_rate)

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
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }}
        .card:hover {{
            transform: translateY(-5px);
        }}
        .card-title {{
            font-size: 1.1em;
            color: #aaa;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .card-value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        .card-error-rate .card-value {{
            color: {error_rate_color};
        }}
        .services-section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 25px;
            margin-top: 20px;
        }}
        .services-section h2 {{
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.2);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        th {{
            background: rgba(255, 255, 255, 0.1);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 0.9em;
        }}
        tr:hover {{
            background: rgba(255, 255, 255, 0.05);
        }}
        .latency-high {{
            color: #dc3545;
        }}
        .latency-medium {{
            color: #ffc107;
        }}
        .latency-normal {{
            color: #28a745;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Log Stream Analyzer</h1>

        <div class="summary-cards">
            <div class="card">
                <div class="card-title">日志总数</div>
                <div class="card-value">{total_logs:,}</div>
            </div>
            <div class="card card-error-rate">
                <div class="card-title">错误率</div>
                <div class="card-value">{error_rate:.2f}%</div>
            </div>
            <div class="card">
                <div class="card-title">错误数</div>
                <div class="card-value">{error_count:,}</div>
            </div>
            <div class="card">
                <div class="card-title">全局 P99 延迟</div>
                <div class="card-value">{global_p99:.0f}ms</div>
            </div>
        </div>

        <div class="services-section">
            <h2>服务详情</h2>
            <table>
                <thead>
                    <tr>
                        <th>服务名称</th>
                        <th>请求数</th>
                        <th>P50 延迟</th>
                        <th>P99 延迟</th>
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
</html>'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def _generate_service_rows(services: Dict[str, Dict[str, Any]]) -> str:
    """
    生成服务表格的 HTML 行。

    Args:
        services: 服务统计数据字典

    Returns:
        HTML 表格行字符串
    """
    rows = []
    for service_name, data in sorted(services.items()):
        p50 = data.get('p50', 0)
        p99 = data.get('p99', 0)
        count = data.get('count', 0)

        # 根据延迟设置颜色类
        p99_class = _get_latency_class(p99)

        row = f'''                    <tr>
                        <td><strong>{service_name}</strong></td>
                        <td>{count:,}</td>
                        <td>{p50:.0f}ms</td>
                        <td class="{p99_class}">{p99:.0f}ms</td>
                    </tr>'''
        rows.append(row)

    return '\n'.join(rows)


def _get_latency_class(latency: float) -> str:
    """
    根据延迟值返回对应的 CSS 类名。

    Args:
        latency: 延迟值（毫秒）

    Returns:
        CSS 类名
    """
    if latency >= 2000:
        return 'latency-high'
    elif latency >= 500:
        return 'latency-medium'
    else:
        return 'latency-normal'
