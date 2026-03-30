COMP2611 Coursework 1 - Part B (Robot Worker Experimentation)

B1. Scenario Design

Background
- An ISS maintenance robot must replace an air filter in the US_Lab module and finish at the Observatory.
- The robot operates in a small graph of connected modules with one special costed edge.

Map (rooms and connectivity)
Rooms: Storage_PMM, Node_3, Observatory, Node_2, US_Lab, Airlock
Adjacency (undirected):
- Storage_PMM <-> Node_3
- Node_3 <-> Observatory
- Node_3 <-> Node_2
- Node_2 <-> US_Lab
- Node_2 <-> Airlock

Move costs
- cost(Node_2, Airlock) = 2 (both directions)
- all other adjacent moves cost 1

State representation
State is a 6-tuple:
(robot_loc, new_filter_loc, old_filter_loc, toolbox_loc, old_filter_removed, new_filter_installed)

Domains
- robot_loc in {Storage_PMM, Node_3, Observatory, Node_2, US_Lab, Airlock}
- new_filter_loc in {Storage_PMM, US_Lab, carried}
- old_filter_loc in {US_Lab, Storage_PMM, carried}
- toolbox_loc in {Storage_PMM, US_Lab, carried}
- old_filter_removed in {True, False}
- new_filter_installed in {True, False}

Actions (preconditions -> effects)
1) Move(to)
- Pre: to is adjacent to robot_loc; cost = move_cost(robot_loc, to)
- Eff: robot_loc := to

2) Pick(obj)
- Pre: obj at robot_loc; robot not carrying any other object
- Eff: obj_loc := carried

3) Drop(obj)
- Pre: obj_loc == carried
- Eff: obj_loc := robot_loc

4) Remove_Old_Filter
- Pre: robot_loc == US_Lab; toolbox_loc == carried; old_filter_removed == False
- Eff: old_filter_removed := True; old_filter_loc := robot_loc

5) Install_New_Filter
- Pre: robot_loc == US_Lab; toolbox_loc == carried; new_filter_loc == carried; old_filter_removed == True
- Eff: new_filter_installed := True; new_filter_loc := US_Lab

Constraints / novelty
- Single-object carry: at most one object may be carried at a time.
- Access constraint: entering US_Lab requires carrying the toolbox.
- Asymmetric cost: Node_2 <-> Airlock has cost 2; all other moves cost 1.

Initial state
robot_loc = Node_3
new_filter_loc = Storage_PMM
old_filter_loc = US_Lab
toolbox_loc = Storage_PMM
old_filter_removed = False
new_filter_installed = False

Goal test
new_filter_installed == True
AND robot_loc == Observatory
AND toolbox_loc == Storage_PMM  (toolbox returned)

B2. Heuristic Design

Let d(x, y) be the shortest-path distance between rooms x and y using the move costs above.
We define an admissible heuristic by summing distances between remaining mandatory waypoints in the fixed task order.
This uses a relaxed problem (ignores the one-object carry and US_Lab access constraint), so it cannot overestimate.

Remaining waypoint list (ordered)
Given state s, build a list W as follows:
1) If old_filter_removed is False:
   - If toolbox_loc != carried, append toolbox_loc (Storage_PMM or US_Lab).
   - Append US_Lab.
2) Else if old_filter_loc != Storage_PMM:
   - Append Storage_PMM.
3) Else if new_filter_installed is False:
   - If new_filter_loc != carried, append new_filter_loc (Storage_PMM).
   - Append US_Lab.
4) Else if toolbox_loc != Storage_PMM:
   - Append Storage_PMM.
5) If robot_loc != Observatory, append Observatory.

Heuristic value
- If W is empty, h(s) = 0.
- Otherwise, h(s) = d(robot_loc, W[0]) + sum_{i=0..len(W)-2} d(W[i], W[i+1]).

Admissibility
- The waypoint list encodes the remaining required locations in the necessary task order.
- The heuristic ignores extra detours caused by carrying limits and access constraints.
- Therefore it underestimates the true remaining cost and is admissible.

Consistency (sketch)
- Each term uses shortest-path distances, which satisfy triangle inequality.
- Non-move actions occur at the current room, so removing a waypoint does not reduce h by more than the action cost.
- Move actions can change robot_loc by one edge, so h decreases by at most that move cost.
- Hence h is consistent.

B3. Experimental Results

Algorithms
- BFS
- DFS (fixed action order)
- DFS (randomized action order)
- Best-first (using h)
- A* (using h)

Common settings
- Loop checking enabled
- max_nodes = 10000
- Each case run 5 times (average nodes/time for randomized DFS)

Test cases
Easy
- Base map as defined above.
- All objects start in Storage_PMM, robot at Node_3.

Medium
- Same map, but start robot at Airlock and place toolbox at US_Lab.
- Highlights the US_Lab access constraint and asymmetric cost.

Hard
- Add one extra room (e.g., Columbus) connected to Node_2 to increase branching.
- Place new_filter in the extra room.

Results table template (fill with measured data)

Case: Easy
| Algorithm | Heuristic | Nodes Expanded | Time (ms) | Path Cost | Success |
|-----------|-----------|----------------|-----------|-----------|---------|
| BFS       | None      | TODO           | TODO      | TODO      | TODO    |
| DFS-Fixed | None      | TODO           | TODO      | TODO      | TODO    |
| DFS-Rand  | None      | TODO           | TODO      | TODO      | TODO    |
| BestFirst | h         | TODO           | TODO      | TODO      | TODO    |
| A*        | h         | TODO           | TODO      | TODO      | TODO    |

Case: Medium
| Algorithm | Heuristic | Nodes Expanded | Time (ms) | Path Cost | Success |
|-----------|-----------|----------------|-----------|-----------|---------|
| BFS       | None      | TODO           | TODO      | TODO      | TODO    |
| DFS-Fixed | None      | TODO           | TODO      | TODO      | TODO    |
| DFS-Rand  | None      | TODO           | TODO      | TODO      | TODO    |
| BestFirst | h         | TODO           | TODO      | TODO      | TODO    |
| A*        | h         | TODO           | TODO      | TODO      | TODO    |

Case: Hard
| Algorithm | Heuristic | Nodes Expanded | Time (ms) | Path Cost | Success |
|-----------|-----------|----------------|-----------|-----------|---------|
| BFS       | None      | TODO           | TODO      | TODO      | TODO    |
| DFS-Fixed | None      | TODO           | TODO      | TODO      | TODO    |
| DFS-Rand  | None      | TODO           | TODO      | TODO      | TODO    |
| BestFirst | h         | TODO           | TODO      | TODO      | TODO    |
| A*        | h         | TODO           | TODO      | TODO      | TODO    |

B4. Key Findings (replace with your measured findings)

- TODO: Compare optimality and node expansions between BFS and A* across cases.
- TODO: Note DFS (fixed/random) variability and any failures within max_nodes.
- TODO: Explain how the heuristic reduced expansions for best-first and A*.
- TODO: Relate increases in branching / constraints to search difficulty.
