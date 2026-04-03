---
name: abaqus-resume
description: 恢复被暂停的 Abaqus 作业
---

# /abaqus-resume — 恢复作业

恢复被 `/abaqus-suspend` 暂停的 Abaqus 作业。

## 使用方式

用户提供作业名称。你需要：

1. 构建命令: `abaqus resume=<job_name>`
2. 执行恢复
3. 提示使用 `/abaqus-monitor` 监控进度

## 执行流程

```
用户: /abaqus-resume model

1. 构建命令: abaqus resume=model
2. 执行恢复
3. 确认恢复成功
4. 提示: 使用 /abaqus-monitor model 监控进度
```

## 注意事项

- 只能恢复被 suspend 暂停的作业
- 如果作业是被 terminate 终止的，需要使用 `/abaqus-run` 的 continue 模式（需要 .res 文件）
