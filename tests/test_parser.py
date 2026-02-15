"""Tests for JSONL parser."""

import os
import sys
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser import parse_line, parse_file


class TestParseLine:
    """Tests for parse_line function."""

    def test_parse_valid_json(self):
        """Test parsing a valid JSON line."""
        line = '{"timestamp": "2025-01-15T10:23:45", "level": "INFO", "service": "auth", "latency_ms": 23, "msg": "token_valid"}'
        result = parse_line(line)

        assert result is not None
        assert result['timestamp'] == "2025-01-15T10:23:45"
        assert result['level'] == "INFO"
        assert result['service'] == "auth"
        assert result['latency_ms'] == 23
        assert result['msg'] == "token_valid"

    def test_parse_invalid_json(self):
        """Test parsing an invalid JSON line returns None."""
        line = '{"timestamp": "broken json here'
        result = parse_line(line)

        assert result is None

    def test_parse_empty_line(self):
        """Test parsing an empty line returns None."""
        result = parse_line("")
        assert result is None

    def test_parse_whitespace_only(self):
        """Test parsing whitespace-only line returns None."""
        result = parse_line("   \n\t  ")
        assert result is None

    def test_parse_missing_fields(self):
        """Test parsing JSON with missing required fields returns None."""
        line = '{"timestamp": "2025-01-15", "level": "INFO"}'
        result = parse_line(line)

        assert result is None


class TestParseFile:
    """Tests for parse_file function."""

    def test_parse_test_data_file(self):
        """Test parsing the test data file."""
        filepath = os.path.join(os.path.dirname(__file__), 'data', 'raw_logs.jsonl')
        records = parse_file(filepath)

        # Should have 19 valid records (21 lines minus 2 broken at lines 3 and 8)
        assert len(records) == 19

    def test_parse_file_handles_broken_lines(self):
        """Test that broken lines are skipped without error."""
        filepath = os.path.join(os.path.dirname(__file__), 'data', 'raw_logs.jsonl')
        records = parse_file(filepath)

        # All records should have required fields
        for record in records:
            assert 'timestamp' in record
            assert 'level' in record
            assert 'service' in record
            assert 'latency_ms' in record
            assert 'msg' in record

    def test_parse_nonexistent_file(self):
        """Test parsing a nonexistent file raises error."""
        with pytest.raises(FileNotFoundError):
            parse_file('/nonexistent/path/to/file.jsonl')

    def test_parse_empty_file(self, tmp_path):
        """Test parsing an empty file returns empty list."""
        empty_file = tmp_path / "empty.jsonl"
        empty_file.write_text("")

        records = parse_file(str(empty_file))
        assert records == []
