#!/usr/bin/env python3

"""
测试BFS和A*的path cost是否永远一样
"""

from search.algorithms import bfs, astar
from search.problems.iss_robot import build_case_problem

def test_bfs_vs_astar():
    """测试BFS和A*在不同情况下的path cost"""
    cases = ["easy", "medium", "hard"]
    heuristics = ["waypoints", "next", "goal", "zero"]
    
    print("测试BFS和A*的path cost比较:")
    print("=" * 80)
    
    for case in cases:
        print(f"\n测试案例: {case}")
        print("-" * 40)
        
        # 测试BFS
        problem_bfs = build_case_problem(case, heuristic_name="waypoints")
        result_bfs = bfs(
            problem=problem_bfs,
            case=case,
            max_nodes=10000,
            loop_check=True,
            seed=0
        )
        
        print(f"BFS path cost: {result_bfs.path_cost}")
        print(f"BFS nodes expanded: {result_bfs.nodes_expanded}")
        
        # 测试A*使用不同启发式
        for heuristic in heuristics:
            problem_astar = build_case_problem(case, heuristic_name=heuristic)
            result_astar = astar(
                problem=problem_astar,
                case=case,
                max_nodes=10000,
                loop_check=True,
                seed=0
            )
            
            cost_match = abs(result_bfs.path_cost - result_astar.path_cost) < 0.001
            status = "✓ 相同" if cost_match else "✗ 不同"
            print(f"A* ({heuristic:10}) path cost: {result_astar.path_cost:5.1f}, nodes: {result_astar.nodes_expanded:4d} {status}")
        
        print(f"BFS找到的路径长度: {result_bfs.path_len}")
        print(f"BFS动作序列: {' -> '.join(result_bfs.action_path)}")

def analyze_bfs_optimality():
    """分析BFS是否总是找到最优解"""
    print("\n\n分析BFS的最优性:")
    print("=" * 80)
    
    # BFS在有权重图中不一定找到最小代价路径
    # BFS按层次扩展，找到的是最少步数（动作数）的路径，但不一定是最小代价路径
    
    case = "easy"
    problem = build_case_problem(case, heuristic_name="waypoints")
    
    print(f"案例: {case}")
    print("地图边权重:")
    print("  - Node_2 <-> Airlock: 代价 2")
    print("  - 其他边: 代价 1")
    print("\nBFS特性:")
    print("  1. BFS按队列层次扩展，找到的是最少动作数的路径")
    print("  2. 在有权重图中，最少动作数 ≠ 最小代价")
    print("  3. 但在本问题中，所有动作（除了Move）代价为0")
    print("  4. Move动作中只有Node_2<->Airlock代价为2，其他为1")
    
    # 手动分析可能的路径
    print("\n路径分析:")
    print("  从Node_3开始，需要:")
    print("  1. 去Storage_PMM拿工具箱")
    print("  2. 去US_Lab拆旧滤芯")
    print("  3. 把旧滤芯送回Storage_PMM")
    print("  4. 拿新滤芯去US_Lab安装")
    print("  5. 把工具箱送回Storage_PMM")
    print("  6. 去Observatory")
    
    print("\n关键观察:")
    print("  - 所有路径都需要完成相同的基本任务序列")
    print("  - 移动代价差异只在于是否经过Node_2<->Airlock边")
    print("  - 最优路径会避免这条代价为2的边")
    print("  - BFS可能找到不同的动作序列，但总代价可能相同")

if __name__ == "__main__":
    test_bfs_vs_astar()
    analyze_bfs_optimality()