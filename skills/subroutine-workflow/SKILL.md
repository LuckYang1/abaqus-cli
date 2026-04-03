---
name: abaqus-subroutine-workflow
description: Abaqus 用户子程序开发 skill — 编写、编译、datacheck、调试的迭代开发工作流
---

# Abaqus 子程序开发工作流

当用户需要开发或调试 Abaqus 用户子程序时使用此 skill。

## 适用场景

- 用户编写了 UMAT/VUMAT/UEL 等子程序需要编译和测试
- 用户子程序编译失败需要调试
- 用户需要验证子程序在 datacheck 中的行为

## 工作流步骤

### 第 1 步: 编译子程序

```bash
python scripts/abaqus_runner.py make fortran=<sub_file>
```

根据文件名后缀选择求解器：
- `.for` / `.f90` — 默认 Standard 求解器
- 如果用户指定 `explicit`，添加到命令中

### 第 2 步: 检查编译结果

编译失败时：
- 解析编译器输出中的错误行号和类型
- 常见错误：语法错误、未声明变量、类型不匹配
- 报告具体行号和修复建议

编译成功时：
- 确认生成了 .obj / .so 文件
- 通知用户可以进入 datacheck 阶段

### 第 3 步: Datacheck 验证

```bash
python scripts/abaqus_runner.py datacheck job=<test_model> user=<compiled_obj>
```

检查 .dat 文件：
- 如果有 ERROR：子程序逻辑错误（如数组越界、除零）
- 如果有 WARNING：检查是否可接受
- 如果成功：子程序可以用于正式分析

### 第 4 步: 测试分析（可选）

如果用户需要进行小型测试分析验证子程序行为：
```bash
python scripts/abaqus_runner.py job=<test_model> user=<compiled_obj> cpus=1
```

### 第 5 步: 迭代调试

如果 datacheck 或分析失败：
1. 定位 .msg 文件中的错误
2. 结合子程序源码分析问题
3. 用户修改代码后回到第 1 步

## 常见子程序类型

| 子程序 | 用途 | 关键接口 |
|--------|------|----------|
| UMAT | 用户自定义材料 | stress, statev, ddsdde |
| VUMAT | 显式分析材料 | stress, stateNew |
| UEL | 用户自定义单元 | rhs, amatrx |
| USDFLD | 场变量依赖 | field, statev |
| UEXPAN | 热膨胀模型 | expand, strain |

## 调试技巧

- 在子程序中使用 `write(6,*)` 输出调试信息到 .msg 文件
- 从简单材料模型开始，逐步增加复杂度
- 使用小模型进行快速迭代测试
- 检查 statev 数组大小是否与 *DEPVAR 定义一致
