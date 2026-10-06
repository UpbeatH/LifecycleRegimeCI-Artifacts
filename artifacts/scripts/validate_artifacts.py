"""Minimal validation placeholder for the compact artifact package.

The script intentionally validates package structure only. It does not execute
Flink jobs, access native checkpoints, or reproduce private infrastructure.
"""

from pathlib import Path

REQUIRED_DIRS = [
    "protocols",
    "manifests",
    "results",
    "receipts",
]


def validate(root: str = "artifacts") -> bool:
    base = Path(root)
    return all((base / item).exists() for item in REQUIRED_DIRS)


if __name__ == "__main__":
    raise SystemExit(0 if validate() else 1)
