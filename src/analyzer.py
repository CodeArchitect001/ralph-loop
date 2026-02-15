"""
流式分析引擎 - 计算日志统计指标
"""

from collections import defaultdict
from typing import Dict, List, Any


def calculate_percentile(values: List[float], percentile: float) -> float:
    """
    计算百分位数。

    Args:
        values: 数值列表
        percentile: 百分位数 (0-100)

    Returns:
        计算得到的百分位数值
    """
    if not values:
        return 0.0

    sorted_values = sorted(values)
    n = len(sorted_values)
    index = (percentile / 100) * (n - 1)
    lower = int(index)
    upper = lower + 1

    if upper >= n:
        return sorted_values[-1]

    weight = index - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


class LogAnalyzer:
    """
    日志分析器类，支持流式处理日志记录并计算统计指标。
    """

    def __init__(self):
        """初始化分析器。"""
        self.total_logs: int = 0
        self.error_count: int = 0
        self.service_latencies: Dict[str, List[int]] = defaultdict(list)

    def add_record(self, record: Dict[str, Any]) -> None:
        """
        添加一条日志记录进行分析。

        Args:
            record: 包含日志字段的字典
        """
        self.total_logs += 1

        # 统计错误数
        if record.get('level') == 'ERROR':
            self.error_count += 1

        # 收集各服务的延迟数据
        service = record.get('service')
        latency = record.get('latency_ms')
        if service is not None and latency is not None:
            self.service_latencies[service].append(latency)

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计结果。

        Returns:
            包含统计指标的字典:
            - total_logs: 日志总数
            - error_count: 错误数
            - error_rate: 错误率 (百分比)
            - services: 各服务的延迟统计
        """
        # 计算错误率
        error_rate = (self.error_count / self.total_logs * 100) if self.total_logs > 0 else 0.0

        # 计算各服务的延迟统计
        services_stats = {}
        for service, latencies in self.service_latencies.items():
            services_stats[service] = {
                'p50': calculate_percentile(latencies, 50),
                'p99': calculate_percentile(latencies, 99),
                'count': len(latencies)
            }

        return {
            'total_logs': self.total_logs,
            'error_count': self.error_count,
            'error_rate': round(error_rate, 2),
            'services': services_stats
        }
