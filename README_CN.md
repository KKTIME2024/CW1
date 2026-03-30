# COMP2611 课程作业 Part B - 机器人工作者实验

## 项目概述

这是一个国际空间站(ISS)机器人维护任务的搜索算法实验项目。项目实现了多种搜索算法（BFS、DFS、最佳优先搜索、A*）在机器人任务规划问题上的性能比较。

## 项目结构

```
.
├── code/                    # 主要代码目录
│   ├── main.py             # 主程序，提供CLI接口
│   ├── README.md           # 项目说明（英文）
│   ├── B_OVERVIEW.md       # 详细技术说明
│   └── search/             # 搜索算法实现
├── B_report.md             # 实验报告（最终提交版本）
├── results.csv             # 详细实验结果
├── summary.csv             # 实验结果汇总
├── experiment_summary.txt  # 实验总结文本
└── *.png                   # 生成的图表文件
```

## 快速开始

### 1. 运行单个实验

```bash
cd code
python3 main.py run --case easy --algo astar --heuristic waypoints
```

### 2. 运行完整实验并生成报告

```bash
# 使用简单脚本（推荐）
python3 run_experiments_simple.py

# 或使用完整脚本（需要matplotlib）
python3 run_experiment_and_generate_charts.py
```

### 3. 自定义参数

```bash
# 使用10个随机种子，最大节点数5000
python3 run_experiments_simple.py 10 5000
```

## 测试用例

项目包含三个不同难度的测试用例：

1. **Easy（简单）**: 机器人从Node_3开始，所有物品在Storage_PMM
2. **Medium（中等）**: 机器人从Airlock开始，工具箱在US_Lab
3. **Hard（困难）**: 机器人从Airlock开始，工具箱在Storage_PMM

## 搜索算法

- **BFS**: 广度优先搜索（保证最短路径）
- **DFS-Fixed**: 深度优先搜索（固定动作顺序）
- **DFS-Random**: 深度优先搜索（随机动作顺序）
- **Best-first**: 最佳优先搜索（贪心启发式）
- **A***: A星搜索（最优启发式搜索）

## 启发式函数

- **waypoints**: 剩余必经点最短路径距离和（最有效）
- **next**: 到下一个必经点的距离
- **goal**: 到最终目标的距离
- **zero**: 零启发式（退化为统一代价搜索）

## 关键约束

1. **单物品携带**: 一次只能携带一个物品
2. **US_Lab访问限制**: 进入US_Lab必须携带工具箱
3. **非对称移动代价**: Node_2 ↔ Airlock移动代价为2（其他为1）
4. **旧滤芯回收**: 旧滤芯必须送回Storage_PMM

## 实验结果

基于实验数据的主要发现：

1. **A* vs BFS**: A*使用waypoints启发式能在保证最优性的同时显著减少节点扩展
2. **Best-first**: 扩展节点最少但路径往往不是最优
3. **DFS**: 扩展节点最少但路径长度显著更长
4. **启发式效果**: waypoints启发式在A*和best-first中表现最佳

## 使用建议

1. **关键任务**: 使用A* + waypoints启发式（保证最优性）
2. **资源受限**: 使用best-first搜索（接近最优解）
3. **避免使用**: DFS（路径非最优且不可预测）

## 文件说明

- `B_report.md`: 最终实验报告，包含完整B1-B4部分
- `run_experiments_simple.py`: 自动化实验脚本（无需matplotlib）
- `run_experiment_and_generate_charts.py`: 带图表的实验脚本（需要matplotlib）
- `generate_simple_charts.py`: 简单图表生成脚本

## 报告更新

运行实验后，使用生成的表格更新`B_report.md`：
1. B3部分：复制生成的表格
2. B4部分：使用生成的关键发现
3. 结论部分：更新总结统计

## 依赖要求

- Python 3.8+
- 基础Python库（无特殊依赖）

可选依赖（用于图表生成）：
- matplotlib
- numpy

## 许可证

本项目为COMP2611课程作业，仅供学习使用。