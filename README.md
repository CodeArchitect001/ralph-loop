# Log Stream Analyzer

A lightweight log stream analyzer that parses JSONL files, computes statistics, and generates HTML monitoring reports.

## Features

- **JSONL Parser**: Robust parsing that skips malformed JSON lines
- **Streaming Analysis**: Incremental processing with error rate and latency statistics
- **HTML Reports**: Self-contained HTML reports with inline CSS styling
- **CLI Interface**: Easy-to-use command line tool

## Installation

No external dependencies required. Uses Python 3.9+ standard library only.

```bash
# Clone the repository
git clone <repo-url>
cd ralph-log-analyzer
```

## Usage

### Basic Usage

```bash
python -m src.cli --input logs.jsonl --output report.html
```

### With Verbose Output

```bash
python -m src.cli --input logs.jsonl --output report.html --verbose
```

### Window Size (Last N Logs)

```bash
python -m src.cli --input logs.jsonl --output report.html --window-size 1000
```

## CLI Options

| Option | Short | Description |
|--------|-------|-------------|
| `--input` | `-i` | Input JSONL file path (required) |
| `--output` | `-o` | Output HTML file path (default: report.html) |
| `--window-size` | `-w` | Analyze only last N log entries |
| `--verbose` | `-v` | Show processing progress |

## Exit Codes

- `0`: Success
- `1`: Input file not found
- `2`: Parse error

## Input Format

Expects JSONL format with the following fields:

```json
{"timestamp": "2025-01-15T10:23:45", "level": "INFO", "service": "auth", "latency_ms": 23, "msg": "token_valid"}
{"timestamp": "2025-01-15T10:23:46", "level": "ERROR", "service": "payment", "latency_ms": 1250, "msg": "timeout"}
```

Required fields:
- `timestamp`: ISO 8601 timestamp
- `level`: Log level (INFO, WARN, ERROR)
- `service`: Service name
- `latency_ms`: Latency in milliseconds
- `msg`: Log message

## Output

Generates an HTML report with:

- **Summary Cards**: Total logs, error rate, max P99 latency, service count
- **Service Details Table**: Per-service statistics with P50/P99 latencies
- **Color Coding**:
  - Green: Error rate < 1%
  - Yellow: Error rate 1-5%
  - Red: Error rate > 5%

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run parser tests only
python -m pytest tests/test_parser.py -v

# Run analyzer tests only
python -m pytest tests/test_analyzer.py -v
```

## Code Quality

```bash
# Run pylint
pylint src/ --fail-under=8.0
```

## Project Structure

```
ralph-log-analyzer/
├── src/
│   ├── __init__.py      # Package exports
│   ├── parser.py        # JSONL parser
│   ├── analyzer.py      # Streaming analysis engine
│   ├── reporter.py      # HTML report generator
│   └── cli.py           # Command line interface
├── tests/
│   ├── test_parser.py   # Parser tests
│   ├── test_analyzer.py # Analyzer tests
│   └── data/
│       └── raw_logs.jsonl  # Test data
├── .ralph/
│   ├── stories.json     # Task definitions
│   └── progress.txt     # Progress log
├── PROMPT.md            # Development instructions
├── run_bash_experiment.sh  # Experiment script
└── README.md            # This file
```

## License

MIT
