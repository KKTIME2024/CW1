# 演示快速参考卡片

## 核心数据（Hard Case）
| 算法 | 启发式 | 节点扩展 | 路径代价 | 是否最优 | 关键点 |
|------|--------|----------|----------|----------|--------|
| **A*** | waypoints | **103** | **18.0** | ✓ | 最优且高效 |
| **BFS** | (无) | 141 | 18.0 | ✓ | 最优但效率低 |
| **Best-first** | waypoints | 81 | 24.0 | ✗ | 高效但次优 |
| **DFS-Fixed** | (无) | 50 | 24.0 | ✗ | 最快但质量差 |

## 关键对比
- **A* vs BFS**：A*少扩展27%节点，相同最优解
- **A* vs Best-first**：A*多22节点，但代价少6（更优）
- **Best-first vs DFS**：Best-first多31节点，但路径相同代价

## 演示命令
```bash
# 基础演示（A* + waypoints）
cd code
python3 main.py run --case hard --algo astar --heuristic waypoints

# 对比演示
python3 main.py run --case hard --algo bfs
python3 main.py run --case hard --algo best_first --heuristic waypoints
python3 main.py run --case hard --algo dfs_fixed

# 完整实验
python3 run_experiments_simple.py
```

## 关键发现（一句话总结）
1. **BFS和A*在树结构中找到相同最优解**
2. **waypoints启发式减少27%节点扩展**
3. **Best-first效率高但可能次优**
4. **A*平衡最优性和效率最佳**

## 常见问题回答要点
1. **为什么树结构？** 简化问题，专注任务依赖
2. **waypoints为什么好？** 编码子目标顺序，更准确估计
3. **Best-first为什么次优？** 贪心策略缺乏代价校正
4. **启发式可采纳性？** 忽略动作成本，总是低估

## 时间分配建议
- 问题介绍：3分钟
- 算法概览：2分钟  
- 现场演示：3分钟
- 结果对比：4分钟
- 图表展示：3分钟
- 总结问答：5分钟

## 应急方案
- 代码无法运行：直接展示图表和summary.csv数据
- 图表无法打开：描述图表内容，引用具体数据
- 时间不够：跳过DFS演示，聚焦A* vs BFS对比

## 成功指标
- ✓ 清楚解释问题约束
- ✓ 展示算法性能差异  
- ✓ 解释waypoints启发式优势
- ✓ 对比不同算法权衡
- ✓ 回答至少2个问题