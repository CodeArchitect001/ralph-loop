"""
鲁棒的 JSONL 解析器模块

提供解析 JSON Lines 格式日志文件的功能，能够优雅地处理损坏的 JSON 行。
"""

import json
import sys
from typing import Dict, List, Optional


def parse_line(line: str, line_number: int = 0) -> Optional[Dict]:
    """
    解析单行 JSON 字符串。

    Args:
        line: JSON 格式的字符串
        line_number: 行号，用于错误报告

    Returns:
        解析成功返回包含日志字段的字典，失败返回 None
    """
    line = line.strip()
    if not line:
        return None

    try:
        record = json.loads(line)
        # 验证必需字段
        required_fields = ['timestamp', 'level', 'service', 'latency_ms', 'msg']
        if all(field in record for field in required_fields):
            return record
        else:
            print(f"Warning: Line {line_number} missing required fields", file=sys.stderr)
            return None
    except json.JSONDecodeError as e:
        print(f"Warning: Line {line_number} has invalid JSON - {e}", file=sys.stderr)
        return None


def parse_file(file_path: str) -> List[Dict]:
    """
    批量解析 JSONL 文件。

    Args:
        file_path: JSONL 文件路径

    Returns:
        解析成功的日志记录列表，每个记录包含 timestamp, level, service, latency_ms, msg 字段

    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    records: List[Dict] = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, start=1):
            record = parse_line(line, line_number)
            if record is not None:
                records.append(record)

    return records
