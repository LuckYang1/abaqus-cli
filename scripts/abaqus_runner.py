#!/usr/bin/env python3
"""Abaqus 命令构建与执行器 — 基于 COMMAND_REGISTRY 的统一 CLI 封装。"""

import argparse
import subprocess
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# 命令注册表 — 映射所有 abaqus 子命令及其参数约束
# ---------------------------------------------------------------------------

COMMAND_REGISTRY = {
    # ===== 作业管理 =====
    "job": {
        "category": "job",
        "required": ["job"],
        "optional": [
            "cpus", "gpus", "memory", "scratch", "user", "input",
            "analysis", "datacheck", "continue", "convert", "recover",
            "syntaxcheck", "interactive", "background", "double",
            "output_precision", "stress_file", "results_format",
        ],
        "help": "提交 Abaqus 分析作业",
    },
    "datacheck": {
        "category": "job",
        "required": ["job"],
        "optional": [
            "cpus", "memory", "user", "input", "double",
            "output_precision", "scratch",
        ],
        "help": "对作业进行数据检查（不运行分析）",
    },
    "continue": {
        "category": "job",
        "required": ["job"],
        "optional": [
            "cpus", "gpus", "memory", "user", "input", "background",
            "double", "output_precision", "scratch",
        ],
        "help": "继续运行中断的作业",
    },
    "convert": {
        "category": "job",
        "required": ["job", "convert"],
        "optional": ["recover", "output_precision", "oldjob"],
        "help": "转换重启动文件格式",
    },
    "recover": {
        "category": "job",
        "required": ["job"],
        "optional": [
            "cpus", "memory", "user", "input", "background",
            "double", "scratch",
        ],
        "help": "从重启动文件恢复分析",
    },
    "syntaxcheck": {
        "category": "job",
        "required": ["job"],
        "optional": ["user", "input", "scratch"],
        "help": "对输入文件进行语法检查",
    },
    # ===== 作业控制 =====
    "suspend": {
        "category": "control",
        "required": ["job"],
        "optional": [],
        "help": "暂停正在运行的作业",
    },
    "resume": {
        "category": "control",
        "required": ["job"],
        "optional": [],
        "help": "恢复暂停的作业",
    },
    "terminate": {
        "category": "control",
        "required": ["job"],
        "optional": [],
        "help": "终止正在运行的作业",
    },
    # ===== 子程序编译 =====
    "make": {
        "category": "make",
        "required": [],
        "optional": ["input", "output", "standard", "explicit", "cfd", "fortran"],
        "help": "编译用户子程序",
    },
    # ===== 文件翻译 =====
    "toNastran": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job", "analysis"],
        "help": "将 Abaqus 模型翻译为 Nastran",
    },
    "fromNastran": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job"],
        "help": "从 Nastran 输入文件导入模型",
    },
    "fromANSYS": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job"],
        "help": "从 ANSYS 输入文件导入模型",
    },
    "fromDyna": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job"],
        "help": "从 LS-DYNA 输入文件导入模型",
    },
    "fromPamcrash": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job"],
        "help": "从 PAM-CRASH 输入文件导入模型",
    },
    "fromRadioss": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job"],
        "help": "从 RADIOSS 输入文件导入模型",
    },
    "fromMoldflow": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job"],
        "help": "从 Moldflow 输入文件导入模型",
    },
    "fromSimpack": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job"],
        "help": "从 Simpack 输入文件导入模型",
    },
    "fromAdams": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job"],
        "help": "从 Adams 输入文件导入模型",
    },
    "fromExcite": {
        "category": "translate",
        "required": ["input"],
        "optional": ["output", "job"],
        "help": "从 EXCITE 输入文件导入模型",
    },
    # ===== 数据库操作 =====
    "odbreport": {
        "category": "database",
        "required": ["odb"],
        "optional": ["output", "job"],
        "help": "生成 ODB 报告",
    },
    "odb2sim": {
        "category": "database",
        "required": ["odb"],
        "optional": ["output"],
        "help": "将 ODB 转换为 Simpack 格式",
    },
    "restartjoin": {
        "category": "database",
        "required": ["output"],
        "optional": ["input"],
        "help": "合并重启动文件",
    },
    # ===== 联合仿真 =====
    "cse": {
        "category": "cosim",
        "required": [],
        "optional": ["input", "job"],
        "help": "启动联合仿真引擎 (CSE)",
    },
    "cosimulation": {
        "category": "cosim",
        "required": ["job"],
        "optional": ["cpus", "input", "memory", "scratch"],
        "help": "运行联合仿真",
    },
    "fmu": {
        "category": "cosim",
        "required": ["job"],
        "optional": ["input", "output"],
        "help": "导出 FMU (功能模型单元)",
    },
    # ===== 加密/解密 =====
    "encrypt": {
        "category": "crypto",
        "required": ["input"],
        "optional": ["output"],
        "help": "加密 Python 脚本",
    },
    "decrypt": {
        "category": "crypto",
        "required": ["input"],
        "optional": ["output"],
        "help": "解密 Python 脚本",
    },
    # ===== 优化 =====
    "optimization": {
        "category": "optimization",
        "required": ["job"],
        "optional": [
            "cpus", "memory", "input", "user", "scratch",
            "background", "double",
        ],
        "help": "运行优化任务",
    },
}


