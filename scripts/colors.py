#!/usr/bin/env python3
"""Simple script to print colored messages for Makefile."""

import sys


def main():
    """Print colored message based on level."""
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/colors.py [INFO|WARN|ERROR] message")
        sys.exit(1)

    level = sys.argv[1].upper()
    message = " ".join(sys.argv[2:])

    # ANSI color codes
    colors = {
        "INFO": "\033[0;32m",  # Green
        "WARN": "\033[0;33m",  # Yellow
        "ERROR": "\033[0;31m",  # Red
    }
    reset = "\033[0m"

    color = colors.get(level, "")
    print(f"{color}{message}{reset}")


if __name__ == "__main__":
    main()
