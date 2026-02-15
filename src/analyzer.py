"""
流式分析引擎模块

计算统计指标：错误率、各服务 P99 延迟、日志总数。
"""

import heapq
from collections import defaultdict
from typing import Dict, List, Any


def percentile(data: List[float], p: float) -> float:
    """
    计算百分位数。

    Args:
        data: 已排序的数据列表
        p: 百分位数（0-100）

    Returns:
        对应百分位的值
    """
    if not data:
        return 0.0

    sorted_data = sorted(data)
    n = len(sorted_data)

    # 计算索引位置
    index = (p / 100) * (n - 1)
    lower = int(index)
    upper = lower + 1

    if upper >= n:
        return sorted_data[-1]

    # 线性插值
    weight = index - lower
    return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight


class LogAnalyzer:
    """
    流式日志分析器。

    支持 add_record() 逐条处理和 get_stats() 获取统计结果。
    """

    def __init__(self):
        """初始化分析器。"""
        self._total_logs: int = 0
        self._error_count: int = 0
        self._service_latencies: Dict[str, List[float]] = defaultdict(list)

    def add_record(self, record: Dict[str, Any]) -> None:
        """
        添加一条日志记录进行分析。

        Args:
            record: 包含日志字段的字典，需包含 level, service, latency_ms 字段
        """
        self._total_logs += 1

        # 统计错误数（ERROR 级别）
        if record.get('level') == 'ERROR':
            self._error_count += 1

        # 按服务收集延迟数据
        service = record.get('service', 'unknown')
        latency = record.get('latency_ms', 0)
        self._service_latencies[service].append(float(latency))

    def get_stats(self) -> Dict[str, Any]:
        """
        获取统计结果。

        Returns:
            包含统计指标的字典：
            - total_logs: 日志总数
            - error_count: 错误数
            - error_rate: 错误率（百分比）
            - services: 各服务的延迟统计
        """
        # 计算错误率
        error_rate = 0.0
        if self._total_logs > 0:
            error_rate = (self._error_count / self._total_logs) * 100

        # 计算各服务的延迟统计
        services_stats = {}
        for service, latencies in self._service_latencies.items():
            if latencies:
                services_stats[service] = {
                    'count': len(latencies),
                    'p50': percentile(latencies, 50),
                    'p99': percentile(latencies, 99),
                    'min': min(latencies),
                    'max': max(latencies)
                }

        return {
            'total_logs': self._total_logs,
            'error_count': self._error_count,
            'error_rate': round(error_rate, 2),
            'services': services_stats
        }
