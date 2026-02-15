"""
测试 JSONL 解析器模块
"""

import pytest
import sys
from io import StringIO
from src.parser import parse_line, parse_file


class TestParseLine:
    """测试单行解析函数"""

    def test_parse_valid_line(self):
        """测试解析有效的 JSON 行"""
        line = '{"timestamp": "2025-01-15T10:23:45", "level": "ERROR", "service": "payment", "latency_ms": 1250, "msg": "timeout"}'
        result = parse_line(line, 1)

        assert result is not None
        assert result['timestamp'] == "2025-01-15T10:23:45"
        assert result['level'] == "ERROR"
        assert result['service'] == "payment"
        assert result['latency_ms'] == 1250
        assert result['msg'] == "timeout"

    def test_parse_invalid_json(self, capsys):
        """测试解析损坏的 JSON 行，应该返回 None 并输出警告"""
        line = '{"timestamp": "broken json here'
        result = parse_line(line, 8)

        assert result is None
        captured = capsys.readouterr()
        assert "Line 8" in captured.err
        assert "invalid JSON" in captured.err

    def test_parse_missing_closing_brace(self, capsys):
        """测试缺少闭合括号的 JSON 行"""
        line = '{"timestamp": "2025-01-15T10:23:46", "level": "WARN", "service": "payment", "latency_ms": 890, "msg": "slow_query"'
        result = parse_line(line, 3)

        assert result is None
        captured = capsys.readouterr()
        assert "Line 3" in captured.err

    def test_parse_empty_line(self):
        """测试空行"""
        assert parse_line("", 0) is None
        assert parse_line("   ", 0) is None
        assert parse_line("\n", 0) is None

    def test_parse_missing_required_field(self, capsys):
        """测试缺少必需字段的 JSON"""
        line = '{"timestamp": "2025-01-15T10:23:45", "level": "ERROR"}'
        result = parse_line(line, 5)

        assert result is None
        captured = capsys.readouterr()
        assert "Line 5" in captured.err
        assert "missing required fields" in captured.err


class TestParseFile:
    """测试批量文件解析函数"""

    def test_parse_raw_logs_file(self):
        """测试解析测试数据文件"""
        records = parse_file("tests/data/raw_logs.jsonl")

        # 21 行中，第3行和第8行损坏，应解析出 19 条记录
        assert len(records) == 19

        # 验证第一条记录
        assert records[0]['level'] == "ERROR"
        assert records[0]['service'] == "payment"

        # 验证最后一条记录
        assert records[-1]['level'] == "ERROR"
        assert records[-1]['service'] == "auth"

    def test_parse_nonexistent_file(self):
        """测试解析不存在的文件"""
        with pytest.raises(FileNotFoundError):
            parse_file("nonexistent_file.jsonl")

    def test_all_records_have_required_fields(self):
        """测试所有解析出的记录都包含必需字段"""
        records = parse_file("tests/data/raw_logs.jsonl")
        required_fields = ['timestamp', 'level', 'service', 'latency_ms', 'msg']

        for record in records:
            for field in required_fields:
                assert field in record, f"Missing field: {field}"
