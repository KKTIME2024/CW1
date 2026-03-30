from __future__ import annotations

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
    start_t = time.perf_counter()
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
    start_t = time.perf_counter()
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
    start_t = time.perf_counter()
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
    start_t = time.perf_counter()
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
        case=case,
        success=False,
        nodes_expanded=nodes_expanded,
        time_ms=int((end_t - start_t) * 1000),
        path_cost=float("inf"),
        path_len=0,
        max_frontier=max_frontier,
        action_path=[],
    )
