"""
CLI Interface Module
Command-line interface for log stream analyzer.
"""

import argparse
import sys
from typing import List

from .parser import parse_file
from .analyzer import LogAnalyzer
from .reporter import generate_report


def main(args: List[str] = None) -> int:
    """
    Main CLI entry point.

    Args:
        args: Command-line arguments (default: sys.argv[1:])

    Returns:
        Exit code: 0 for success, 1 for file not found, 2 for parse error
    """
    parser = argparse.ArgumentParser(
        description='Log Stream Analyzer - Generate monitoring dashboards from log files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli --input logs.jsonl --output report.html
  python -m src.cli --input logs.jsonl --output report.html --window-size 100
  python -m src.cli --input logs.jsonl --output report.html --verbose
        """
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Path to input JSONL log file'
    )

    parser.add_argument(
        '--output',
        default='report.html',
        help='Path to output HTML report (default: report.html)'
    )

    parser.add_argument(
        '--window-size',
        type=int,
        default=None,
        help='Only analyze the last N log entries (default: analyze all)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show processing progress'
    )

    parsed_args = parser.parse_args(args)

    try:
        # Step 1: Parse input file
        if parsed_args.verbose:
            print(f"Reading logs from: {parsed_args.input}")

        try:
            records = parse_file(parsed_args.input)
        except FileNotFoundError:
            print(f"Error: Input file not found: {parsed_args.input}", file=sys.stderr)
            return 1

        if parsed_args.verbose:
            print(f"Parsed {len(records)} log records")

        # Step 2: Apply window size if specified
        if parsed_args.window_size is not None:
            records = records[-parsed_args.window_size:]
            if parsed_args.verbose:
                print(f"Analyzing last {len(records)} records (window size: {parsed_args.window_size})")

        # Step 3: Analyze logs
        if parsed_args.verbose:
            print("Analyzing logs...")

        analyzer = LogAnalyzer()
        for record in records:
            analyzer.add_record(record)

        stats = analyzer.get_stats()

        if parsed_args.verbose:
            print(f"Analysis complete:")
            print(f"  - Total logs: {stats['total_logs']}")
            print(f"  - Error rate: {stats['error_rate']:.2f}%")
            print(f"  - Services: {len(stats['services'])}")

        # Step 4: Generate report
        if parsed_args.verbose:
            print(f"Generating report: {parsed_args.output}")

        generate_report(stats, parsed_args.output)

        if parsed_args.verbose:
            print(f"✓ Report generated successfully!")

        return 0

    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
