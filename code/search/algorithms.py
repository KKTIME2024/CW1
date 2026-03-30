from __future__ import annotations

"""
搜索算法实现
实现目标：
- 统一的函数签名，便于在 CLI / 实验脚本里切换算法
- 统一统计指标：nodes_expanded / time_ms / path_cost / path_len / max_frontier

注意：
- 本实现把每个动作的 step_cost 直接累加到 Node.g 中，因此 SearchResult.path_cost = 终点节点的 g 值。
- BFS 这里按“队列层次”展开，语义上更接近“最少动作数”；但我们仍然会记录真实 path_cost（按 step_cost 累加）。
"""

import heapq
import random
import time
from collections import deque
from typing import Any

from .common import Node, Problem, SearchResult


def bfs(
    *,
    problem: Problem,
    case: str,
    max_nodes: int,
    loop_check: bool,
    seed: int = 0,
) -> SearchResult:
    # Breadth-First Search：按“先入先出队列”逐层扩展
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


def dfs(
    *,
    problem: Problem,
    case: str,
    max_nodes: int,
    loop_check: bool,
    seed: int,
    randomized: bool,
) -> SearchResult:
    # Depth-First Search：用栈（后进先出）深入搜索；可选固定顺序 or 随机顺序
    start_t = time.perf_counter()
    heur_name = getattr(problem, "heuristic_name", "n/a")
    rng = random.Random(seed)
    start = problem.initial_state()
    start_key = problem.state_key(start)

    stack: list[Node] = [Node(state=start, parent=None, action=None, g=0.0, h=0.0)]
    visited: set[Any] = {start_key} if loop_check else set()
    nodes_expanded = 0
    max_frontier = 1

    while stack:
        max_frontier = max(max_frontier, len(stack))
        node = stack.pop()
        if problem.is_goal(node.state):
            actions = node.iter_actions()
            end_t = time.perf_counter()
            return SearchResult(
                algorithm="dfs_random" if randomized else "dfs_fixed",
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

        succ = list(problem.successors(node.state))
        if randomized:
            # 随机化动作顺序：用于对比 DFS 的不稳定性（不同 seed 可能走出不同路径）
            rng.shuffle(succ)
        # DFS: push in reverse so the first successor is explored first.
        for action, nxt, step_cost in reversed(succ):
            k = problem.state_key(nxt)
            if loop_check and k in visited:
                continue
            if loop_check:
                visited.add(k)
            stack.append(Node(state=nxt, parent=node, action=action, g=node.g + float(step_cost), h=0.0))

    end_t = time.perf_counter()
    return SearchResult(
        algorithm="dfs_random" if randomized else "dfs_fixed",
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


def best_first(
    *,
    problem: Problem,
    case: str,
    max_nodes: int,
    loop_check: bool,
    seed: int = 0,
) -> SearchResult:
    # Best-First Search（贪心）：每次优先扩展 h(n) 最小的节点（忽略 g(n)）
    start_t = time.perf_counter()
    heur_name = getattr(problem, "heuristic_name", "n/a")
    start = problem.initial_state()
    start_node = Node(state=start, parent=None, action=None, g=0.0, h=problem.heuristic(start))

    heap: list[tuple[float, int, Node]] = []
    tie = 0
    heapq.heappush(heap, (start_node.h, tie, start_node))
    tie += 1

    visited: set[Any] = {problem.state_key(start)} if loop_check else set()
    nodes_expanded = 0
    max_frontier = 1

    while heap:
        max_frontier = max(max_frontier, len(heap))
        _prio, _t, node = heapq.heappop(heap)
        if problem.is_goal(node.state):
            actions = node.iter_actions()
            end_t = time.perf_counter()
            return SearchResult(
                algorithm="best_first",
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

        for action, nxt, step in problem.successors(node.state):
            k = problem.state_key(nxt)
            if loop_check and k in visited:
                continue
            if loop_check:
                visited.add(k)
            nxt_node = Node(
                state=nxt,
                parent=node,
                action=action,
                g=node.g + float(step),
                h=problem.heuristic(nxt),
            )
            heapq.heappush(heap, (nxt_node.h, tie, nxt_node))
            tie += 1

    end_t = time.perf_counter()
    return SearchResult(
        algorithm="best_first",
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


def astar(
    *,
    problem: Problem,
    case: str,
    max_nodes: int,
    loop_check: bool,
    seed: int = 0,
) -> SearchResult:
    # A*：优先扩展 f(n)=g(n)+h(n) 最小的节点；用 best_g 做“代价层面的 loop checking”
    start_t = time.perf_counter()
    heur_name = getattr(problem, "heuristic_name", "n/a")
    start = problem.initial_state()
    start_key = problem.state_key(start)
    start_node = Node(state=start, parent=None, action=None, g=0.0, h=problem.heuristic(start))

    heap: list[tuple[float, int, Node]] = []
    tie = 0
    heapq.heappush(heap, (start_node.f, tie, start_node))
    tie += 1

    best_g: dict[Any, float] = {start_key: 0.0} if loop_check else {}
    nodes_expanded = 0
    max_frontier = 1

    while heap:
        max_frontier = max(max_frontier, len(heap))
        _prio, _t, node = heapq.heappop(heap)
        k = problem.state_key(node.state)
        if loop_check and node.g != best_g.get(k, node.g):
            # Stale queue entry.
            continue

        if problem.is_goal(node.state):
            actions = node.iter_actions()
            end_t = time.perf_counter()
            return SearchResult(
                algorithm="astar",
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

        for action, nxt, step in problem.successors(node.state):
            step = float(step)
            nxt_g = node.g + step
            nxt_k = problem.state_key(nxt)
            if loop_check:
                prev = best_g.get(nxt_k)
                if prev is not None and nxt_g >= prev:
                    continue
                best_g[nxt_k] = nxt_g
            nxt_node = Node(state=nxt, parent=node, action=action, g=nxt_g, h=problem.heuristic(nxt))
            heapq.heappush(heap, (nxt_node.f, tie, nxt_node))
            tie += 1

    end_t = time.perf_counter()
    return SearchResult(
        algorithm="astar",
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
