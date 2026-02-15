"""
Tests for Log Analyzer Module
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.analyzer import LogAnalyzer


class TestLogAnalyzer:
    """Tests for LogAnalyzer class"""

    def test_empty_analyzer(self):
        """Should handle empty input without errors"""
        analyzer = LogAnalyzer()
        stats = analyzer.get_stats()

        assert stats['total_logs'] == 0
        assert stats['error_count'] == 0
        assert stats['error_rate'] == 0.0
        assert stats['services'] == {}

    def test_single_record(self):
        """Should process a single record correctly"""
        analyzer = LogAnalyzer()
        record = {
            'timestamp': '2025-01-15T10:23:45',
            'level': 'ERROR',
            'service': 'payment',
            'latency_ms': 100,
            'msg': 'test'
        }

        analyzer.add_record(record)
        stats = analyzer.get_stats()

        assert stats['total_logs'] == 1
        assert stats['error_count'] == 1
        assert stats['error_rate'] == 100.0
        assert 'payment' in stats['services']
        assert stats['services']['payment']['p50'] == 100.0
        assert stats['services']['payment']['p99'] == 100.0

    def test_multiple_records(self):
        """Should process multiple records and calculate statistics"""
        analyzer = LogAnalyzer()

        records = [
            {'level': 'INFO', 'service': 'auth', 'latency_ms': 10, 'msg': 'test'},
            {'level': 'ERROR', 'service': 'auth', 'latency_ms': 20, 'msg': 'test'},
            {'level': 'INFO', 'service': 'payment', 'latency_ms': 100, 'msg': 'test'},
            {'level': 'INFO', 'service': 'auth', 'latency_ms': 30, 'msg': 'test'},
            {'level': 'WARN', 'service': 'payment', 'latency_ms': 200, 'msg': 'test'},
        ]

        for record in records:
            analyzer.add_record(record)

        stats = analyzer.get_stats()

        assert stats['total_logs'] == 5
        assert stats['error_count'] == 1
        assert stats['error_rate'] == 20.0
        assert 'auth' in stats['services']
        assert 'payment' in stats['services']

    def test_percentile_calculation(self):
        """Should correctly calculate p50 and p99 percentiles"""
        analyzer = LogAnalyzer()

        # Add 100 records with latencies 1-100
        for i in range(1, 101):
            record = {
                'level': 'INFO',
                'service': 'test',
                'latency_ms': i,
                'msg': 'test'
            }
            analyzer.add_record(record)

        stats = analyzer.get_stats()

        # p50 should be around 50.5 (interpolated)
        assert 49 <= stats['services']['test']['p50'] <= 52

        # p99 should be around 99.01 (interpolated)
        assert 98 <= stats['services']['test']['p99'] <= 100

    def test_error_rate_calculation(self):
        """Should calculate error rate correctly"""
        analyzer = LogAnalyzer()

        # 3 errors out of 10 records = 30%
        for i in range(10):
            record = {
                'level': 'ERROR' if i < 3 else 'INFO',
                'service': 'test',
                'latency_ms': 100,
                'msg': 'test'
            }
            analyzer.add_record(record)

        stats = analyzer.get_stats()

        assert stats['error_count'] == 3
        assert stats['error_rate'] == 30.0

    def test_multiple_services(self):
        """Should track statistics for multiple services independently"""
        analyzer = LogAnalyzer()

        records = [
            {'level': 'ERROR', 'service': 'payment', 'latency_ms': 1000, 'msg': 'test'},
            {'level': 'ERROR', 'service': 'payment', 'latency_ms': 2000, 'msg': 'test'},
            {'level': 'INFO', 'service': 'auth', 'latency_ms': 10, 'msg': 'test'},
            {'level': 'INFO', 'service': 'auth', 'latency_ms': 20, 'msg': 'test'},
            {'level': 'INFO', 'service': 'db', 'latency_ms': 500, 'msg': 'test'},
        ]

        for record in records:
            analyzer.add_record(record)

        stats = analyzer.get_stats()

        # Check all services are tracked
        assert len(stats['services']) == 3
        assert 'payment' in stats['services']
        assert 'auth' in stats['services']
        assert 'db' in stats['services']

        # Check service counts
        assert stats['services']['payment']['count'] == 2
        assert stats['services']['auth']['count'] == 2
        assert stats['services']['db']['count'] == 1


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
