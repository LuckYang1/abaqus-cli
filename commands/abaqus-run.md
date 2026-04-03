---
name: abaqus-run
description: 提交 Abaqus 分析作业，支持 datacheck、continue、recover 等模式
---

# /abaqus-run — 作业提交

使用此命令提交 Abaqus 分析作业。

## 使用方式

用户会提供一个 `.inp` 文件和可选参数。你需要：

1. **环境预检查**：先运行 `python scripts/version_resolver.py --detect` 确认 Abaqus 可用。若未检测到，提示用户安装或使用 `--abaqus-cmd` 指定路径
2. 调用 `scripts/abaqus_runner.py` 构建并执行命令
3. 支持的子命令：`job`（默认）、`datacheck`、`continue`、`recover`、`syntaxcheck`
4. 版本切换：如果用户指定版本号（如 `2024`），使用 `scripts/version_resolver.py --resolve-and-validate 2024` 解析并验证

## 常用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| job | 作业名称（不含 .inp） | 必需 |
| cpus | CPU 核心数 | 4 |
| gpus | GPU 数量 | - |
| memory | 内存限制 | 8gb |
| scratch | 临时目录 | 系统默认 |
| user | 用户子程序文件 | - |
| double | 双精度 | - |
| input | 输入文件 | - |

## 执行流程

```
用户: /abaqus-run model.inp cpus=8 memory=16gb

1. 环境检查: version_resolver.py --detect → 确认命令可用
2. 解析参数: job=model, cpus=8, memory=16gb
3. 构建命令: abaqus job=model cpus=8 memory=16gb
4. 执行并返回结果（命令未找到时返回友好错误提示）
5. 如果作业非交互式提交，提示使用 /abaqus-monitor 监控
```

## Datacheck 模式

```
用户: /abaqus-run --datacheck model.inp

构建命令: abaqus datacheck=model cpus=4
仅检查语法和数据，不运行分析
```

## 注意事项

- 如果用户指定 `background` 参数，作业在后台运行，需使用 `/abaqus-monitor` 监控状态
- 子程序文件需先使用 `/abaqus-compile` 编译
- `continue` 模式需要存在重启动文件
