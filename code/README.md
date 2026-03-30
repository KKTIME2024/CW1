# COMP2611 CW1 - Robot Worker Code

This folder contains a small, self-contained Python framework to run multiple search algorithms against the
ISS robot worker planning problem (Part B).

## Quick start

Run one algorithm on one case:

```bash
python3 code/main.py run --case easy --algo astar
```

Run the standard experiment matrix (cases x algos) and print a markdown table:

```bash
python3 code/main.py experiment
```

Save results to CSV:

```bash
python3 code/main.py experiment --csv out.csv
```

## Notes

- `bfs` is breadth-first by depth (optimizes number of actions, not weighted move cost).
- `best_first` uses only `h(n)` (greedy).
- `astar` uses `f(n)=g(n)+h(n)` with a consistent heuristic, so it is optimal w.r.t. the defined move costs.

