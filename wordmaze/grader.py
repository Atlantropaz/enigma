#!/usr/bin/env python3
"""
WordMaze Grader
- Creates sample tests if missing
- Runs correctness tests against a solver command (default: python3 private_solutions/rotator_finder.py)
- Runs a large performance test and scores by runtime
- Updates leaderboard.json (append + sorted)
- Prints a concise report

Solver contract:
- Reads the grid (N lines of equal length, no spaces) from STDIN.
- Prints the TOTAL MATCH COUNT as the FIRST LINE. (Additional lines are ignored by the grader.)

Usage:
  python3 grader.py                       # grade default solver
  python3 grader.py --cmd "python3 private_solutions/rotator_finder.py" --name "Sator"
  python3 grader.py --cmd "./my_cpp_solver" --name "Alice"
  python3 grader.py --list                # show current leaderboard

Scoring:
- Correctness: 60 points (split across 6 unit tests: 20 + 10 + 10 + 10 + 5 + 5)
- Performance: 40 points max, based on runtime on a generated large grid
  A+ (<= 50 ms): 40
  A  (<= 100 ms): 35
  B  (<= 250 ms): 28
  C  (<= 750 ms): 18
  D  (> 750 ms):  0
"""
import argparse, json, os, subprocess, sys, textwrap, time, random, re, shlex
from pathlib import Path
from datetime import datetime

def _count_overlaps(s: str, pat: re.Pattern) -> int:
    return sum(1 for _ in pat.finditer(s))

def _all_rows(grid):
    for s in grid:
        yield s

def _all_cols(grid):
    H, W = len(grid), len(grid[0])
    for c in range(W):
        yield "".join(grid[r][c] for r in range(H))

def _all_diagonals_SE(grid):
    H, W = len(grid), len(grid[0])
    for r0 in range(H):
        r, c = r0, 0
        out = []
        while r < H and c < W:
            out.append(grid[r][c]); r += 1; c += 1
        yield "".join(out)
    for c0 in range(1, W):
        r, c = 0, c0
        out = []
        while r < H and c < W:
            out.append(grid[r][c]); r += 1; c += 1
        yield "".join(out)

def _all_diagonals_SW(grid):
    H, W = len(grid), len(grid[0])
    for r0 in range(H):
        r, c = r0, W - 1
        out = []
        while r < H and c >= 0:
            out.append(grid[r][c]); r += 1; c -= 1
        yield "".join(out)
    for c0 in range(W - 2, -1, -1):
        r, c = 0, c0
        out = []
        while r < H and c >= 0:
            out.append(grid[r][c]); r += 1; c -= 1
        yield "".join(out)

def reference_total(grid, word="rotator"):
    """Reference counter used to set the perf expected_total."""
    if not grid or not word:
        return 0
    L = len(word)
    pat = re.compile(r"(?=" + re.escape(word) + r")")
    total = 0
    # rows
    for s in _all_rows(grid):
        total += _count_overlaps(s, pat)
        total += _count_overlaps(s[::-1], pat)
    # cols
    for s in _all_cols(grid):
        total += _count_overlaps(s, pat)
        total += _count_overlaps(s[::-1], pat)
    # diagonals
    for s in _all_diagonals_SE(grid):
        if len(s) >= L:
            total += _count_overlaps(s, pat)
            total += _count_overlaps(s[::-1], pat)
    for s in _all_diagonals_SW(grid):
        if len(s) >= L:
            total += _count_overlaps(s, pat)
            total += _count_overlaps(s[::-1], pat)
    return total


ROOT = Path(__file__).resolve().parent
TEST_DIR = ROOT / "tests"
LEADERBOARD = ROOT / "leaderboard.json"
DEFAULT_SOLVER = ROOT / "private_solutions" / "rotator_finder.py"
DEFAULT_CMD = f"python3 {shlex.quote(str(DEFAULT_SOLVER))}"

# ----------------------------
# Test fixtures (small grids)
# ----------------------------

