"""
流式分析引擎测试
"""

import pytest
from src.analyzer import LogAnalyzer, percentile


class TestPercentile:
    """测试 percentile 函数。"""

    def test_percentile_empty(self):
        """空列表返回 0。"""
        assert percentile([], 50) == 0.0

    def test_percentile_single(self):
        """单元素列表返回该元素。"""
        assert percentile([100], 50) == 100

    def test_percentile_p50(self):
        """测试中位数。"""
        data = [1, 2, 3, 4, 5]
        assert percentile(data, 50) == 3.0

    def test_percentile_p99(self):
        """测试 P99。"""
        data = list(range(1, 101))  # 1-100
        result = percentile(data, 99)
        assert 98 <= result <= 100

    def test_percentile_p0(self):
        """测试最小值。"""
        data = [10, 20, 30, 40, 50]
        assert percentile(data, 0) == 10

    def test_percentile_p100(self):
        """测试最大值。"""
        data = [10, 20, 30, 40, 50]
        assert percentile(data, 100) == 50


class TestLogAnalyzer:
    """测试 LogAnalyzer 类。"""

    def test_empty_analyzer(self):
        """空分析器返回正确初始状态。"""
        analyzer = LogAnalyzer()
        stats = analyzer.get_stats()

        assert stats['total_logs'] == 0
        assert stats['error_count'] == 0
        assert stats['error_rate'] == 0.0
        assert stats['services'] == {}

    def test_add_single_record(self):
        """添加单条记录。"""
        analyzer = LogAnalyzer()
        analyzer.add_record({
            'timestamp': '2025-01-15T10:00:00',
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

    def test_error_counting(self):
        """错误计数正确。"""
        analyzer = LogAnalyzer()

        # 添加 3 条 INFO，2 条 ERROR
        for _ in range(3):
            analyzer.add_record({
                'level': 'INFO',
                'service': 'api',
                'latency_ms': 10
            })
        for _ in range(2):
            analyzer.add_record({
                'level': 'ERROR',
                'service': 'api',
                'latency_ms': 100
            })

        stats = analyzer.get_stats()
        assert stats['total_logs'] == 5
        assert stats['error_count'] == 2
        assert stats['error_rate'] == 40.0

    def test_service_latency_stats(self):
        """服务延迟统计正确。"""
        analyzer = LogAnalyzer()

        # 添加 auth 服务的延迟数据
        for latency in [10, 20, 30, 40, 50]:
            analyzer.add_record({
                'level': 'INFO',
                'service': 'auth',
                'latency_ms': latency
            })

        stats = analyzer.get_stats()
        auth_stats = stats['services']['auth']

        assert auth_stats['count'] == 5
        assert auth_stats['min'] == 10
        assert auth_stats['max'] == 50
        assert auth_stats['p50'] == 30.0

    def test_multiple_services(self):
        """多个服务的统计分开计算。"""
        analyzer = LogAnalyzer()

        # auth 服务
        analyzer.add_record({'level': 'INFO', 'service': 'auth', 'latency_ms': 100})
        analyzer.add_record({'level': 'INFO', 'service': 'auth', 'latency_ms': 200})

        # payment 服务
        analyzer.add_record({'level': 'ERROR', 'service': 'payment', 'latency_ms': 500})
        analyzer.add_record({'level': 'ERROR', 'service': 'payment', 'latency_ms': 1000})

        stats = analyzer.get_stats()

        assert 'auth' in stats['services']
        assert 'payment' in stats['services']
        assert stats['services']['auth']['count'] == 2
        assert stats['services']['payment']['count'] == 2
        assert stats['error_count'] == 2

    def test_p99_calculation(self):
        """P99 计算正确。"""
        analyzer = LogAnalyzer()

        # 添加 100 条记录
        for i in range(1, 101):
            analyzer.add_record({
                'level': 'INFO',
                'service': 'test',
                'latency_ms': i
            })

        stats = analyzer.get_stats()
        p99 = stats['services']['test']['p99']

        # P99 应该接近 99
        assert 98 <= p99 <= 100

    def test_record_without_latency(self):
        """缺少 latency_ms 字段的记录不崩溃。"""
        analyzer = LogAnalyzer()
        analyzer.add_record({'level': 'INFO', 'service': 'test'})

        stats = analyzer.get_stats()
        assert stats['total_logs'] == 1

    def test_record_without_service(self):
        """缺少 service 字段的记录使用 unknown。"""
        analyzer = LogAnalyzer()
        analyzer.add_record({'level': 'INFO', 'latency_ms': 50})

        stats = analyzer.get_stats()
        assert 'unknown' in stats['services']
