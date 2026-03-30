# COMP2611 CW1 - Robot Worker Code

This folder contains a small, self-contained Python framework to run multiple search algorithms against the
ISS robot worker planning problem (Part B).

## Quick start

Run one algorithm on one case:

```bash
python3 code/main.py run --case easy --algo astar --heuristic waypoints
```

Run the standard experiment matrix and print a markdown table summary (includes mean/std for `dfs_random`):

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
- `astar` uses `f(n)=g(n)+h(n)` (optimality depends on the chosen heuristic being admissible/consistent).
- Heuristic choices are in `code/B_OVERVIEW.md`.
