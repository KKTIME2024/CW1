#!/usr/bin/env python3
"""
创建真正的BFS反例
"""

import heapq
import time
from collections import deque
from typing import Any

class SimpleProblem:
    def __init__(self):
        self.heuristic_name = "n/a"
        
    def initial_state(self):
        return "S"
        
    def is_goal(self, state):
        return state == "G"
        
    def successors(self, state):
        if state == "S":
            # 关键：让次优路径的动作数更少
            # 路径1: S->A->B->G (3个动作，代价: 1+1+1=3)
            # 路径2: S->C->G (2个动作，代价: 10+1=11)
            # BFS会先找到路径2，因为只有2个动作
            yield ("to_A", "A", 1.0)
            yield ("to_C", "C", 10.0)  # 高代价但动作数少
        elif state == "A":
            yield ("to_B", "B", 1.0)
        elif state == "B":
            yield ("to_G", "G", 1.0)
        elif state == "C":
            yield ("to_G", "G", 1.0)
            
    def state_key(self, state):
        return state
        
    def heuristic(self, state):
        return 0.0

def bfs_original(problem, case="test", max_nodes=10000, loop_check=True):
    """原始BFS实现"""
    start_t = time.perf_counter()
    heur_name = problem.heuristic_name
    start = problem.initial_state()
    start_key = problem.state_key(start)

    q = deque([Node(state=start, parent=None, action=None, g=0.0, h=0.0)])
    visited = {start_key} if loop_check else set()
    nodes_expanded = 0
    max_frontier = 1

    while q:
        max_frontier = max(max_frontier, len(q))
        node = q.popleft()
        if problem.is_goal(node.state):
            actions = node.iter_actions()
            end_t = time.perf_counter()
            return {
                "algorithm": "bfs",
                "path_cost": node.g,
                "nodes_expanded": nodes_expanded,
                "path_len": len(actions),
                "actions": actions
            }

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
    return {"algorithm": "bfs", "path_cost": float("inf")}

def bfs_ucs(problem, case="test", max_nodes=10000, loop_check=True):
    """BFS作为UCS"""
    start_t = time.perf_counter()
    heur_name = problem.heuristic_name
    start = problem.initial_state()
    start_key = problem.state_key(start)

    heap = []
    tie = 0
    start_node = Node(state=start, parent=None, action=None, g=0.0, h=0.0)
    heapq.heappush(heap, (start_node.g, tie, start_node))
    tie += 1

    visited = {start_key} if loop_check else set()
    nodes_expanded = 0
    max_frontier = 1

    while heap:
        max_frontier = max(max_frontier, len(heap))
        _cost, _t, node = heapq.heappop(heap)
        if problem.is_goal(node.state):
            actions = node.iter_actions()
            end_t = time.perf_counter()
            return {
                "algorithm": "bfs_ucs",
                "path_cost": node.g,
                "nodes_expanded": nodes_expanded,
                "path_len": len(actions),
                "actions": actions
            }

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
    return {"algorithm": "bfs_ucs", "path_cost": float("inf")}

class Node:
    def __init__(self, state, parent, action, g, h):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.h = h
        
    def iter_actions(self):
        actions = []
        n = self
        while n is not None and n.action is not None:
            actions.append(n.action)
            n = n.parent
        actions.reverse()
        return actions

def main():
    print("创建真正的BFS反例:")
    print("=" * 80)
    
    problem = SimpleProblem()
    
    print("问题描述:")
    print("  路径1: S -> A -> B -> G (3个动作，代价: 1+1+1=3)")
    print("  路径2: S -> C -> G (2个动作，代价: 10+1=11)")
    print("  最优路径: 路径1 (代价3)")
    print("  次优路径: 路径2 (代价11)")
    print("\n  关键: 次优路径动作数更少(2 vs 3)，BFS会先找到它")
    
    print("\n测试原始BFS:")
    result_bfs = bfs_original(problem)
    print(f"  Path cost: {result_bfs['path_cost']}")
    print(f"  Path: {' -> '.join(result_bfs['actions'])}")
    print(f"  Nodes expanded: {result_bfs['nodes_expanded']}")
    
    print("\n测试BFS作为UCS:")
    result_ucs = bfs_ucs(problem)
    print(f"  Path cost: {result_ucs['path_cost']}")
    print(f"  Path: {' -> '.join(result_ucs['actions'])}")
    print(f"  Nodes expanded: {result_ucs['nodes_expanded']}")
    
    print("\n结论:")
    if result_bfs['path_cost'] > result_ucs['path_cost']:
        print("  ✓ 成功创建反例！原始BFS找到了次优路径")
        print(f"  BFS path cost: {result_bfs['path_cost']} (次优)")
        print(f"  UCS path cost: {result_ucs['path_cost']} (最优)")
    else:
        print("  ✗ 未能创建反例，两者都找到了相同路径")
        
    print("\n分析ISS问题:")
    print("  在ISS问题中，BFS和A*的path cost总是相同，因为:")
    print("  1. 所有必需任务序列基本相同")
    print("  2. 移动路径选择有限")
    print("  3. 代价差异小(只有1和2的区别)")
    print("  4. 最优路径恰好也是最少动作数路径")
    print("  5. 状态空间有限，BFS能探索所有可能路径")

if __name__ == "__main__":
    main()