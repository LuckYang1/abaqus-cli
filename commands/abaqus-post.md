---
name: abaqus-post
description: 从 Abaqus ODB 文件中提取后处理数据（场输出、历史输出、报告）
---

# /abaqus-post — 后处理

使用此命令从 Abaqus ODB 文件中提取结果数据。

## 使用方式

用户提供 ODB 文件和提取需求。你需要：

1. **环境预检查**：先运行 `python scripts/version_resolver.py --detect` 确认 Abaqus 可用
2. 调用 `scripts/odb_extractor.py` 提取数据
3. 支持的操作：`report`（生成报告）、`extract`（提取场输出）、`odb2sim`（Simpack 转换）、`restartjoin`（合并重启动）

## 提取场输出

```
用户: /abaqus-post extract model.odb --field S --step Step-1

1. 生成 Abaqus Python 提取脚本
2. 执行 abaqus python extract_script.py
3. 输出 CSV 文件
```

## 场输出变量

| 变量名 | 说明 |
|--------|------|
| S | 应力 |
| U | 位移 |
| E | 应变 |
| RF | 反力 |
| CF | 节点集中力 |
| PE | 塑性应变 |
| TEMP | 温度 |
| NT | 法向力 |
| CT | 接触力 |

## 生成报告

```
用户: /abaqus-post report model.odb

调用 abaqus odbreport odb=model.odb
输出 ODB 内容摘要报告
```

## ODB 转 Simpack

```
用户: /abaqus-post odb2sim model.odb

调用 abaqus odb2sim odb=model.odb
```

## 合并重启动文件

```
用户: /abaqus-post restartjoin --output merged --input part1 --input part2

调用 abaqus restartjoin output=merged input=part1 input=part2
```
