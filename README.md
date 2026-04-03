<p align="center">
  <a href="https://github.com/LuckYang1/abaqus-cli">
    <img src="logo.svg" alt="abaqus-cli" width="400">
  </a>
</p>
<p align="center">
    <em>Abaqus 有限元分析 CLI 封装插件，专为 Claude Code 设计。AI Agent 可自主完成仿真工作流：作业提交、运行监控、后处理、子程序编译、格式翻译、联合仿真。</em>
</p>




<p align="center">
<a href="https://github.com/LuckYang1/abaqus-cli/">
<img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Plugin Version">
<a href="https://creativecommons.org/licenses/by/4.0/">
<img src="https://img.shields.io/badge/License-CC%20BY%204.0-green.svg" alt="License">
</p>


## 安装

在 Claude Code 中通过插件市场安装：

```
/plugin marketplace add LuckYang1/abaqus-cli
/plugin install abaqus-cli@abaqus-cli
```

## 功能特性

### Slash 命令

| 命令 | 用途 |
|------|------|
| `/abaqus-run` | 提交分析作业（job, datacheck, continue, recover, syntaxcheck） |
| `/abaqus-monitor` | 监控作业状态（解析 .sta/.msg 文件，支持持续轮询） |
| `/abaqus-post` | 后处理（ODB 报告、场输出提取、格式转换、重启动合并） |
| `/abaqus-compile` | 编译用户子程序（Fortran/C/C++，支持 standard/explicit/cfd） |
| `/abaqus-translate` | 文件翻译（Nastran, ANSYS, LS-DYNA, PAM-CRASH, RADIOSS 等） |

### Agent

| Agent | 用途 |
|-------|------|
| `abaqus-job-manager` | 作业生命周期管理（datacheck → submit → monitor → post-process） |
| `abaqus-post-processor` | 结果提取（场输出/历史输出、CSV 导出、报告生成） |

### Skill

| Skill | 用途 |
|-------|------|
| `job-workflow` | 完整仿真工作流自动化 |
| `subroutine-workflow` | 用户子程序迭代开发 |
| `result-extraction` | ODB 数据提取与后处理 |

## 环境要求

- **Abaqus** 已安装并配置 PATH
- **Python 3**（插件脚本）
- **Intel Fortran** 或 **gfortran**（编译用户子程序时需要）
- **LM_LICENSE_FILE** 环境变量（Abaqus 许可证）

## 详细文档

完整使用说明请参阅：https://LuckYang1.github.io/guide-of-abaqus/cli-plugin/

## 项目结构

```
abaqus-cli/
├── .claude-plugin/
│   ├── marketplace.json      # 插件市场定义
│   └── plugin.json           # 插件清单与配置
├── commands/                 # Slash 命令（5 个）
├── agents/                   # Agent 定义（2 个）
├── skills/                   # Skill 定义（3 个）
└── scripts/                  # Python 脚本
    ├── version_resolver.py   # 版本解析
    ├── abaqus_runner.py      # 命令构建与执行
    ├── job_monitor.py        # 作业状态监控
    └── odb_extractor.py      # ODB 数据提取
```

## 许可证

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
