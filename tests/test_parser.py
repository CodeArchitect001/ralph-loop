"""
Tests for JSONL Parser Module
"""

import sys
import os
import io
from contextlib import redirect_stderr

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parser import parse_line, parse_file


class TestParseLine:
    """Tests for parse_line() function"""

    def test_parse_valid_line(self):
        """Should parse a valid JSONL line"""
        line = '{"timestamp": "2025-01-15T10:23:45", "level": "ERROR", "service": "payment", "latency_ms": 1250, "msg": "timeout"}'
        result = parse_line(line, 1)

        assert result is not None
        assert result['timestamp'] == "2025-01-15T10:23:45"
        assert result['level'] == "ERROR"
        assert result['service'] == "payment"
        assert result['latency_ms'] == 1250
        assert result['msg'] == "timeout"

    def test_parse_corrupted_json(self):
        """Should return None for corrupted JSON and log to stderr"""
        line = '{"timestamp": "broken json here'
        stderr_capture = io.StringIO()

        with redirect_stderr(stderr_capture):
            result = parse_line(line, 3)

        assert result is None
        assert "Warning" in stderr_capture.getvalue()
        assert "line 3" in stderr_capture.getvalue()

    def test_parse_missing_fields(self):
        """Should return None if required fields are missing"""
        line = '{"timestamp": "2025-01-15T10:23:45", "level": "INFO"}'
        stderr_capture = io.StringIO()

        with redirect_stderr(stderr_capture):
            result = parse_line(line, 5)

        assert result is None
        assert "missing required fields" in stderr_capture.getvalue()


class TestParseFile:
    """Tests for parse_file() function"""

    def test_parse_valid_file(self):
        """Should parse entire JSONL file and skip corrupted lines"""
        filepath = os.path.join(os.path.dirname(__file__), 'data', 'raw_logs.jsonl')
        stderr_capture = io.StringIO()

        with redirect_stderr(stderr_capture):
            results = parse_file(filepath)

        # Should have 19 valid records (21 total - 2 corrupted)
        assert len(results) == 19

        # All records should have required fields
        required_fields = ['timestamp', 'level', 'service', 'latency_ms', 'msg']
        for record in results:
            for field in required_fields:
                assert field in record

        # Corrupted lines should be logged
        stderr_output = stderr_capture.getvalue()
        assert "line 3" in stderr_output or "line 8" in stderr_output

    def test_parse_file_not_found(self):
        """Should raise FileNotFoundError for non-existent file"""
        try:
            parse_file('/non/existent/file.jsonl')
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_parse_empty_file(self):
        """Should handle empty file gracefully"""
        # Create temporary empty file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            temp_path = f.name

        try:
            results = parse_file(temp_path)
            assert results == []
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
