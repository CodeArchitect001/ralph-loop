"""
CLI 接口模块

命令行入口，使用 argparse 处理参数。
"""

import argparse
import sys
from typing import List, Optional

from .parser import parse_file
from .analyzer import LogAnalyzer
from .reporter import generate_report


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器。

    Returns:
        配置好的 ArgumentParser 实例
    """
    parser = argparse.ArgumentParser(
        prog='python -m src.cli',
        description='Log Stream Analyzer - 分析 JSONL 日志文件并生成 HTML 报告'
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        dest='input_file',
        help='输入的 JSONL 日志文件路径'
    )

    parser.add_argument(
        '--output', '-o',
        default='report.html',
        dest='output_file',
        help='输出的 HTML 报告文件路径（默认: report.html）'
    )

    parser.add_argument(
        '--window-size', '-w',
        type=int,
        default=None,
        dest='window_size',
        help='只分析最近 N 条日志（默认: 全部）'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        dest='verbose',
        help='显示处理进度'
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:  # pylint: disable=too-many-branches
    """
    CLI 主入口函数。

    Args:
        argv: 命令行参数列表，None 时使用 sys.argv

    Returns:
        退出码：成功 0，文件不存在 1，解析错误 2
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # 验证输入文件是否存在
    try:
        if args.verbose:
            print(f'[INFO] 正在读取文件: {args.input_file}')

        records = parse_file(args.input_file)
    except FileNotFoundError:
        print(f'[ERROR] 文件不存在: {args.input_file}', file=sys.stderr)
        return 1
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f'[ERROR] 读取文件失败: {e}', file=sys.stderr)
        return 2

    # 应用窗口大小限制
    if args.window_size is not None and args.window_size > 0:
        records = records[-args.window_size:]
        if args.verbose:
            print(f'[INFO] 应用窗口大小: {args.window_size} 条')

    if args.verbose:
        print(f'[INFO] 成功解析 {len(records)} 条日志记录')

    # 检查是否有有效记录
    if not records:
        print('[WARN] 没有有效的日志记录', file=sys.stderr)
        # 仍然生成报告，但包含空数据

    # 分析日志
    if args.verbose:
        print('[INFO] 正在分析日志...')

    analyzer = LogAnalyzer()
    for record in records:
        analyzer.add_record(record)

    stats = analyzer.get_stats()

    if args.verbose:
        print(f'[INFO] 分析完成: 共 {stats["total_logs"]} 条日志, '
              f'错误率 {stats["error_rate"]:.2f}%')

    # 生成报告
    if args.verbose:
        print(f'[INFO] 正在生成报告: {args.output_file}')

    try:
        generate_report(stats, args.output_file)
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f'[ERROR] 生成报告失败: {e}', file=sys.stderr)
        return 2

    if args.verbose:
        print(f'[INFO] 报告已生成: {args.output_file}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
