#!/usr/bin/env python3
"""Abaqus 版本解析器 — 将版本字符串解析为实际命令路径。"""

import shutil
import subprocess
import sys


def resolve_command(version_str: str) -> str:
    """将版本字符串解析为 Abaqus 命令名。

    >>> resolve_command("2024")
    'abq2024'
    >>> resolve_command("abq2025")
    'abq2025'
    >>> resolve_command("abaqus")
    'abaqus'
    """
    if not version_str or version_str.strip() == "":
        return "abaqus"
    version_str = version_str.strip()
    # 已经是完整命令名
    if version_str.startswith("abq") or version_str == "abaqus":
        return version_str
    # 纯数字年份
    if version_str.isdigit():
        return f"abq{version_str}"
    # 带 "abq" 前缀的年份
    return version_str


def validate_command(cmd: str) -> bool:
    """检查命令是否在 PATH 中可用。"""
    return shutil.which(cmd) is not None


def auto_detect() -> str:
    """自动检测系统中可用的 Abaqus 命令。"""
    candidates = ["abaqus"] + [f"abq{y}" for y in range(2026, 2019, -1)]
    for cmd in candidates:
        if validate_command(cmd):
            return cmd
    return ""


def get_version_info(cmd: str = "abaqus") -> str:
    """获取 Abaqus 版本信息。"""
    try:
        result = subprocess.run(
            [cmd, "information=version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return (result.stdout + result.stderr).strip()
    except FileNotFoundError:
        return f"错误: 命令 '{cmd}' 未找到"
    except subprocess.TimeoutExpired:
        return f"错误: 命令 '{cmd}' 执行超时"


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Abaqus 版本解析器")
    parser.add_argument("--resolve", help="解析版本字符串为命令名")
    parser.add_argument("--validate", help="验证命令是否可用")
    parser.add_argument("--detect", action="store_true", help="自动检测可用命令")
    parser.add_argument("--info", nargs="?", const="abaqus", help="获取版本信息")
    args = parser.parse_args()

    if args.resolve:
        cmd = resolve_command(args.resolve)
        valid = validate_command(cmd)
        print(f"{cmd} (可用: {'是' if valid else '否'})")
    elif args.validate:
        print(f"{args.validate}: {'可用' if validate_command(args.validate) else '不可用'}")
    elif args.detect:
        cmd = auto_detect()
        if cmd:
            print(f"检测到: {cmd}")
        else:
            print("未找到可用的 Abaqus 命令")
    elif args.info:
        print(get_version_info(args.info))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
