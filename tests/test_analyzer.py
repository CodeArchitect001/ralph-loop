"""Tests for streaming analysis engine."""

import os
import sys
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.analyzer import LogAnalyzer


class TestLogAnalyzer:
    """Tests for LogAnalyzer class."""

    def test_empty_analyzer(self):
        """Test analyzer with no records."""
        analyzer = LogAnalyzer()
        stats = analyzer.get_stats()

        assert stats['total_logs'] == 0
        assert stats['error_count'] == 0
        assert stats['error_rate'] == 0.0
        assert stats['services'] == {}

    def test_add_single_record(self):
        """Test adding a single record."""
        analyzer = LogAnalyzer()
        record = {
            'timestamp': '2025-01-15T10:23:45',
            'level': 'INFO',
            'service': 'auth',
            'latency_ms': 50,
            'msg': 'test'
        }

        analyzer.add_record(record)
        stats = analyzer.get_stats()

        assert stats['total_logs'] == 1
        assert stats['error_count'] == 0
        assert stats['error_rate'] == 0.0
        assert 'auth' in stats['services']

    def test_error_counting(self):
        """Test error count and rate calculation."""
        analyzer = LogAnalyzer()

        # Add 3 INFO and 1 ERROR
        for i in range(3):
            analyzer.add_record({
                'timestamp': f'2025-01-15T10:23:4{i}',
                'level': 'INFO',
                'service': 'auth',
                'latency_ms': 10,
                'msg': 'info'
            })

        analyzer.add_record({
            'timestamp': '2025-01-15T10:23:50',
            'level': 'ERROR',
            'service': 'auth',
            'latency_ms': 100,
            'msg': 'error'
        })

        stats = analyzer.get_stats()

        assert stats['total_logs'] == 4
        assert stats['error_count'] == 1
        assert stats['error_rate'] == 25.0

    def test_service_latency_tracking(self):
        """Test latency tracking per service."""
        analyzer = LogAnalyzer()

        # Add records for multiple services
        analyzer.add_record({
            'timestamp': '2025-01-15T10:23:45',
            'level': 'INFO',
            'service': 'auth',
            'latency_ms': 100,
            'msg': 'test'
        })
        analyzer.add_record({
            'timestamp': '2025-01-15T10:23:46',
            'level': 'INFO',
            'service': 'auth',
            'latency_ms': 200,
            'msg': 'test'
        })
        analyzer.add_record({
            'timestamp': '2025-01-15T10:23:47',
            'level': 'INFO',
            'service': 'payment',
            'latency_ms': 500,
            'msg': 'test'
        })

        stats = analyzer.get_stats()

        assert 'auth' in stats['services']
        assert 'payment' in stats['services']
        assert stats['services']['auth']['count'] == 2
        assert stats['services']['payment']['count'] == 1

    def test_percentile_calculation(self):
        """Test P50 and P99 latency calculation."""
        analyzer = LogAnalyzer()

        # Add 100 records with latencies 1-100
        for i in range(1, 101):
            analyzer.add_record({
                'timestamp': f'2025-01-15T10:23:{i:02d}',
                'level': 'INFO',
                'service': 'test',
                'latency_ms': i,
                'msg': 'test'
            })

        stats = analyzer.get_stats()

        # P50 should be around 50
        assert 49 <= stats['services']['test']['p50'] <= 51
        # P99 should be around 99
        assert 98 <= stats['services']['test']['p99'] <= 100

    def test_full_integration(self):
        """Test with actual test data."""
        from src.parser import parse_file

        filepath = os.path.join(os.path.dirname(__file__), 'data', 'raw_logs.jsonl')
        records = parse_file(filepath)

        analyzer = LogAnalyzer()
        for record in records:
            analyzer.add_record(record)

        stats = analyzer.get_stats()

        # Verify we processed all valid records (19 valid out of 21 lines)
        assert stats['total_logs'] == 19

        # Verify we have multiple services
        assert len(stats['services']) >= 4

        # Verify error rate is calculated
        assert stats['error_rate'] > 0
