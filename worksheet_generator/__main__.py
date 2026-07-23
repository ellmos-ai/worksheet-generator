"""Ermoeglicht `python -m worksheet_generator <command> ...` (siehe cli.py)."""
from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
