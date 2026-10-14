# Python Log Analyzer

A small command-line program that reads a text log, counts entries by severity, finds repeated messages, and prints error and critical events. It uses only the Python standard library.

## Development lifecycle

1. **Requirements:** accept a log file, summarize severity levels and repeated messages, and make it possible to filter by severity or message text.
2. **Design:** use one predictable line format: `YYYY-MM-DD HH:MM:SS [LEVEL] message`. Keep parsing, file analysis, and reporting in separate functions.
3. **Implementation:** `log_analyzer.py` parses each nonblank line, ignores malformed lines while counting them, applies optional filters, and prints a report. Input errors are reported with command-line usage help.
4. **Run and review:** use the sample below to inspect the output and try filters. For production use, compare the accepted line format with the application's actual logs and adjust `LOG_PATTERN` if needed.
5. **Maintenance:** add format support when log formats change, and consider structured JSON output or export options if reports need to feed another system.

## Requirements

Python 3.10 or later. No third-party packages are required.

## Examples

From this folder, analyze the included example log:

```bash
python log_analyzer.py examples/application.log
```

Show only errors:

```bash
python log_analyzer.py examples/application.log --level ERROR
```

Find entries whose message contains `database` (case-insensitive):

```bash
python log_analyzer.py examples/application.log --keyword database
```

Show the three most frequent messages:

```bash
python log_analyzer.py examples/application.log --top 3
```

Combine filters:

```bash
python log_analyzer.py examples/application.log --level ERROR --keyword timeout
```

The report includes matching entry counts by level, frequent messages, malformed line count, and matching `ERROR`/`CRITICAL` entries. A malformed line is skipped rather than treated as a valid event.
