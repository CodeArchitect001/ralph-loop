"""
JSONL 解析器测试用例
"""

import os
import sys
import pytest

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser import parse_line, parse_file


class TestParseLine:
    """测试 parse_line 函数"""

    def test_valid_json_line(self):
        """测试有效的 JSON 行"""
        line = '{"timestamp": "2025-01-15T10:23:45", "level": "ERROR", "service": "payment", "latency_ms": 1250, "msg": "timeout"}'
        result = parse_line(line)
        assert result is not None
        assert result['timestamp'] == '2025-01-15T10:23:45'
        assert result['level'] == 'ERROR'
        assert result['service'] == 'payment'
        assert result['latency_ms'] == 1250
        assert result['msg'] == 'timeout'

    def test_invalid_json_line(self):
        """测试无效的 JSON 行"""
        line = '{"timestamp": "broken json here'
        result = parse_line(line)
        assert result is None

    def test_empty_line(self):
        """测试空行"""
        assert parse_line('') is None
        assert parse_line('   ') is None

    def test_missing_required_field(self):
        """测试缺少必需字段"""
        line = '{"timestamp": "2025-01-15T10:23:45", "level": "INFO"}'
        result = parse_line(line)
        assert result is None


class TestParseFile:
    """测试 parse_file 函数"""

    def test_parse_valid_file(self):
        """测试解析包含损坏行的文件"""
        test_file = os.path.join(os.path.dirname(__file__), 'data', 'raw_logs.jsonl')
        records = parse_file(test_file)

        # 文件有 21 行，其中第 3 行和第 8 行损坏
        # 应该解析出 19 条有效记录
        assert len(records) == 19

    def test_all_records_have_required_fields(self):
        """测试所有记录都有必需字段"""
        test_file = os.path.join(os.path.dirname(__file__), 'data', 'raw_logs.jsonl')
        records = parse_file(test_file)

        required_fields = ['timestamp', 'level', 'service', 'latency_ms', 'msg']
        for record in records:
            for field in required_fields:
                assert field in record, f"Missing field: {field}"

    def test_file_not_found(self):
        """测试文件不存在的情况"""
        with pytest.raises(FileNotFoundError):
            parse_file('/nonexistent/path/to/file.jsonl')

    def test_skip_corrupted_lines(self):
        """测试正确跳过损坏行（第3行和第8行）"""
        test_file = os.path.join(os.path.dirname(__file__), 'data', 'raw_logs.jsonl')
        records = parse_file(test_file)

        # 验证解析出的记录
        # 第 1 行应该是 payment ERROR
        assert records[0]['service'] == 'payment'
        assert records[0]['level'] == 'ERROR'

        # 第 2 行应该是 auth INFO
        assert records[1]['service'] == 'auth'
        assert records[1]['level'] == 'INFO'

        # 第 3 行损坏被跳过
        # 所以 records[2] 应该是第 4 行 db ERROR
        assert records[2]['service'] == 'db'
        assert records[2]['level'] == 'ERROR'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
