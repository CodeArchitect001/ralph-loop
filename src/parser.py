"""JSONL parser for log stream analyzer."""

import json
import sys
from typing import Dict, List, Optional


def parse_line(line: str) -> Optional[Dict]:
    """
    Parse a single JSON line.

    Args:
        line: A string containing JSON data

    Returns:
        Parsed dictionary if successful, None if parsing fails
    """
    line = line.strip()
    if not line:
        return None

    try:
        record = json.loads(line)
        # Validate required fields
        required_fields = ['timestamp', 'level', 'service', 'latency_ms', 'msg']
        if all(field in record for field in required_fields):
            return record
        print("Warning: Missing required fields in line", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse JSON line: {e}", file=sys.stderr)
        return None


def parse_file(filepath: str) -> List[Dict]:
    """
    Parse a JSONL file and return list of valid records.

    Args:
        filepath: Path to the JSONL file

    Returns:
        List of parsed dictionaries, skipping invalid lines
    """
    records = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                record = parse_line(line)
                if record is not None:
                    records.append(record)
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        raise
    except IOError as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        raise

    return records
