
#!/usr/bin/env python3
"""
Template for the maintainer's local submission checker.

Usage (maintainer only, with local copy):

    cp check_submission_template.py check_submission_local.py
    # edit CORRECT_ANSWER in check_submission_local.py (do NOT commit)
    python check_submission_local.py submissions/<handle>.txt

Do NOT commit the file with the real CORRECT_ANSWER to the public repo.
"""

import sys
import hashlib

# Replace this in your local copy (check_submission_local.py), NOT in git.
CORRECT_ANSWER = "REPLACE_ME_WITH_HEX_ANSWER" 


def expected_hash(handle: str) -> str:
    """
    The expected hash is SHA256("<handle>-<ANSWER>"), where ANSWER is CORRECT_ANSWER.
    """
    s = f"{handle}-{CORRECT_ANSWER}"
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def main():
    if CORRECT_ANSWER == "REPLACE_ME_WITH_HEX_ANSWER":
        print("ERROR: Please set CORRECT_ANSWER in your local copy (check_submission_local.py).")
        sys.exit(1)

    if len(sys.argv) != 2:
        print("Usage: python check_submission_local.py submissions/<handle>.txt")
        sys.exit(1)

    path = sys.argv[1]

    try:
        with open(path, "r", encoding="utf-8") as f:
            line = ""
            for ln in f:
                if ln.strip():
                    line = ln.strip()
                    break
    except FileNotFoundError:
        print(f"File not found: {path}")
        sys.exit(1)

    if not line:
        print("No non-empty line found in submission file.")
        sys.exit(1)

    parts = line.split()
    if len(parts) != 2:
        print(f"Expected '<handle> <hash>', got: {line!r}")
        sys.exit(1)

    handle, submitted_hash = parts
    submitted_hash = submitted_hash.lower()

    correct = expected_hash(handle)
    if submitted_hash == correct:
        print(f"✅ {handle} — Correct hash for this handle.")
        sys.exit(0)
    else:
        print(f"❌ {handle} — Incorrect hash.")
        print(f"    (Got {submitted_hash}, expected something else.)")
        sys.exit(1)


if __name__ == "__main__":
    main()