SMALL_TESTS = [
    {
        "name": "sample_multidir",
        "points": 20,
        "grid": [
            "rotatorxxr",
            "xxxxxxxxxo",
            "xxxxxxxxxt",
            "xxrxxxrxxa",
            "xxxoxoxxxt",
            "xxxxtxxxxo",
            "xxxaxaxxxr",
            "xxtxxxtxxx",
            "xoxxxxxoxx",
            "rxxxxxxxrx",
        ],
        "expected_total": 8,
    },
    {
        "name": "no_hits",
        "points": 10,
        "grid": ["xxxxxxxxxx"] * 10,
        "expected_total": 0,
    },
    {
        "name": "single_horizontal_bidir",
        "points": 10,
        "grid": [
            "rotatorxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
        ],
        "expected_total": 2,
    },
    {
        "name": "vertical_mid",
        "points": 5,
        "grid": [
            "xxxxrxxxxx",
            "xxxxoxxxxx",
            "xxxxtxxxxx",
            "xxxxaxxxxx",
            "xxxxtxxxxx",
            "xxxxoxxxxx",
            "xxxxrxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
        ],
        "expected_total": 2,
    },
    {
        "name": "diag_cross",
        "points": 5,
        "grid": [
            "rxxxxxrxxx",
            "xoxxxoxxxx",
            "xxtxtxxxxx",
            "xxxaxxxxxx",
            "xxtxtxxxxx",
            "xoxxxoxxxx",
            "rxxxxxrxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
            "xxxxxxxxxx",
        ],
        "expected_total": 4,
    },
    {
        # heavy overlap in a 10x10 to test indexing logic
        "name": "overlap_corner",
        "points": 10,
        "grid": [
            "rotatorrot",
            "otatorrota",
            "tatorrotax",
            "atorrotaxx",
            "torrotaxxx",
            "orrotaxxxx",
            "rrotaxxxxx",
            "rotaxxxxxx",
            "otaxxxxxxx",
            "taxxxxxxxx",
        ],
        # This grid has "rotator" horizontally at (1,1)->(1,7) and (1,4)->(1,10) and many reverse/semi-overlaps.
        # To avoid solver disagreements on path-duplications, we only assert the total we computed deterministically:
        "expected_total": 4,
    },
]

# ----------------------------
# Performance grid generator
# ----------------------------

def make_perf_grid(N=1200, word="rotator", seed=1337):
    """
    Generate a large N x N grid with known-count placements of `word`.
    The grid is mostly 'x'. We plant the word (and its reverse) at a stride
    so expected total can be computed analytically.

    Directions planted:
      E/W every row multiple of row_stride, stepping col_stride across
      S/N every col multiple of col_stride, stepping row_stride down
      SE/NW every diag start at top row every diag_stride cols
      SW/NE every anti-diag start at top row every diag_stride cols

    We avoid overlaps counting problems by simply counting placements we plant.
    """
    random.seed(seed)
    L = len(word)
    grid = [["x"] * N for _ in range(N)]

    row_stride = 11
    col_stride = 13
    diag_stride = 17

    planted = 0

    # Horizontal (E and W)
    for r in range(0, N, row_stride):
        for c in range(0, N - L + 1, col_stride):
            for k, ch in enumerate(word):
                grid[r][c + k] = ch
            # also ensure reverse is automatically found by solver (W) — no need to plant again
            planted += 2  # E and W

    # Vertical (S and N)
    for c in range(0, N, col_stride):
        for r in range(0, N - L + 1, row_stride):
            for k, ch in enumerate(word):
                grid[r + k][c] = ch
            planted += 2  # S and N

    # Diagonal SE/NW from top row
    for c0 in range(0, N - L + 1, diag_stride):
        r, c = 0, c0
        while r + L <= N and c + L <= N:
            for k, ch in enumerate(word):
                grid[r + k][c + k] = ch
            planted += 2  # SE and NW
            r += row_stride
            c += col_stride

    # Diagonal SW/NE from top row
    for c0 in range(L - 1, N, diag_stride):
        r, c = 0, c0
        while r + L <= N and c - (L - 1) >= 0:
            for k, ch in enumerate(word):
                grid[r + k][c - k] = ch
            planted += 2  # SW and NE
            r += row_stride
            c -= col_stride

    # Finalize strings
    grid = ["".join(row) for row in grid]
    return grid, planted

# ----------------------------
# Test IO helpers
# ----------------------------

def ensure_tests():
    TEST_DIR.mkdir(exist_ok=True)
    # Write small fixed tests
    for t in SMALL_TESTS:
        p = TEST_DIR / f"{t['name']}.in"
        q = TEST_DIR / f"{t['name']}.out"
        if not p.exists():
            p.write_text("\n".join(t["grid"]) + "\n", encoding="utf-8")
        if not q.exists():
            q.write_text(str(t["expected_total"]).strip() + "\n", encoding="utf-8")

    # Write a pinned performance test (so runs are comparable across machines)
    perf_in = TEST_DIR / "perf_fixed.in"
    perf_meta = TEST_DIR / "perf_fixed.meta.json"
    if not perf_in.exists() or not perf_meta.exists():
        # build grid with deterministic planting
        grid, _planted_twice = make_perf_grid(N=1200)
        perf_in.write_text("\n".join(grid) + "\n", encoding="utf-8")

        # compute the *true* expected by scanning (handles palindrome + intersections)
        expected = reference_total(grid, word="rotator")

        perf_meta.write_text(
            json.dumps({"expected_total": expected, "N": 1200}, indent=2),
            encoding="utf-8"
        )

