---
name: abaqus-monitor
description: 监控 Abaqus 作业状态，解析 .sta/.msg 文件
---

# /abaqus-monitor — 作业监控

使用此命令监控 Abaqus 作业的运行状态。

## 使用方式

用户提供作业名称。你需要：

1. 调用 `scripts/job_monitor.py` 解析 .sta 和 .msg 文件
2. 显示作业状态、进度、错误和警告
3. 支持 `--watch` 持续监控模式

## 执行流程

```
用户: /abaqus-monitor model

1. 查找 model.sta 和 model.msg
2. 解析状态（COMPLETED/TERMINATED/RUNNING）
3. 统计迭代次数、警告、错误
4. 格式化输出
```

## 持续监控

```
用户: /abaqus-monitor --watch model

每隔 10 秒刷新一次状态，直到作业完成或用户中断
```

## 多作业监控

```
用户: /abaqus-monitor model1 model2 model3

依次显示每个作业的状态
```

## 输出格式

```
[RUN] model
  状态: RUNNING
  增量步: 1542
  警告: 3
  ODB: model.odb (245.1 MB)
```

## 状态说明

| 标记 | 含义 |
|------|------|
| [DONE] | 分析完成 |
| [RUN]  | 正在运行 |
| [TERM] | 用户终止 |
| [ABRT] | 分析中止 |
| [????] | 未知状态 |
| [MISS] | 文件未找到 |