def parse_kv_args(args_list: list[str]) -> dict[str, str]:
    """解析 key=value 形式的参数列表。"""
    params = {}
    for arg in args_list:
        if "=" in arg:
            key, _, value = arg.partition("=")
            params[key.strip()] = value.strip()
        else:
            params[arg] = ""
    return params


def build_command(
    subcommand: str,
    params: dict[str, str],
    abaqus_cmd: str = "abaqus",
) -> list[str]:
    """根据子命令和参数构建完整的命令行列表。

    >>> build_command("job", {"job": "test", "cpus": "4"})
    ['abaqus', 'job=test', 'cpus=4']
    """
    if subcommand not in COMMAND_REGISTRY:
        raise ValueError(f"未知子命令: {subcommand}。可用: {', '.join(COMMAND_REGISTRY.keys())}")

    spec = COMMAND_REGISTRY[subcommand]

    # 验证必需参数
    missing = [p for p in spec["required"] if p not in params]
    if missing:
        raise ValueError(f"缺少必需参数: {', '.join(missing)}")

    # 过滤未知参数
    valid = set(spec["required"]) | set(spec["optional"])
    filtered = {k: v for k, v in params.items() if k in valid}

    # 构建命令行
    # 对于 job 类的子命令（如 datacheck, continue），它们是 abaqus 的参数而非子命令
    if subcommand in ("job", "datacheck", "continue", "convert", "recover", "syntaxcheck"):
        cmd = [abaqus_cmd, f"{subcommand}=" + filtered.pop(subcommand, filtered.pop("job", ""))]
    elif subcommand == "make":
        cmd = [abaqus_cmd, "make"]
    elif subcommand in ("suspend", "resume", "terminate"):
        job_name = filtered.pop(subcommand, filtered.pop("job", ""))
        cmd = [abaqus_cmd, f"{subcommand}={job_name}"]
    else:
        cmd = [abaqus_cmd, subcommand]

    # 添加剩余参数
    for key, value in filtered.items():
        if value:
            cmd.append(f"{key}={value}")
        else:
            cmd.append(key)

    return cmd


def execute_command(
    cmd: list[str],
    timeout: Optional[int] = None,
    background: bool = False,
) -> subprocess.CompletedProcess:
    """执行构建好的命令。"""
    abaqus_cmd = cmd[0] if cmd else "unknown"
    try:
        if background:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return subprocess.CompletedProcess(
                args=cmd, returncode=0, stdout="", stderr=""
            )
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        print(f"错误: 命令 '{abaqus_cmd}' 未找到。", file=sys.stderr)
        print(f"请确认 Abaqus 已安装且 '{abaqus_cmd}' 在 PATH 中。", file=sys.stderr)
        print("可使用 --abaqus-cmd 指定正确的命令名，或运行 version_resolver.py --detect 自动检测。", file=sys.stderr)
        return subprocess.CompletedProcess(
            args=cmd, returncode=127,
            stdout="", stderr=f"命令 '{abaqus_cmd}' 未找到",
        )
    except subprocess.TimeoutExpired:
        print(f"错误: 命令执行超时 ({timeout}s)", file=sys.stderr)
        return subprocess.CompletedProcess(
            args=cmd, returncode=124,
            stdout="", stderr=f"命令执行超时 ({timeout}s)",
        )


def main():
    parser = argparse.ArgumentParser(
        description="Abaqus 命令构建与执行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("subcommand", help="Abaqus 子命令 (如 job, datacheck, toNastran)")
    parser.add_argument("params", nargs="*", help="参数 (key=value 格式)")
    parser.add_argument("--abaqus-cmd", default="abaqus", help="Abaqus 命令名 (默认: abaqus)")
    parser.add_argument("--timeout", type=int, default=None, help="超时秒数")
    parser.add_argument("--dry-run", action="store_true", help="仅打印命令，不执行")
    parser.add_argument("--list", action="store_true", help="列出所有可用子命令")
    args = parser.parse_args()

    if args.list:
        for name, spec in COMMAND_REGISTRY.items():
            print(f"  {name:20s} [{spec['category']:12s}] {spec['help']}")
        return

    params = parse_kv_args(args.params)

    try:
        cmd = build_command(args.subcommand, params, args.abaqus_cmd)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print(" ".join(cmd))
        return

    result = execute_command(cmd, timeout=args.timeout)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
