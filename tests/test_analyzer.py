"""
测试流式分析引擎模块
"""

import pytest
from src.analyzer import LogAnalyzer, calculate_percentile


class TestCalculatePercentile:
    """测试百分位数计算"""

    def test_percentile_empty_list(self):
        """测试空列表返回 0"""
        assert calculate_percentile([], 50) == 0.0

    def test_percentile_single_value(self):
        """测试单个值返回该值"""
        assert calculate_percentile([100], 50) == 100

    def test_percentile_p50(self):
        """测试中位数计算"""
        values = [1, 2, 3, 4, 5]
        assert calculate_percentile(values, 50) == 3

    def test_percentile_p99(self):
        """测试 P99 计算"""
        values = list(range(1, 101))  # 1 to 100
        p99 = calculate_percentile(values, 99)
        assert 98 <= p99 <= 100

    def test_percentile_p0(self):
        """测试 P0 返回最小值"""
        values = [10, 20, 30, 40, 50]
        assert calculate_percentile(values, 0) == 10

    def test_percentile_p100(self):
        """测试 P100 返回最大值"""
        values = [10, 20, 30, 40, 50]
        assert calculate_percentile(values, 100) == 50


class TestLogAnalyzer:
    """测试 LogAnalyzer 类"""

    def test_empty_analyzer(self):
        """测试空分析器不报错"""
        analyzer = LogAnalyzer()
        stats = analyzer.get_stats()
        assert stats['total_logs'] == 0
        assert stats['error_count'] == 0
        assert stats['error_rate'] == 0.0
        assert stats['services'] == {}

    def test_add_single_record(self):
        """测试添加单条记录"""
        analyzer = LogAnalyzer()
        analyzer.add_record({
            'timestamp': '2025-01-15T10:23:45',
            'level': 'INFO',
            'service': 'auth',
            'latency_ms': 50,
            'msg': 'test'
        })
        stats = analyzer.get_stats()
        assert stats['total_logs'] == 1
        assert stats['error_count'] == 0
        assert stats['error_rate'] == 0.0
        assert 'auth' in stats['services']

    def test_error_count(self):
        """测试错误计数"""
        analyzer = LogAnalyzer()
        analyzer.add_record({'level': 'INFO', 'service': 'a', 'latency_ms': 10})
        analyzer.add_record({'level': 'ERROR', 'service': 'b', 'latency_ms': 20})
        analyzer.add_record({'level': 'ERROR', 'service': 'c', 'latency_ms': 30})
        stats = analyzer.get_stats()
        assert stats['error_count'] == 2
        assert stats['error_rate'] == pytest.approx(66.67, rel=0.01)

    def test_service_latency_stats(self):
        """测试服务延迟统计"""
        analyzer = LogAnalyzer()
        # 添加 payment 服务的多条记录
        for latency in [100, 200, 300, 400, 500]:
            analyzer.add_record({'level': 'INFO', 'service': 'payment', 'latency_ms': latency})
        # 添加 auth 服务的记录
        for latency in [10, 20, 30]:
            analyzer.add_record({'level': 'INFO', 'service': 'auth', 'latency_ms': latency})

        stats = analyzer.get_stats()
        assert 'payment' in stats['services']
        assert 'auth' in stats['services']
        assert stats['services']['payment']['count'] == 5
        assert stats['services']['auth']['count'] == 3
        # P50 应该在合理范围内
        assert stats['services']['payment']['p50'] == 300

    def test_error_rate_calculation(self):
        """测试错误率计算"""
        analyzer = LogAnalyzer()
        # 10 条记录，2 条错误
        for _ in range(8):
            analyzer.add_record({'level': 'INFO', 'service': 'test', 'latency_ms': 10})
        for _ in range(2):
            analyzer.add_record({'level': 'ERROR', 'service': 'test', 'latency_ms': 100})

        stats = analyzer.get_stats()
        assert stats['error_rate'] == 20.0

    def test_multiple_services(self):
        """测试多服务统计"""
        analyzer = LogAnalyzer()
        services = ['payment', 'auth', 'db', 'user', 'cache']
        for service in services:
            analyzer.add_record({'level': 'INFO', 'service': service, 'latency_ms': 50})

        stats = analyzer.get_stats()
        assert len(stats['services']) == 5
        for service in services:
            assert service in stats['services']
            assert stats['services'][service]['count'] == 1
