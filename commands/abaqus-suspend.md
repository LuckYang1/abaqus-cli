---
name: abaqus-suspend
description: 暂停正在运行的 Abaqus 作业
---

# /abaqus-suspend — 暂停作业

暂停正在运行的 Abaqus 作业，保留内存状态，后续可用 `/abaqus-resume` 恢复。

## 使用方式

用户提供作业名称。你需要：

1. 构建命令: `abaqus suspend=<job_name>`
2. 执行暂停
3. 提示用户使用 `/abaqus-resume` 恢复

## 执行流程

```
用户: /abaqus-suspend model

1. 构建命令: abaqus suspend=model
2. 执行暂停
3. 确认暂停成功
4. 提示: 使用 /abaqus-resume model 恢复作业
```

## 注意事项

- suspend 会冻结作业状态，不丢失进度
- 恢复请使用 `/abaqus-resume`，不要重新提交
- 如果 suspend 失败，可使用 `/abaqus-run` 的 terminate 作为备选
