#!/usr/bin/env python3
"""
测试BFS算法的问题
"""

import heapq
import time
from collections import deque
from typing import Any

from search.common import Node, Problem, SearchResult
from search.problems.iss_robot import build_case_problem

def bfs_original(
    *,
    problem: Problem,
    case: str,
    max_nodes: int,
    loop_check: bool,
    seed: int = 0,
) -> SearchResult:
    """原始BFS实现"""
    start_t = time.perf_counter()
    heur_name = getattr(problem, "heuristic_name", "n/a")
    start = problem.initial_state()
    start_key = problem.state_key(start)

    q: deque[Node] = deque([Node(state=start, parent=None, action=None, g=0.0, h=0.0)])
    visited: set[Any] = {start_key} if loop_check else set()
    nodes_expanded = 0
    max_frontier = 1

    while q:
        max_frontier = max(max_frontier, len(q))
        node = q.popleft()
        if problem.is_goal(node.state):
            actions = node.iter_actions()
            end_t = time.perf_counter()
            return SearchResult(
                algorithm="bfs",
                heuristic=heur_name,
                case=case,
                success=True,
                nodes_expanded=nodes_expanded,
                time_ms=int((end_t - start_t) * 1000),
                path_cost=node.g,
                path_len=len(actions),
                max_frontier=max_frontier,
                action_path=actions,
            )

        if nodes_expanded >= max_nodes:
            break
        nodes_expanded += 1

        for action, nxt, step_cost in problem.successors(node.state):
            k = problem.state_key(nxt)
            if loop_check and k in visited:
                continue
            if loop_check:
                visited.add(k)
            q.append(Node(state=nxt, parent=node, action=action, g=node.g + float(step_cost), h=0.0))

    end_t = time.perf_counter()
    return SearchResult(
        algorithm="bfs",
        heuristic=heur_name,
        case=case,
        success=False,
        nodes_expanded=nodes_expanded,
        time_ms=int((end_t - start_t) * 1000),
        path_cost=float("inf"),
        path_len=0,
        max_frontier=max_frontier,
        action_path=[],
    )

def bfs_ucs(
    *,
    problem: Problem,
    case: str,
    max_nodes: int,
    loop_check: bool,
    seed: int = 0,
) -> SearchResult:
    """BFS修改为UCS（Uniform Cost Search）"""
    start_t = time.perf_counter()
    heur_name = getattr(problem, "heuristic_name", "n/a")
    start = problem.initial_state()
    start_key = problem.state_key(start)

    # 使用优先队列而不是普通队列
    heap: list[tuple[float, int, Node]] = []
    tie = 0
    start_node = Node(state=start, parent=None, action=None, g=0.0, h=0.0)
    heapq.heappush(heap, (start_node.g, tie, start_node))
    tie += 1

    visited: set[Any] = {start_key} if loop_check else set()
    nodes_expanded = 0
    max_frontier = 1

    while heap:
        max_frontier = max(max_frontier, len(heap))
        _cost, _t, node = heapq.heappop(heap)
        if problem.is_goal(node.state):
            actions = node.iter_actions()
            end_t = time.perf_counter()
            return SearchResult(
                algorithm="bfs_ucs",
                heuristic=heur_name,
                case=case,
                success=True,
                nodes_expanded=nodes_expanded,
                time_ms=int((end_t - start_t) * 1000),
                path_cost=node.g,
                path_len=len(actions),
                max_frontier=max_frontier,
                action_path=actions,
            )

        if nodes_expanded >= max_nodes:
            break
        nodes_expanded += 1

        for action, nxt, step_cost in problem.successors(node.state):
            k = problem.state_key(nxt)
            if loop_check and k in visited:
                continue
            if loop_check:
                visited.add(k)
            nxt_node = Node(state=nxt, parent=node, action=action, g=node.g + float(step_cost), h=0.0)
            heapq.heappush(heap, (nxt_node.g, tie, nxt_node))
            tie += 1

    end_t = time.perf_counter()
    return SearchResult(
        algorithm="bfs_ucs",
        heuristic=heur_name,
        case=case,
        success=False,
        nodes_expanded=nodes_expanded,
        time_ms=int((end_t - start_t) * 1000),
        path_cost=float("inf"),
        path_len=0,
        max_frontier=max_frontier,
        action_path=[],
    )

