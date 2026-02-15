"""
Log Analyzer Module
Streaming analysis engine for computing log statistics.
"""

import heapq
from collections import defaultdict
from typing import Dict, List


class LogAnalyzer:
    """
    Streaming log analyzer that computes statistics incrementally.
    """

    def __init__(self):
        """Initialize the analyzer with empty state."""
        self.total_logs = 0
        self.error_count = 0
        self.service_latencies = defaultdict(list)

    def add_record(self, record: Dict) -> None:
        """
        Add a single log record to the analyzer.

        Args:
            record: Dict containing timestamp, level, service, latency_ms, msg
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
        Get computed statistics.

        Returns:
            Dict containing:
                - total_logs: int
                - error_count: int
                - error_rate: float (percentage)
                - services: Dict of service name to {p50, p99}
        """
        # Calculate error rate
        error_rate = (self.error_count / self.total_logs * 100) if self.total_logs > 0 else 0.0

        # Calculate percentiles for each service
        services = {}
        for service_name, latencies in self.service_latencies.items():
            if latencies:
                services[service_name] = {
                    'p50': self._percentile(latencies, 50),
                    'p99': self._percentile(latencies, 99),
                    'count': len(latencies)
                }

        return {
            'total_logs': self.total_logs,
            'error_count': self.error_count,
            'error_rate': round(error_rate, 2),
            'services': services
        }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """
        Calculate the given percentile of a list.

        Args:
            data: List of numeric values
            percentile: Percentile to calculate (0-100)

        Returns:
            The percentile value
        """
        if not data:
            return 0.0

        # Sort the data
        sorted_data = sorted(data)
        n = len(sorted_data)

        # Calculate index
        index = (percentile / 100) * (n - 1)

        # Interpolate if necessary
        lower = int(index)
        upper = lower + 1

        if upper >= n:
            return sorted_data[-1]

        # Linear interpolation
        weight = index - lower
        return sorted_data[lower] * (1 - weight) + sorted_data[upper] * weight
