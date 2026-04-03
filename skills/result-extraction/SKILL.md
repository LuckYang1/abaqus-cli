---
name: abaqus-result-extraction
description: Abaqus ODB 数据提取 skill — 从输出数据库中提取场/历史数据，支持多种输出格式
---

# Abaqus ODB 数据提取

当用户需要从 Abaqus ODB 文件中提取分析结果时使用此 skill。

## 适用场景

- 用户分析完成后需要提取应力、位移等场数据
- 用户需要将结果导出为 CSV 进行进一步处理
- 用户需要生成 ODB 内容报告
- 用户需要将 ODB 转换为其他格式（Simpack）

## 工作流步骤

### 第 1 步: 了解 ODB 内容

先调用 odbreport 了解 ODB 文件结构：
```bash
python scripts/odb_extractor.py report <odb_path>
```
获取：分析步名称、帧信息、可用场输出变量、历史输出变量。

### 第 2 步: 确定提取需求

与用户确认：
- 提取哪些场变量（S, U, E, RF 等）
- 提取哪个分析步
- 提取哪一帧（最后一帧 / 特定帧 / 全部帧）
- 输出格式（CSV）

### 第 3 步: 执行提取

```bash
python scripts/odb_extractor.py extract <odb_path> --field <var> --step <step> --frame <idx> --output <csv>
```

### 第 4 步: 数据验证

提取完成后：
- 检查 CSV 文件行数是否合理
- 报告数据范围（最大值、最小值）
- 对于应力数据，检查量级是否合理

### 第 5 步: 后续处理（可选）

根据用户需求：
- 使用 pandas 进行统计分析
- 使用 matplotlib 生成云图或曲线
- 与其他分析结果进行对比

## 场输出变量参考

| 变量名 | 类型 | 维度 | 说明 |
|--------|------|------|------|
| S | Element | 6 (对称张量) | 应力 (S11, S22, S33, S12, S13, S23) |
| E | Element | 6 | 应变 |
| U | Node | 3 | 位移 (U1, U2, U3) |
| RF | Node | 3 | 反力 |
| CF | Node | 3 | 集中力 |
| PE | Element | 6 | 塑性应变 |
| TEMP | Node | 1 | 温度 |
| PRESS | Element | 1 | 静水压力 |
| MISES | Element | 1 | Mises 应力 |
| LE | Element | 6 | 对数应变 |

## 注意事项

- 大型 ODB 文件（>1GB）提取可能需要较长时间
- 场输出数据量取决于节点/单元数量
- 提取脚本在 Abaqus Python 环境中运行，不依赖外部 Python 库
