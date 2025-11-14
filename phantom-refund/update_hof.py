#!/usr/bin/env python3
"""
update_hof.py

Small helper to append a new row to the Hall of Fame table in README.md.

Usage (from repo root):

    python phantom-refund/update_hof.py <handle> "<approach tag>"

Examples:

    python phantom-refund/update_hof.py s8torxyz "Foundry + Rust mini-EVM"
    python phantom-refund/update_hof.py alice "Manual opcode tracing"

The script:
- Finds the "## 🏅 Hall of Fame" section in README.md
- Finds the markdown table under it
- Removes the `_None yet_` placeholder if present
- Appends a new row: | `handle` | approach tag |
- If the handle already exists, it updates the approach tag instead of duplicating.
"""

import sys
from pathlib import Path

README_PATH = Path(__file__).resolve().parent / "README.md"


def update_hof(handle: str, approach: str) -> None:
    if not README_PATH.exists():
        print(f"ERROR: README.md not found at {README_PATH}")
        sys.exit(1)

    with README_PATH.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # Find the Hall of Fame section
    hof_header_prefix = "🏅 Hall of Fame"
    try:
        hof_start_idx = next(
            i
            for i, line in enumerate(lines)
            if line.strip()
            and line.strip().lstrip("#").strip().startswith(hof_header_prefix)
        )
    except StopIteration:
        print("ERROR: Could not find Hall of Fame section in README.md")
        sys.exit(1)

    # Find the table header inside the section
    table_header_idx = None
    separator_idx = None
    for i in range(hof_start_idx, len(lines)):
        line = lines[i]
        if line.strip().startswith("| Handle"):
            table_header_idx = i
        if table_header_idx is not None and line.strip().startswith("|---"):
            separator_idx = i
            break

    if table_header_idx is None or separator_idx is None:
        print("ERROR: Could not find Hall of Fame table header/separator in README.md")
        sys.exit(1)

    # Collect existing rows
    rows_start = separator_idx + 1
    rows_end = rows_start
    while rows_end < len(lines) and lines[rows_end].strip().startswith("|"):
        rows_end += 1

    existing_rows = [l.rstrip("\n") for l in lines[rows_start:rows_end]]

    # Remove placeholder row if present
    new_rows = []
    for row in existing_rows:
        if "_None yet_" in row:
            continue
        new_rows.append(row)

    # Check if handle already exists; if so, update its approach
    row_prefix = f"| `{handle}`"
    updated = False
    for idx, row in enumerate(new_rows):
        if row.strip().startswith(row_prefix):
            # Row format: | `handle` | Approach |
            parts = row.split("|")
            # parts: ["", " `handle` ", " Approach ", ""]
            if len(parts) >= 3:
                parts[2] = f" {approach} "
                new_rows[idx] = "|".join(parts)
                updated = True
                break

    if not updated:
        # Append new row
        new_row = f"| `{handle}` | {approach} |"
        new_rows.append(new_row)

    # Reconstruct README
    new_lines = []
    new_lines.extend(lines[:rows_start])
    for row in new_rows:
        new_lines.append(row + "\n")
    new_lines.extend(lines[rows_end:])

    with README_PATH.open("w", encoding="utf-8") as f:
        f.writelines(new_lines)

    if updated:
        print(f"Updated existing Hall of Fame entry for handle `{handle}`.")
    else:
        print(f"Added `{handle}` to Hall of Fame.")


def main():
    if len(sys.argv) < 3:
        print("Usage: python phantom-refund/update_hof.py <handle> \"<approach tag>\"")
        sys.exit(1)

    handle = sys.argv[1].strip()
    approach = " ".join(sys.argv[2:]).strip()

    if not handle:
        print("ERROR: handle is empty")
        sys.exit(1)
    if not approach:
        print("ERROR: approach tag is empty")
        sys.exit(1)

    update_hof(handle, approach)


if __name__ == "__main__":
    main()
