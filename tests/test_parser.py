"""
测试 JSONL 解析器模块
"""

import os
import pytest
from src.parser import parse_line, parse_file


class TestParseLine:
    """测试单行解析功能"""

    def test_parse_valid_line(self):
        """测试解析有效的 JSON 行"""
        line = '{"timestamp": "2025-01-15T10:23:45", "level": "ERROR", "service": "payment", "latency_ms": 1250, "msg": "timeout"}'
        result = parse_line(line)
        assert result is not None
        assert result['timestamp'] == "2025-01-15T10:23:45"
        assert result['level'] == "ERROR"
        assert result['service'] == "payment"
        assert result['latency_ms'] == 1250
        assert result['msg'] == "timeout"

    def test_parse_broken_json(self):
        """测试解析损坏的 JSON 行返回 None"""
        line = '{"timestamp": "broken json here'
        result = parse_line(line)
        assert result is None

    def test_parse_missing_brace(self):
        """测试解析缺少括号的 JSON 行返回 None"""
        line = '{"timestamp": "2025-01-15T10:23:46", "level": "WARN", "service": "payment", "latency_ms": 890, "msg": "slow_query"'
        result = parse_line(line)
        assert result is None

    def test_parse_empty_line(self):
        """测试解析空行返回 None"""
        result = parse_line("")
        assert result is None

    def test_parse_whitespace_only(self):
        """测试解析只有空白字符的行返回 None"""
        result = parse_line("   \t\n  ")
        assert result is None

    def test_parse_missing_required_field(self):
        """测试解析缺少必需字段的 JSON 行返回 None"""
        line = '{"timestamp": "2025-01-15T10:23:45", "level": "ERROR"}'
        result = parse_line(line)
        assert result is None


class TestParseFile:
    """测试文件解析功能"""

    def test_parse_valid_file(self):
        """测试解析测试数据文件，跳过损坏行"""
        filepath = os.path.join(os.path.dirname(__file__), 'data', 'raw_logs.jsonl')
        records = parse_file(filepath)

        # 应该有 19 条有效记录（21 行减去 2 条损坏的）
        assert len(records) == 19

        # 验证所有记录都有必需字段
        required_fields = ['timestamp', 'level', 'service', 'latency_ms', 'msg']
        for record in records:
            for field in required_fields:
                assert field in record

    def test_parse_nonexistent_file(self):
        """测试解析不存在的文件抛出 FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            parse_file('/nonexistent/path/to/file.jsonl')

    def test_parse_file_returns_list(self):
        """测试 parse_file 返回列表类型"""
        filepath = os.path.join(os.path.dirname(__file__), 'data', 'raw_logs.jsonl')
        records = parse_file(filepath)
        assert isinstance(records, list)
