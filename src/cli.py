"""CLI interface for log stream analyzer."""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parser import parse_file
from src.analyzer import LogAnalyzer
from src.reporter import generate_report


def main():
    """
    Main CLI entry point.

    Returns:
        Exit code: 0 for success, 1 for file not found, 2 for parse error
    """
    parser = argparse.ArgumentParser(
        description='Log Stream Analyzer - Generate HTML reports from JSONL log files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.cli --input logs.jsonl --output report.html
  python -m src.cli --input logs.jsonl --window-size 1000 --verbose
        """
    )

    parser.add_argument(
        '--input', '-i',
        required=True,
        help='Input JSONL file path'
    )

    parser.add_argument(
        '--output', '-o',
        default='report.html',
        help='Output HTML file path (default: report.html)'
    )

    parser.add_argument(
        '--window-size', '-w',
        type=int,
        default=None,
        help='Only analyze the last N log entries (default: all)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show processing progress'
    )

    args = parser.parse_args()

    # Check input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        # Parse input file
        if args.verbose:
            print(f"Parsing input file: {args.input}")

        records = parse_file(args.input)

        if args.verbose:
            print(f"Parsed {len(records)} valid records")

        # Apply window size if specified
        if args.window_size is not None and args.window_size > 0:
            records = records[-args.window_size:]
            if args.verbose:
                print(f"Analyzing last {len(records)} records (window size: {args.window_size})")

        # Analyze records
        if args.verbose:
            print("Analyzing records...")

        analyzer = LogAnalyzer()
        for i, record in enumerate(records):
            analyzer.add_record(record)
            if args.verbose and (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{len(records)} records")

        stats = analyzer.get_stats()

        if args.verbose:
            print(f"Analysis complete: {stats['total_logs']} logs, {stats['error_rate']:.2f}% error rate")

        # Generate report
        if args.verbose:
            print(f"Generating report: {args.output}")

        generate_report(stats, args.output)

        if args.verbose:
            print(f"Report generated successfully!")

        return 0

    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error during processing: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
