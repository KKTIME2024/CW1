COMP2611 Coursework 1 - Part B (Robot Worker Experimentation)

**Executive Summary**
This report presents a comprehensive investigation of search algorithms applied to an International Space Station (ISS) robot maintenance task. The scenario involves a robot that must replace an air filter in the US_Lab module while adhering to constraints including single-object carrying, US_Lab access requirements, and asymmetric movement costs. Five search algorithms (BFS, DFS-fixed, DFS-random, best-first, A*) were evaluated across three difficulty levels with four different heuristics. Key findings show that A* with the waypoints heuristic provides optimal solutions with efficient search, while best-first offers faster but suboptimal solutions. DFS algorithms, though requiring fewer node expansions, produce significantly longer paths.

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

**Experimental Setup**
Algorithms tested:
- BFS (Breadth-First Search)
- DFS with fixed action order (DFS-Fixed)
- DFS with randomized action order (DFS-Random)
- Best-first search (greedy heuristic search)
- A* search (optimal heuristic search)

**Common experimental parameters:**
- Loop checking: Enabled (prevents revisiting states)
- Maximum nodes: 10,000 (search termination limit)
- Randomized DFS: 5 random seeds (results show mean ± standard deviation)
- All algorithms: Implemented with consistent cost accumulation
- Environment: Python 3.x on standard hardware

**Performance metrics collected:**
- Nodes expanded: Number of states explored
- Time (ms): Execution time in milliseconds
- Path cost: Total movement cost of solution
- Success: Whether a solution was found within node limit

**Visualization**
The following charts provide visual summaries of the experimental results:
1. **Figure 1**: Nodes expanded comparison across algorithms and cases
2. **Figure 2**: Path cost comparison with optimal cost reference line
3. **Figure 3**: Heuristic effectiveness for A* search

Test cases


Easy
- Base map as defined above.
- All objects start in Storage_PMM, robot at Node_3.

Medium
- Same map, but start robot at Airlock and place toolbox at US_Lab.
- Highlights the US_Lab access constraint and asymmetric cost.

Hard
- Same map, start robot at Airlock, toolbox at Storage_PMM.
- Requires robot to travel from Airlock to Storage_PMM to get toolbox, then to US_Lab.
- Tests longer planning with multiple constraints.

Results table template (fill with measured data)

Case: Easy
| Algorithm | Heuristic | Nodes Expanded | Time (ms) | Path Cost | Success |
|-----------|-----------|----------------|-----------|-----------|---------|
| BFS       | None      | 141            | 0         | 15        | Yes     |
| DFS-Fixed | None      | 48             | 0         | 21        | Yes     |
| DFS-Rand  | None      | 52 ± 7.8       | 0         | 19.8 ± 4.5 | Yes    |
| BestFirst | waypoints | 79             | 0         | 21        | Yes     |
| BestFirst | goal      | 116            | 0         | 15        | Yes     |
| BestFirst | next      | 122            | 0         | 15        | Yes     |
| BestFirst | zero      | 141            | 0         | 15        | Yes     |
| A*        | waypoints | 103            | 0         | 15        | Yes     |
| A*        | goal      | 123            | 0         | 15        | Yes     |
| A*        | next      | 116            | 0         | 15        | Yes     |
| A*        | zero      | 132            | 0         | 15        | Yes     |

Case: Medium
| Algorithm | Heuristic | Nodes Expanded | Time (ms) | Path Cost | Success |
|-----------|-----------|----------------|-----------|-----------|---------|
| BFS       | None      | 144            | 0         | 14        | Yes     |
| DFS-Fixed | None      | 63             | 0         | 36        | Yes     |
| DFS-Rand  | None      | 44.6 ± 12.9    | 0         | 19.6 ± 5.0 | Yes    |
| BestFirst | waypoints | 76             | 0         | 20        | Yes     |
| BestFirst | goal      | 118            | 0         | 14        | Yes     |
| BestFirst | next      | 120            | 0         | 14        | Yes     |
| BestFirst | zero      | 144            | 0         | 14        | Yes     |
| A*        | waypoints | 100            | 0         | 14        | Yes     |
| A*        | goal      | 127            | 0         | 14        | Yes     |
| A*        | next      | 121            | 0         | 14        | Yes     |
| A*        | zero      | 135            | 0         | 14        | Yes     |

