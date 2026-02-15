"""
JSONL Parser Module
Parses .jsonl log files with error recovery for corrupted lines.
"""

import json
import sys
from typing import Dict, List, Optional


def parse_line(line: str, line_number: int = 0) -> Optional[Dict]:
    """
    Parse a single JSONL line.

    Args:
        line: A string containing a single JSON line
        line_number: Line number for error reporting

    Returns:
        Dict with parsed data or None if parsing fails
    """
    try:
        data = json.loads(line.strip())

        # Validate required fields exist
        required_fields = ['timestamp', 'level', 'service', 'latency_ms', 'msg']
        if all(field in data for field in required_fields):
            return data

        print(f"Warning: Line {line_number} missing required fields", file=sys.stderr)
        return None

    except json.JSONDecodeError as e:
        print(f"Warning: Corrupted JSON at line {line_number}: {str(e)}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Unexpected error at line {line_number}: {str(e)}", file=sys.stderr)
        return None


def parse_file(filepath: str) -> List[Dict]:
    """
    Parse an entire JSONL file.

    Args:
        filepath: Path to the .jsonl file

    Returns:
        List of dicts, each containing timestamp, level, service, latency_ms, msg
    """
    records = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:  # Skip empty lines
                    continue

                parsed = parse_line(line, line_number)
                if parsed is not None:
                    records.append(parsed)

    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        raise
    except IOError as e:
        print(f"Error: Cannot read file {filepath}: {str(e)}", file=sys.stderr)
        raise

    return records