def run_solver(cmd, input_text, timeout=30):
    """Run solver command with given input_text. Return (returncode, stdout, stderr, runtime_s)."""
    start = time.perf_counter()
    try:
        p = subprocess.run(
            cmd,
            input=input_text.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        return -1, "", f"TIMEOUT after {timeout}s", timeout
    runtime = time.perf_counter() - start
    return p.returncode, p.stdout.decode("utf-8", errors="replace"), p.stderr.decode("utf-8", errors="replace"), runtime

def parse_total(stdout: str):
    """Return first non-empty line parsed as int; None if invalid."""
    for line in stdout.splitlines():
        s = line.strip()
        if not s:
            continue
        try:
            return int(s)
        except ValueError:
            return None
    return None

def perf_score(ms: int) -> int:
    if ms <= 50:  return 40
    if ms <= 100:  return 35
    if ms <= 250:  return 28
    if ms <= 750:  return 18
    return 0

def load_leaderboard():
    if LEADERBOARD.exists():
        try:
            return json.loads(LEADERBOARD.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []

def save_leaderboard(entries):
    # Sort: score desc, then perf_ms asc
    entries_sorted = sorted(entries, key=lambda e: (-e["total_score"], e.get("perf_ms", 9_999_999)))
    LEADERBOARD.write_text(json.dumps(entries_sorted, indent=2), encoding="utf-8")
    return entries_sorted

def print_table(rows, headers):
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    fmt = " | ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print("-+-".join("-" * w for w in widths))
    for r in rows:
        print(fmt.format(*r))

# ----------------------------
# Main grading flow
# ----------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cmd", default=DEFAULT_CMD, help="Command to run solver")
    ap.add_argument("--name", default=os.getenv("USER") or "anonymous", help="Name for leaderboard")
    ap.add_argument("--list", action="store_true", help="Show current leaderboard and exit")
    args = ap.parse_args()

    if args.list:
        lb = load_leaderboard()
        if not lb:
            print("No leaderboard entries yet.")
            return
        rows = []
        for i, e in enumerate(lb, 1):
            rows.append([i, e["name"], e["total_score"], e["correctness"], e["perf_score"], f'{e.get("perf_ms", "-")} ms', e["cmd"]])
        print_table(rows, ["#", "Name", "Total", "Correct", "Perf", "Perf(ms)", "Cmd"])
        return

    ensure_tests()

    # Correctness
    correctness_points = 0
    details = []
    for t in SMALL_TESTS:
        rc, out, err, rt = run_solver(args.cmd, "\n".join(t["grid"]) + "\n", timeout=10)
        got = parse_total(out)
        ok = (rc == 0 and got == t["expected_total"])
        if ok:
            correctness_points += t["points"]
        details.append({
            "test": t["name"], "ok": ok, "expected": t["expected_total"], "got": got,
            "rt_ms": int(rt * 1000), "stderr": err.strip()[:200]
        })

    # Performance
    perf_in = (TEST_DIR / "perf_fixed.in").read_text(encoding="utf-8")
    perf_meta = json.loads((TEST_DIR / "perf_fixed.meta.json").read_text(encoding="utf-8"))
    rc, out, err, rt = run_solver(args.cmd, perf_in, timeout=60)
    got = parse_total(out)
    perf_ok = (rc == 0 and got == perf_meta["expected_total"])
    perf_ms = int(rt * 1000)
    perf_pts = perf_score(perf_ms) if perf_ok else 0

    total_score = correctness_points + perf_pts

    # Report
    print("\n=== WordMaze Grader Report ===")
    print(f"Solver cmd : {args.cmd}")
    print(f"Participant: {args.name}")
    print("\nCorrectness results:")
    rows = []
    for d in details:
        rows.append([d["test"], "OK" if d["ok"] else "FAIL", d["expected"], d["got"], d["rt_ms"]])
    print_table(rows, ["Test", "Result", "Expected", "Got", "Time(ms)"])
    print(f"\nCorrectness points: {correctness_points}/60")

    print("\nPerformance result:")
    print_table([[perf_meta["N"], perf_ok, perf_meta["expected_total"], got, perf_ms, perf_pts]],
                ["N", "Correct", "Expected", "Got", "Time(ms)", "Perf points"])
    print(f"\nTOTAL SCORE: {total_score}/100")

    # Update leaderboard
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "name": args.name,
        "cmd": args.cmd,
        "correctness": correctness_points,
        "perf_score": perf_pts,
        "perf_ms": perf_ms,
        "total_score": total_score,
        "version": 1,
    }
    lb = load_leaderboard()
    lb.append(entry)
    lb = save_leaderboard(lb)

    print("\nLeaderboard (top 10):")
    rows = []
    for i, e in enumerate(lb[:10], 1):
        rows.append([i, e["name"], e["total_score"], e["correctness"], e["perf_score"], f'{e["perf_ms"]} ms'])
    print_table(rows, ["#", "Name", "Total", "Correct", "Perf", "Perf(ms)"])

if __name__ == "__main__":
    main()
