# Part B Code Overview (Robot Worker)

This folder contains a small Python runner for COMP2611 CW1 Part B (robot worker task planning).

## How To Run

Run a single algorithm on a single case:

```bash
python3 code/main.py run --case easy --algo astar --heuristic waypoints
```

Run an experiment matrix and print a summary table (mean/std is shown for randomized DFS):

```bash
python3 code/main.py experiment --seeds 10
```

Write the summary table to CSV:

```bash
python3 code/main.py experiment --seeds 10 --csv summary.csv
```

## Search Algorithms Implemented

Defined in `code/search/algorithms.py` and selectable via `--algo`:

- `bfs`: breadth-first by depth (min number of actions, not guaranteed min cost with weighted moves)
- `dfs_fixed`: depth-first with fixed successor ordering
- `dfs_random`: depth-first with randomized successor ordering (controlled by `--seed`; in experiments we repeat many seeds)
- `best_first`: greedy best-first using only `h(n)`
- `astar`: A* using `f(n)=g(n)+h(n)` and a `best_g` table when loop checking is enabled

Loop checking can be disabled with `--no-loop-check` (mainly for experimentation).

## Heuristics Implemented

Heuristics are defined in `code/search/problems/iss_robot.py` and selectable via `--heuristic`:

- `waypoints`: sum of shortest-path distances through an ordered "remaining waypoint" list
- `next`: shortest-path distance to the next waypoint only (weaker than `waypoints`)
- `goal`: shortest-path distance to the final goal room (Observatory) only (usually very weak)
- `zero`: always 0 (A* becomes uniform-cost search)

Note: Heuristics are only used by `best_first` and `astar`. For BFS/DFS we report heuristic as `n/a` in the experiment summary.

## Robot Worker Problem (ISS Scenario)

Map and costs:
- Rooms: `Storage_PMM`, `Node_3`, `Node_2`, `US_Lab`, `Airlock`, `Observatory`
- Adjacency is defined in `base_iss_map()`
- Move cost is defined in `base_move_cost()` (only `Node_2 <-> Airlock` costs 2; others cost 1)

State (ISSState):
- `robot_loc`
- `new_filter_loc`, `old_filter_loc`, `toolbox_loc` in `{room_id, "carried"}`
- `old_filter_removed`, `new_filter_installed`

Actions (generated in `ISSRobotProblem.successors()`):
- `Move(room)` with move cost
- `Pick(obj)` / `Drop(obj)` with cost 0, with extra constraints below
- `Remove_Old_Filter` (only in `US_Lab`, requires toolbox present)
- `Install_New_Filter` (only in `US_Lab`, requires toolbox present, old removed, and new filter carried)

Constraints added to reduce branching and keep focus on routing:
- Single-carry: at most one of the three objects is `"carried"` at a time
- Pick/Drop only in specified rooms:
  - `toolbox`: Pick/Drop only in `Storage_PMM` or `US_Lab`
  - `new_filter`: Pick/Drop only in `Storage_PMM` (installed via `Install_New_Filter`)
  - `old_filter`: Pick only in `US_Lab` (after removal), Drop only in `Storage_PMM`
- Goal additionally requires the old filter to be returned: `old_filter_loc == "Storage_PMM"`

## Experiment Output (mean/std)

`python3 code/main.py experiment` prints one row per (case, algorithm, heuristic) group:
- Deterministic algorithms have `runs=1` and std=0.
- `dfs_random` has `runs = --seeds` and we report mean/std across those runs.

Std is computed as population standard deviation (ddof=0).