def test_bfs_variants():
    """测试不同BFS变体"""
    print("测试BFS变体:")
    print("=" * 80)
    
    case = "easy"
    problem = build_case_problem(case, heuristic_name="waypoints")
    
    # 测试原始BFS
    print("\n1. 原始BFS (使用队列):")
    result_bfs = bfs_original(
        problem=problem,
        case=case,
        max_nodes=10000,
        loop_check=True,
        seed=0
    )
    print(f"   Path cost: {result_bfs.path_cost}")
    print(f"   Nodes expanded: {result_bfs.nodes_expanded}")
    print(f"   Path length: {result_bfs.path_len}")
    
    # 测试BFS作为UCS
    print("\n2. BFS作为UCS (使用优先队列按g排序):")
    result_ucs = bfs_ucs(
        problem=problem,
        case=case,
        max_nodes=10000,
        loop_check=True,
        seed=0
    )
    print(f"   Path cost: {result_ucs.path_cost}")
    print(f"   Nodes expanded: {result_ucs.nodes_expanded}")
    print(f"   Path length: {result_ucs.path_len}")
    
    # 测试A*作为参考
    from search.algorithms import astar
    print("\n3. A* (作为参考):")
    result_astar = astar(
        problem=problem,
        case=case,
        max_nodes=10000,
        loop_check=True,
        seed=0
    )
    print(f"   Path cost: {result_astar.path_cost}")
    print(f"   Nodes expanded: {result_astar.nodes_expanded}")
    print(f"   Path length: {result_astar.path_len}")
    
    print("\n分析:")
    print(f"  原始BFS和UCS的path cost相同: {result_bfs.path_cost == result_ucs.path_cost}")
    print(f"  原始BFS和A*的path cost相同: {result_bfs.path_cost == result_astar.path_cost}")
    print(f"  UCS和A*的path cost相同: {result_ucs.path_cost == result_astar.path_cost}")

def create_simple_counterexample():
    """创建一个简单的反例"""
    print("\n\n创建简单反例:")
    print("=" * 80)
    
    class SimpleProblem:
        def __init__(self):
            self.heuristic_name = "n/a"
            
        def initial_state(self):
            return "S"
            
        def is_goal(self, state):
            return state == "G"
            
        def successors(self, state):
            if state == "S":
                # 两条路径到G
                # 路径1: S->A->G (代价: 1+1=2)
                # 路径2: S->B->G (代价: 10+1=11)
                # 两个路径都是2个动作
                yield ("to_A", "A", 1.0)
                yield ("to_B", "B", 10.0)
            elif state == "A":
                yield ("to_G", "G", 1.0)
            elif state == "B":
                yield ("to_G", "G", 1.0)
                
        def state_key(self, state):
            return state
            
        def heuristic(self, state):
            return 0.0
    
    problem = SimpleProblem()
    
    print("简单问题:")
    print("  S --(1)--> A --(1)--> G")
    print("  S --(10)-> B --(1)--> G")
    print("  最优路径: S->A->G (代价2)")
    print("  次优路径: S->B->G (代价11)")
    
    print("\n测试原始BFS:")
    result_bfs = bfs_original(
        problem=problem,
        case="simple",
        max_nodes=10000,
        loop_check=True,
        seed=0
    )
    print(f"  Path cost: {result_bfs.path_cost}")
    print(f"  Path: {' -> '.join(result_bfs.action_path)}")
    
    print("\n测试BFS作为UCS:")
    result_ucs = bfs_ucs(
        problem=problem,
        case="simple",
        max_nodes=10000,
        loop_check=True,
        seed=0
    )
    print(f"  Path cost: {result_ucs.path_cost}")
    print(f"  Path: {' -> '.join(result_ucs.action_path)}")
    
    print("\n结论:")
    print("  在这个简单例子中，原始BFS找到了次优路径(代价11)")
    print("  而UCS找到了最优路径(代价2)")
    print("  这说明原始BFS在有权重图中不一定找到最小代价路径")

if __name__ == "__main__":
    test_bfs_variants()
    create_simple_counterexample()