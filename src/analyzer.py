"""Streaming analysis engine for log stream analyzer."""

from collections import defaultdict
from typing import Dict, List


class LogAnalyzer:
    """Streaming log analyzer that computes statistics incrementally."""

    def __init__(self):
        """Initialize the analyzer with empty state."""
        self.total_logs = 0
        self.error_count = 0
        self.service_latencies: Dict[str, List[int]] = defaultdict(list)

    def add_record(self, record: Dict) -> None:
        """
        Add a single log record to the analysis.

        Args:
            record: A dictionary containing log data with keys:
                    timestamp, level, service, latency_ms, msg
        """
        self.total_logs += 1

        # Count errors
        if record.get('level') == 'ERROR':
            self.error_count += 1

        # Track latencies per service
        service = record.get('service')
        latency = record.get('latency_ms')
        if service and latency is not None:
            self.service_latencies[service].append(latency)

    def get_stats(self) -> Dict:
        """
        Get computed statistics from analyzed logs.

        Returns:
            Dictionary containing:
            - total_logs: Total number of logs processed
            - error_count: Number of error logs
            - error_rate: Error percentage (0-100)
            - services: Dict of service stats with p50/p99 latencies
        """
        error_rate = 0.0
        if self.total_logs > 0:
            error_rate = (self.error_count / self.total_logs) * 100

        services_stats = {}
        for service, latencies in self.service_latencies.items():
            if latencies:
                services_stats[service] = {
                    'count': len(latencies),
                    'p50': self._percentile(latencies, 50),
                    'p99': self._percentile(latencies, 99),
                    'min': min(latencies),
                    'max': max(latencies)
                }

        return {
            'total_logs': self.total_logs,
            'error_count': self.error_count,
            'error_rate': round(error_rate, 2),
            'services': services_stats
        }

    def _percentile(self, data: List[int], percentile: int) -> int:
        """
        Calculate the percentile value using heapq.

        Args:
            data: List of numeric values
            percentile: Percentile to calculate (0-100)

        Returns:
            The percentile value
        """
        if not data:
            return 0

        # Use nsmallest for efficient calculation
        sorted_data = sorted(data)
        n = len(sorted_data)
        index = (percentile / 100) * (n - 1)

        lower = int(index)
        upper = lower + 1

        if upper >= n:
            return sorted_data[-1]

        # Linear interpolation
        weight = index - lower
        return int(sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight)
