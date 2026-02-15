"""
CLI 接口 - 命令行入口
"""

import argparse
import sys
from typing import List

from src.parser import parse_file
from src.analyzer import LogAnalyzer
from src.reporter import generate_report


def main(args: List[str] = None) -> int:
    """
    CLI 主入口函数。

    Args:
        args: 命令行参数列表，默认使用 sys.argv

    Returns:
        返回码：0 成功，1 文件不存在，2 解析错误
    """
    parser = argparse.ArgumentParser(
        description='Log Stream Analyzer - 分析日志文件并生成 HTML 报告'
    )
    parser.add_argument(
        '--input', '-i',
        required=True,
        help='输入 JSONL 日志文件路径'
    )
    parser.add_argument(
        '--output', '-o',
        default='report.html',
        help='输出 HTML 报告路径（默认：report.html）'
    )
    parser.add_argument(
        '--window-size', '-w',
        type=int,
        default=None,
        help='只分析最近 N 条日志（默认：全部）'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='显示处理进度'
    )

    parsed_args = parser.parse_args(args)

    # 解析日志文件
    if parsed_args.verbose:
        print(f'Reading log file: {parsed_args.input}')

    try:
        records = parse_file(parsed_args.input)
    except FileNotFoundError:
        print(f'Error: File not found: {parsed_args.input}', file=sys.stderr)
        return 1
    except Exception as e:
        print(f'Error: Failed to parse file: {e}', file=sys.stderr)
        return 2

    if parsed_args.verbose:
        print(f'Parsed {len(records)} valid records')

    # 应用窗口大小限制
    if parsed_args.window_size is not None and parsed_args.window_size > 0:
        records = records[-parsed_args.window_size:]
        if parsed_args.verbose:
            print(f'Processing last {len(records)} records '
                  f'(window size: {parsed_args.window_size})')

    # 检查是否有有效记录
    if not records:
        print('Warning: No valid records to analyze', file=sys.stderr)
        # 仍然生成报告，只是统计为空
        stats = {
            'total_logs': 0,
            'error_count': 0,
            'error_rate': 0.0,
            'services': {}
        }
    else:
        # 分析日志
        if parsed_args.verbose:
            print('Analyzing logs...')

        analyzer = LogAnalyzer()
        for record in records:
            analyzer.add_record(record)

        stats = analyzer.get_stats()

        if parsed_args.verbose:
            print(f'Analysis complete: {stats["total_logs"]} logs, '
                  f'{stats["error_rate"]:.2f}% error rate')

    # 生成报告
    if parsed_args.verbose:
        print(f'Generating report: {parsed_args.output}')

    generate_report(stats, parsed_args.output)

    if parsed_args.verbose:
        print('Done!')

    return 0


if __name__ == '__main__':
    sys.exit(main())
