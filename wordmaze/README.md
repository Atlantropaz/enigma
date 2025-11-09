## WordMaze: Find Every `rotator`

Contestants are given a rectangular grid of lowercase letters and must count how many times the palindrome `rotator` appears in **all eight compass directions**. The grader in this folder compiles the official score used on the leaderboard.

### Problem Recap
- Read **N lines** of equal length from `stdin` (no spaces).
- Count overlapping matches of `rotator` in these 8 directions: `N, NE, E, SE, S, SW, W, NW`.
- Output **only the total count** on the first line. (If you want to print coordinates for debugging, do so afterward—the grader ignores extra lines.)

#### Sample (10×10)
```
rotatorxxr
xxxxxxxxxo
xxxxxxxxxt
xxrxxxrxxa
xxxoxoxxxt
xxxxtxxxxo
xxxaxaxxxr
xxtxxxtxxx
xoxxxxxoxx
rxxxxxxxrx
```
Expected total: `8` (four lines × both directions).

### Running the Grader
From `wordmaze/`:
```bash
python3 grader.py --name "your-handle"
```
- `--cmd` lets you override the solver command (default points to `python3 private_solutions/rotator_finder.py`).
- `--list` prints the current leaderboard.
- The grader writes/refreshes all `.in/.out` fixtures under `tests/` automatically.

### Evaluation Pipeline
1. **Correctness suite (60 pts total)**  
   Each test streams a 10×10 grid to your solver and compares the reported count:
   | Test name               | Focus                            | Points |
   |-------------------------|----------------------------------|--------|
   | `sample_multidir`       | Mixed rows/cols/diagonals        | 20     |
   | `no_hits`               | Properly returning zero          | 10     |
   | `single_horizontal_bidir` | Horizontal in both directions | 10     |
   | `vertical_mid`          | Straight vertical palindrome     | 5      |
   | `diag_cross`            | Intersecting diagonals           | 5      |
   | `overlap_corner`        | Dense overlaps near an edge      | 10     |

2. **Performance test (40 pts max)**  
   - Input: a deterministic **1200×1200** grid containing 49,058 planted matches.  
   - Your solver must emit `49058` to earn perf credit.  
   - Points depend on runtime:
     - ≤ 50 ms → 40 pts  
     - ≤ 100 ms → 35 pts  
     - ≤ 250 ms → 28 pts  
     - ≤ 750 ms → 18 pts  
     - \> 750 ms or wrong answer → 0 pts

3. **Leaderboard update**  
   Submitting via `grader.py` appends your `(name, scores, perf time, command)` entry to `leaderboard.json` sorted by total score (ties broken by faster perf).

### Tips for Contestants
- Don’t hardcode a 10×10 assumption—the performance grid is huge.
- Because `rotator` is a palindrome, each line contributes twice (forward/backward). Be careful not to double-count unless you intend to.
- Keep extra debugging prints off `stdout`’s first line; instead, write them to `stderr` or after the total.
- You can drop experimental solvers under `private_solutions/` (already `.gitignore`d) and point `--cmd` at whichever one you want to benchmark.

### Submitting to the Leaderboard
1. Run the grader with your preferred command and name:
   ```bash
   python3 grader.py --cmd "python3 my_solver.py" --name "your-handle"
   ```
2. Confirm the report shows the score and that `leaderboard.json` contains your entry.
3. Commit your solver (if you want it reviewed) plus the updated `leaderboard.json`.
4. Open a pull request describing your approach and paste the grader output.  
   Maintainers will re-run `python3 grader.py --name "your-handle"` to verify before merging.

Good luck, and may every `rotator` be found!
