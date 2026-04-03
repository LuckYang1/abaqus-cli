---
name: abaqus-job-workflow
description: 完整的 Abaqus 仿真工作流 skill — 从输入文件到结果提取，覆盖子程序编译、作业提交、监控、后处理全流程
---

# Abaqus 完整仿真工作流

当用户需要运行一个完整的 Abaqus 仿真时使用此 skill。

## 适用场景

- 用户提供了 .inp 文件，需要完成从提交到获取结果的全流程
- 用户需要编译子程序后运行分析
- 用户需要多步分析（预加载 → 主分析）

## 工作流步骤

### 第 1 步: 环境检查

1. 使用 `scripts/version_resolver.py --detect` 检测可用的 Abaqus 命令
2. 如果用户指定了版本，使用 `--resolve <version>` 解析
3. 确认 .inp 文件存在

### 第 2 步: 子程序编译（如有）

如果用户提供了子程序文件：
```bash
python scripts/abaqus_runner.py make fortran=<sub_file>
```
检查编译是否成功。失败则报告编译器错误并停止。

### 第 3 步: 数据检查

```bash
python scripts/abaqus_runner.py datacheck job=<name> user=<subroutine>
```
检查 .dat 文件中的错误。datacheck 失败则报告并停止。

### 第 4 步: 提交分析

```bash
python scripts/abaqus_runner.py job=<name> cpus=<n> memory=<mem> user=<subroutine> background
```

### 第 5 步: 监控进度

```bash
python scripts/job_monitor.py <name> --watch --interval 30
```
持续监控直到 COMPLETED / TERMINATED / ABORTED。

### 第 6 步: 结果提取

如果分析完成：
```bash
python scripts/odb_extractor.py extract <name>.odb --field S --step Step-1
python scripts/odb_extractor.py extract <name>.odb --field U --step Step-1
```
提取应力 (S) 和位移 (U) 到 CSV 文件。

### 第 7 步: 报告汇总

汇总：
- 作业运行时间
- 收敛情况（检查 .msg 中的警告）
- ODB 文件大小
- 提取出的 CSV 数据预览（最大/最小值）

## 版本灵活性

全程支持 `abaqus`/`abq2024`/`abq20xx` 命令切换。在第 1 步确定版本后，后续所有命令使用同一个命令名。

## 错误处理

每一步失败时：
- 解析 .msg / .dat 文件中的错误信息
- 提供根本原因分析
- 建议修复方案
