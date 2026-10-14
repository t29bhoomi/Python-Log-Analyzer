"""Analyze plain-text application logs and summarize levels and messages."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})\s+"
    r"\[(?P<level>[A-Za-z]+)\]\s*(?P<message>.*)$"
)


@dataclass(frozen=True)
class LogEntry:
    timestamp: str
    level: str
    message: str


def parse_line(line: str) -> LogEntry | None:
    """Parse a line like '2026-10-14 09:30:00 [ERROR] Database unavailable'."""
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None
    return LogEntry(
        timestamp=match.group("timestamp"),
        level=match.group("level").upper(),
        message=match.group("message"),
    )


def analyze_file(
    path: Path, level: str | None = None, keyword: str | None = None
) -> tuple[list[LogEntry], int]:
    """Return matching entries and the number of nonblank malformed lines."""
    entries: list[LogEntry] = []
    malformed = 0
    wanted_level = level.upper() if level else None
    wanted_keyword = keyword.casefold() if keyword else None

    with path.open("r", encoding="utf-8", errors="replace") as log_file:
        for raw_line in log_file:
            if not raw_line.strip():
                continue
            entry = parse_line(raw_line)
            if entry is None:
                malformed += 1
                continue
            if wanted_level and entry.level != wanted_level:
                continue
            if wanted_keyword and wanted_keyword not in entry.message.casefold():
                continue
            entries.append(entry)
    return entries, malformed


def print_report(entries: list[LogEntry], malformed: int, top: int) -> None:
    print("Log Analyzer Report")
    print("===================")
    print(f"Matching entries: {len(entries)}")
    print(f"Malformed lines:  {malformed}")
    print("\nEntries by level:")
    counts = Counter(entry.level for entry in entries)
    if counts:
        for level, count in sorted(counts.items()):
            print(f"  {level:<8} {count}")
    else:
        print("  (none)")

    print(f"\nTop {top} messages:")
    messages = Counter(entry.message for entry in entries)
    if messages:
        for message, count in messages.most_common(top):
            print(f"  {count:>3}  {message}")
    else:
        print("  (none)")

    errors = [entry for entry in entries if entry.level in {"ERROR", "CRITICAL"}]
    if errors:
        print("\nErrors and critical events:")
        for entry in errors:
            print(f"  {entry.timestamp} [{entry.level}] {entry.message}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize a plain-text log with timestamps and [LEVEL] labels."
    )
    parser.add_argument("file", type=Path, help="Path to the log file")
    parser.add_argument("--level", help="Only include a level, such as ERROR")
    parser.add_argument("--keyword", help="Only include messages containing this text")
    parser.add_argument("--top", type=int, default=5, help="Number of frequent messages to show (default: 5)")
    args = parser.parse_args()

    if args.top < 1:
        parser.error("--top must be at least 1")
    if not args.file.is_file():
        parser.error(f"log file not found: {args.file}")

    try:
        entries, malformed = analyze_file(args.file, args.level, args.keyword)
    except OSError as error:
        parser.error(f"could not read log file: {error}")
    print_report(entries, malformed, args.top)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
