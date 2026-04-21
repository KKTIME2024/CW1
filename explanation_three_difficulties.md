# 三种难度的区别

## 1. 初始状态对比

### Easy（简单）
```python
robot_loc="Node_3"           # 机器人起点：Node_3（中心位置）
new_filter_loc="Storage_PMM" # 新滤芯：Storage_PMM
old_filter_loc="US_Lab"      # 旧滤芯：US_Lab（未拆除）
toolbox_loc="Storage_PMM"    # 工具箱：Storage_PMM
```

### Medium（中等）
```python
robot_loc="Airlock"          # 机器人起点：Airlock（偏远位置）
new_filter_loc="Storage_PMM" # 新滤芯：Storage_PMM
old_filter_loc="US_Lab"      # 旧滤芯：US_Lab（未拆除）
toolbox_loc="US_Lab"         # 工具箱：US_Lab（已在实验室）
```

### Hard（困难）
```python
robot_loc="Airlock"          # 机器人起点：Airlock（偏远位置）
new_filter_loc="Storage_PMM" # 新滤芯：Storage_PMM
old_filter_loc="US_Lab"      # 旧滤芯：US_Lab（未拆除）
toolbox_loc="Storage_PMM"    # 工具箱：Storage_PMM
```

## 2. 难度递增的关键因素

### 因素1：机器人起点位置
- **Easy**：Node_3（中心枢纽，四通八达）
- **Medium/Hard**：Airlock（偏远角落，到Node_2代价为2）

### 因素2：工具箱位置
- **Easy/Hard**：Storage_PMM（需要先去拿）
- **Medium**：US_Lab（已在实验室，但机器人不在那里）

### 因素3：组合复杂度
1. **Easy**：工具箱和新滤芯在同一位置（Storage_PMM），起点居中
2. **Medium**：工具箱在US_Lab但机器人在Airlock，存在"先有鸡还是先有蛋"问题
3. **Hard**：工具箱在Storage_PMM，机器人在Airlock，需要最长路径规划

## 3. 任务执行顺序差异

### Easy 任务流程
```
1. 从Node_3出发
2. 到Storage_PMM拿工具箱
3. 到US_Lab拆旧滤芯
4. 送旧滤芯回Storage_PMM
5. 拿新滤芯
6. 到US_Lab装新滤芯
7. 还工具箱到Storage_PMM
8. 到Observatory
```

### Medium 任务流程（关键挑战）
```
1. 从Airlock出发（代价2到Node_2）
2. 到US_Lab拿工具箱（但需要工具箱才能进US_Lab？矛盾！）
实际：需要先空手进US_Lab，但受约束限制
解决方案：需要特殊路径规划
```

### Hard 任务流程
```
1. 从Airlock出发（代价2）
2. 到Storage_PMM拿工具箱
3. 到US_Lab拆旧滤芯
4. 送旧滤芯回Storage_PMM
5. 拿新滤芯
6. 到US_Lab装新滤芯
7. 还工具箱到Storage_PMM
8. 到Observatory
（路径最长）
```

## 4. 实验数据对比（A* + waypoints）

| 难度 | 节点扩展 | 路径代价 | 路径长度 | 搜索复杂度 |
|------|----------|----------|----------|------------|
| **Easy** | 103 | 15.0 | 24 | 最低 |
| **Medium** | 100 | 14.0 | 20 | 中等（但路径最短） |
| **Hard** | 103 | 18.0 | 26 | 最高 |

### 有趣发现
1. **Medium路径代价最低（14.0）**：因为工具箱已在US_Lab，减少往返
2. **Hard路径代价最高（18.0）**：需要从Airlock到Storage_PMM的长距离移动
3. **节点扩展数相似**：三种难度搜索复杂度相当

## 5. 难度本质分析

### Easy：教学示例
- 起点居中，物品集中
- 适合演示基本算法流程
- 路径规划相对直接

### Medium：约束挑战
- **核心难点**：进入US_Lab需要工具箱，但工具箱在US_Lab
- **解决方案**：机器人必须先空手进入US_Lab？实际上受约束限制
- **实际分析**：这可能是一个设计上的挑战，测试算法处理约束的能力

### Hard：综合难度
- 偏远起点 + 分散物品
- 需要最长移动路径
- 测试算法的效率和最优性

## 6. 在演示中的意义

### 展示算法鲁棒性
- **Easy**：展示算法基本功能
- **Medium**：展示处理约束的能力
- **Hard**：展示在复杂情况下的性能

### 数据对比价值
```bash
# 三种难度的A* + waypoints结果
Easy:   103节点, 15.0代价, 24步
Medium: 100节点, 14.0代价, 20步  
Hard:   103节点, 18.0代价, 26步
```

这个对比展示：
1. 难度 ≠ 节点扩展数（搜索复杂度）
2. 难度影响路径代价和长度