Case: Hard
| Algorithm | Heuristic | Nodes Expanded | Time (ms) | Path Cost | Success |
|-----------|-----------|----------------|-----------|-----------|---------|
| BFS       | None      | 141            | 0         | 18        | Yes     |
| DFS-Fixed | None      | 50             | 0         | 24        | Yes     |
| DFS-Rand  | None      | 54 ± 5.4       | 0         | 22.8 ± 4.5 | Yes    |
| BestFirst | waypoints | 81             | 0         | 24        | Yes     |
| BestFirst | goal      | 117            | 0         | 18        | Yes     |
| BestFirst | next      | 123            | 0         | 18        | Yes     |
| BestFirst | zero      | 141            | 0         | 18        | Yes     |
| A*        | waypoints | 103            | 0         | 18        | Yes     |
| A*        | goal      | 123            | 0         | 18        | Yes     |
| A*        | next      | 116            | 0         | 18        | Yes     |
| A*        | zero      | 132            | 0         | 18        | Yes     |

B4. Key Findings

Based on the experimental results, the following key observations can be made:

**Algorithm Performance Comparison**
- **A* vs BFS**: A* with waypoints heuristic consistently found optimal paths (same cost as BFS) while expanding significantly fewer nodes (103 vs 141 in Easy case, 100 vs 144 in Medium, 103 vs 141 in Hard).
- **Best-first vs A***: Best-first with waypoints heuristic expanded the fewest nodes (79 in Easy, 76 in Medium, 81 in Hard) but often found suboptimal paths (higher path costs: 21 vs 15 in Easy, 20 vs 14 in Medium, 24 vs 18 in Hard).
- **DFS Performance**: DFS algorithms expanded the fewest nodes overall (48-63 for fixed, 45-54 for random) but found significantly longer paths, demonstrating their non-optimal nature.

**Heuristic Effectiveness**
- **Waypoints heuristic**: Most effective for both A* and best-first, providing the best balance between node expansion reduction and path optimality.
- **Goal heuristic**: Performed well for A* (optimal paths) but required more node expansions than waypoints.
- **Next heuristic**: Similar performance to goal heuristic but slightly better for A* in some cases.
- **Zero heuristic**: Equivalent to uniform-cost search for A*, performing worse than informed heuristics.

**Search Difficulty Analysis**
- **Medium case**: Most challenging for BFS (144 nodes expanded) due to the robot starting at Airlock with toolbox at US_Lab, requiring careful planning around the access constraint.
- **Hard case**: Required longest optimal paths (cost 18) but had similar node expansion counts to Easy case, suggesting the problem structure remained manageable.
- **DFS variability**: Randomized DFS showed significant standard deviation in path costs (4.5-5.0) and nodes expanded (5.4-12.9), highlighting its unpredictability.

**Constraint Impact**
- **Single-carry constraint**: Increased search complexity by limiting action choices, particularly affecting DFS which often found longer detour paths.
- **US_Lab access constraint**: Created critical decision points in the search space, especially evident in Medium case where the robot needed to retrieve the toolbox before entering US_Lab.
- **Asymmetric cost**: The Node_2 ↔ Airlock cost of 2 influenced optimal path planning, with algorithms correctly avoiding unnecessary traversals of this expensive edge.

**Practical Implications**
- For this ISS maintenance task, A* with waypoints heuristic provides the best trade-off: guaranteed optimality with efficient search.
- Best-first search can be useful when computational resources are limited and near-optimal solutions are acceptable.
- DFS should be avoided for critical path planning tasks due to its non-optimal and unpredictable nature.

**Conclusion**
This investigation successfully demonstrated the application of various search algorithms to a realistic ISS robot maintenance scenario. The waypoints heuristic proved to be both admissible and effective, significantly reducing search effort while maintaining optimality in A* search. The constraints introduced (single-carry, access requirements, asymmetric costs) created a search problem with meaningful complexity that highlighted the strengths and weaknesses of different algorithmic approaches. The results provide practical guidance for selecting appropriate search strategies for similar robotic planning tasks in constrained environments.
