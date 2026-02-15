"""
JSONL 解析器模块 - 解析日志文件，跳过损坏的 JSON 行
"""

import json
import sys
from typing import Dict, List, Optional


def parse_line(line: str) -> Optional[Dict]:
    """
    解析单行 JSON 字符串。

    Args:
        line: JSON 格式的字符串

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
            print(f"Warning: Missing required fields in line", file=sys.stderr)
            return None
    except json.JSONDecodeError as e:
        print(f"Warning: Failed to parse JSON line: {e}", file=sys.stderr)
        return None


def parse_file(filepath: str) -> List[Dict]:
    """
    解析 JSONL 文件，返回所有有效记录列表。

    Args:
        filepath: JSONL 文件路径

    Returns:
        包含所有有效日志记录的列表

    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    records: List[Dict] = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            record = parse_line(line)
            if record is not None:
                records.append(record)

    return records
