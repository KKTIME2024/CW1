#!/usr/bin/env python3
"""
深入分析BFS和A*的path cost为什么总是相同
"""

from search.algorithms import bfs, astar
from search.problems.iss_robot import build_case_problem, base_iss_map, base_move_cost

def analyze_problem_structure():
    """分析问题结构"""
    print("分析ISS机器人问题的结构:")
    print("=" * 80)
    
    # 分析地图
    iss_map = base_iss_map()
    print("地图结构:")
    for room, neighbors in iss_map.items():
        print(f"  {room:15} -> {neighbors}")
    
    print("\n移动代价:")
    print("  Node_2 <-> Airlock: 代价 2")
    print("  其他边: 代价 1")
    
    # 分析状态空间
    print("\n状态表示 (ISSState):")
    print("  robot_loc: 机器人位置 (6个可能位置)")
    print("  new_filter_loc: 新滤芯位置 (7个可能位置: 6个房间 + 'carried')")
    print("  old_filter_loc: 旧滤芯位置 (3个可能位置: Storage_PMM, US_Lab, 'carried')")
    print("  toolbox_loc: 工具箱位置 (3个可能位置: Storage_PMM, US_Lab, 'carried')")
    print("  old_filter_removed: 布尔值")
    print("  new_filter_installed: 布尔值")
    
    # 计算状态空间大小
    robot_positions = 6
    new_filter_positions = 7  # 6 rooms + carried
    old_filter_positions = 3  # Storage_PMM, US_Lab, carried
    toolbox_positions = 3     # Storage_PMM, US_Lab, carried
    old_filter_removed = 2    # True/False
    new_filter_installed = 2  # True/False
    
    total_states = (robot_positions * new_filter_positions * old_filter_positions * 
                   toolbox_positions * old_filter_removed * new_filter_installed)
    print(f"\n理论状态空间大小: {total_states:,} 个状态")
    print("实际可达状态会更少，因为有约束条件")

def analyze_bfs_behavior():
    """分析BFS的行为"""
    print("\n\n分析BFS算法行为:")
    print("=" * 80)
    
    print("BFS实现的关键特点:")
    print("  1. 使用队列 (deque) 进行层次扩展")
    print("  2. 每个节点记录累积代价 g(n)")
    print("  3. 扩展节点时，子节点的 g = 父节点.g + step_cost")
    print("  4. 找到目标时，返回节点的 g 值作为 path_cost")
    
    print("\nBFS在有权重图中的问题:")
    print("  1. BFS按层次扩展，找到的是最少动作数的路径")
    print("  2. 在均匀代价图中，最少动作数 = 最小代价")
    print("  3. 在非均匀代价图中，最少动作数 ≠ 最小代价")
    print("  4. 本问题中只有一条边代价为2，其他为1")
    
    print("\n为什么BFS可能找到最小代价路径:")
    print("  1. 问题结构相对简单")
    print("  2. 代价差异不大 (只有1和2的区别)")
    print("  3. 最优路径可能恰好也是最少动作数路径")
    print("  4. 状态空间有限，BFS能探索所有可能路径")

def analyze_astar_behavior():
    """分析A*的行为"""
    print("\n\n分析A*算法行为:")
    print("=" * 80)
    
    print("A*实现的关键特点:")
    print("  1. 使用优先队列 (heapq)，按 f(n) = g(n) + h(n) 排序")
    print("  2. 使用 best_g 字典记录到达每个状态的最小代价")
    print("  3. 如果找到更小的 g 值，会更新 best_g")
    print("  4. 保证找到最小代价路径（如果启发式可采纳）")
    
    print("\n启发式函数分析:")
    print("  1. waypoints: 剩余必经房间的最短路径距离之和")
    print("  2. next: 到下一个必经房间的最短距离")
    print("  3. goal: 到最终目标房间的距离")
    print("  4. zero: 恒为0，退化为UCS")
    
    print("\n为什么A*总能找到最小代价路径:")
    print("  1. 启发式函数都是可采纳的 (admissible)")
    print("  2. 使用 best_g 确保不会错过更优路径")
    print("  3. 优先扩展 f(n) 最小的节点")

def test_edge_cases():
    """测试边界情况"""
    print("\n\n测试边界情况:")
    print("=" * 80)
    
    # 创建一个更复杂的地图
    complex_map = {
        "Start": ["A", "B"],
        "A": ["Start", "Goal"],
        "B": ["Start", "Goal"],
        "Goal": ["A", "B"]
    }
    
    print("假设一个更复杂的地图:")
    print("  Start -> A (代价1), Start -> B (代价3)")
    print("  A -> Goal (代价1), B -> Goal (代价1)")
    print("  最短路径: Start->A->Goal (代价2)")
    print("  BFS可能找到: Start->B->Goal (代价4)")
    print("  因为BFS按动作数扩展，两个路径都是2个动作")
    
    print("\n在本ISS问题中:")
    print("  1. 所有必需的任务序列基本相同")
    print("  2. 移动路径选择有限")
    print("  3. 代价差异只在于是否经过Node_2<->Airlock边")
    print("  4. 最优路径明显会避免这条边")

def create_counterexample():
    """创建一个BFS和A* path cost不同的反例"""
    print("\n\n创建BFS和A* path cost不同的反例:")
    print("=" * 80)
    
    print("要创建BFS和A* path cost不同的情况，需要:")
    print("  1. 更大的代价差异 (如1 vs 10)")
    print("  2. 更复杂的路径选择")
    print("  3. 最少动作数路径不是最小代价路径")
    
    print("\n示例:")
    print("  地图: S--(1)--A--(1)--G")
    print("        S--(10)-B--(1)--G")
    print("  最短代价路径: S->A->G (代价2)")
    print("  BFS可能找到: S->B->G (代价11)")
    print("  因为两个路径都是2个动作")
    
    print("\n修改ISS问题使其出现差异:")
    print("  1. 增加更多高代价边")
    print("  2. 创建绕远路但动作数少的路径")
    print("  3. 增加状态空间的复杂性")

if __name__ == "__main__":
    analyze_problem_structure()
    analyze_bfs_behavior()
    analyze_astar_behavior()
    test_edge_cases()
    create_counterexample()