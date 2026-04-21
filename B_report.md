

## B.1. My Robot Scenario: ISS Maintenance Task

**Scenario Overview**
This scenario models a robotic maintenance task on the ISS. The robot must retrieve a toolbox and a new filter, perform a replacement in the lab, and return all items to storage before ending at the Observatory.

The core challenge lies in the interaction between **sequential task constraints** and a **tree-structured spatial topology**. Unlike standard pathfinding problems, this scenario introduces interleaved symbolic (task dependency) and geometric (navigation) constraints, making naive shortest-path heuristics insufficient.

**Environment Layout (Rooms & Connectivity)**

* **Storage_PMM**: stores toolbox and new filter
* **US_Lab**: maintenance location
* **Node_2 & Node_3**: transit hubs
* **Observatory**: final goal location
* **Airlock**: leaf node

All connections are bidirectional. All edge costs are 1.0 except `Node_2 ↔ Airlock`, which is 2.0.

**Objects and Constraints**

* Items: Toolbox, New Filter, Old Filter
* Capacity: only one item can be carried at a time
* Preconditions:

  * Old filter can only be removed in `US_Lab` with toolbox
  * New filter can only be installed if toolbox is in `US_Lab`

**Robot Actions**
Move, Pick, Drop, Remove_Old_Filter, Install_New_Filter

**Goal State**
New filter installed, both toolbox and old filter returned to storage, and robot ends at Observatory.

---

## B.2. Heuristic(s): The "Waypoints" Logic

To guide search under strong task dependencies, we design a **Waypoints heuristic** that encodes the required execution order.

**Definition**
Let the remaining task be represented as an ordered waypoint sequence:

[
W(n) = [w_1, w_2, ..., w_k]
]

The heuristic is defined as:

[
h(n) = dist(pos(n), w_1) + \sum_{i=1}^{k-1} dist(w_i, w_{i+1})
]

where distances are precomputed using shortest paths.

**Interpretation**
Instead of estimating distance to the final goal only, the heuristic approximates the cost of completing all remaining subgoals in order. This effectively embeds **task structure into spatial estimation**.

**Comparison with Goal-only Heuristic**

* Goal-only: spatially aware, but ignores task sequence
* Waypoints: encodes both spatial distance and task progression

Thus, Goal-only heuristics are **spatially aware but temporally blind**, while Waypoints incorporate both dimensions.

**Admissibility**
The heuristic is admissible because it ignores action costs (pick/drop, etc.) and assumes unobstructed movement. Since all omitted costs are non-negative, it remains a lower bound on the true cost.

---

## B.3. Results

We evaluated A*, BFS, DFS, and Greedy Best-First across Easy, Medium, and Hard settings.

| Algorithm      | Heuristic     | Case | Nodes Expanded | Path Cost |
| :------------- | :------------ | :--- | :------------- | :-------- |
| **A***         | **Waypoints** | Hard | **103**        | **18.0**  |
| **A***         | Goal-only     | Hard | 123            | 18.0      |
| **BFS**        | N/A           | Hard | 141            | 18.0      |
| **Best-First** | Waypoints     | Hard | **81**         | 24.0      |
| **DFS_Fixed**  | N/A           | Hard | 50             | 24.0      |

**Efficiency**
A* with Waypoints reduces node expansions by ~27% compared to BFS (103 vs 141) while maintaining optimal cost. This shows that incorporating task structure significantly improves pruning effectiveness.

**Optimality**
A* consistently finds optimal solutions across all heuristics. In contrast, Greedy Best-First produces suboptimal paths when combined with Waypoints (e.g., 24 vs optimal 18), despite expanding fewer nodes.

Importantly, Greedy with simpler heuristics (Goal / Zero) still finds optimal solutions in this domain. This indicates that suboptimality is not inherent to Greedy itself, but arises from the interaction with the heuristic.

**Interpretation**
For Greedy Best-First, the heuristic does not merely estimate cost—it effectively determines the search policy. The Waypoints heuristic enforces a fixed task sequence, which reduces exploration but may deviate from the true cost-optimal ordering.

---

## B.4. Key Findings

**1. BFS and A* Cost Equivalence in Tree Structures**
BFS consistently finds solutions with the same cost as A*. This follows from two properties:

* The environment is a tree: there is exactly one simple path between any two states
* All relevant edges have uniform cost

Under these conditions, minimizing steps (BFS) is equivalent to minimizing path cost (A*).

---

**2. Heuristics Must Encode Task Structure**
The Waypoints heuristic demonstrates that effective heuristics in this domain must capture **task progression**, not just spatial proximity. By incorporating subgoal ordering, A* avoids exploring invalid or premature action sequences.

---

**3. Heuristic Sensitivity Across Algorithms**
The same heuristic can have fundamentally different effects depending on the search algorithm:

* In A*, Waypoints improves efficiency while preserving optimality
* In Greedy Best-First, it acts as a **policy constraint**, not just an estimator

As a result, Greedy becomes highly sensitive to heuristic design.

---

**4. Robustness vs. Bias Correction**
A* is robust to heuristic bias due to the corrective role of path cost ( g(n) ). In contrast, Greedy Best-First lacks this correction mechanism and fully commits to the heuristic.

This explains why Waypoints improves A* but can degrade Greedy performance:
the issue is not misleading local minima, but **over-constraining the search trajectory**.

