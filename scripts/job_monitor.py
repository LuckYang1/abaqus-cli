#!/usr/bin/env python3
"""Abaqus 作业监控器 — 解析 .sta / .msg 文件获取作业状态。"""

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class JobStatus:
    """Abaqus 作业状态。"""
    job_name: str
    status: str = "UNKNOWN"
    iterations: int = 0
    total_iterations: int = 0
    errors: int = 0
    warnings: int = 0
    elapsed_time: str = ""
    sta_file: str = ""
    msg_file: str = ""
    odb_file: str = ""


@dataclass
class MsgInfo:
    """从 .msg 文件中提取的错误和警告信息。"""
    error_lines: list[str] = field(default_factory=list)
    warning_lines: list[str] = field(default_factory=list)


# .sta 文件中的状态标记
STA_PATTERNS = {
    "COMPLETED": re.compile(r"THE ANALYSIS HAS BEEN COMPLETED", re.IGNORECASE),
    "TERMINATED": re.compile(r"THE ANALYSIS HAS BEEN TERMINATED", re.IGNORECASE),
    "RUNNING": re.compile(r"THE ANALYSIS IS RUNNING", re.IGNORECASE),
    "ABORTED": re.compile(r"THE ANALYSIS HAS BEEN ABORTED", re.IGNORECASE),
}

# .sta 文件中的迭代进度
ITER_PATTERN = re.compile(
    r"INCREMENT\s+(\d+)\s+SUMMARY.*?STEP\s+(\d+)",
    re.IGNORECASE | re.DOTALL,
)

# .msg 文件中的错误/警告模式
MSG_ERROR = re.compile(r"^\s*ERROR:", re.IGNORECASE)
MSG_WARNING = re.compile(r"^\s*WARNING:", re.IGNORECASE)
MSG_ABORT = re.compile(r"THE ANALYSIS HAS BEEN ABORTED", re.IGNORECASE)


def parse_sta_file(sta_path: str) -> JobStatus:
    """解析 .sta 文件获取作业状态。

    检测 COMPLETED / TERMINATED / RUNNING / ABORTED 标记。
    """
    job_name = Path(sta_path).stem
    status = JobStatus(job_name=job_name, sta_file=sta_path)

    try:
        with open(sta_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except FileNotFoundError:
        status.status = "FILE_NOT_FOUND"
        return status

    lines = content.splitlines()

    # 查找状态 — 从文件末尾向前搜索最后一个状态标记
    for line in reversed(lines):
        for state_name, pattern in STA_PATTERNS.items():
            if pattern.search(line):
                if status.status == "UNKNOWN":
                    status.status = state_name
                break
        if status.status != "UNKNOWN":
            break

    # 统计迭代次数（粗略）
    increment_count = len(re.findall(r"INCREMENT\s+\d+", content, re.IGNORECASE))
    status.iterations = increment_count

    # 统计警告数量
    status.warnings = sum(1 for l in lines if re.search(r"WARNING", l, re.IGNORECASE))

    return status


def parse_msg_file(msg_path: str) -> MsgInfo:
    """解析 .msg 文件提取错误和警告。"""
    info = MsgInfo()

    try:
        with open(msg_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if MSG_ERROR.match(line):
                    info.error_lines.append(line.rstrip())
                elif MSG_WARNING.match(line):
                    info.warning_lines.append(line.rstrip())
    except FileNotFoundError:
        pass

    return info


def find_job_files(job_name: str, search_dir: str = ".") -> dict[str, str]:
    """查找作业相关的文件。"""
    files = {}
    search_path = Path(search_dir)

    for ext in (".sta", ".msg", ".inp", ".odb", ".dat", ".log"):
        candidate = search_path / f"{job_name}{ext}"
        if candidate.exists():
            files[ext.lstrip(".")] = str(candidate)

    return files


def format_status(status: JobStatus, msg_info: Optional[MsgInfo] = None) -> str:
    """格式化作业状态为可读字符串。"""
    status_icons = {
        "COMPLETED": "DONE",
        "TERMINATED": "TERM",
        "RUNNING": "RUN",
        "ABORTED": "ABRT",
        "UNKNOWN": "????",
        "FILE_NOT_FOUND": "MISS",
    }
    icon = status_icons.get(status.status, "????")

    lines = [
        f"[{icon}] {status.job_name}",
        f"  状态: {status.status}",
        f"  增量步: {status.iterations}",
        f"  警告: {status.warnings}",
    ]

    if status.odb_file and os.path.exists(status.odb_file):
        size_mb = os.path.getsize(status.odb_file) / (1024 * 1024)
        lines.append(f"  ODB: {status.odb_file} ({size_mb:.1f} MB)")

    if msg_info:
        if msg_info.error_lines:
            lines.append(f"  错误 ({len(msg_info.error_lines)}):")
            for err in msg_info.error_lines[:5]:
                lines.append(f"    {err}")
            if len(msg_info.error_lines) > 5:
                lines.append(f"    ... 还有 {len(msg_info.error_lines) - 5} 条错误")

        if msg_info.warning_lines:
            lines.append(f"  警告 ({len(msg_info.warning_lines)}):")
            for warn in msg_info.warning_lines[:3]:
                lines.append(f"    {warn}")
            if len(msg_info.warning_lines) > 3:
                lines.append(f"    ... 还有 {len(msg_info.warning_lines) - 3} 条警告")

    return "\n".join(lines)


def monitor_jobs(
    job_names: list[str],
    search_dir: str = ".",
    watch: bool = False,
    interval: int = 10,
) -> list[JobStatus]:
    """监控一个或多个作业。"""
    results = []

    while True:
        results.clear()
        for job_name in job_names:
            files = find_job_files(job_name, search_dir)

            status = parse_sta_file(files.get("sta", f"{search_dir}/{job_name}.sta"))
            status.odb_file = files.get("odb", "")

            msg_info = None
            if "msg" in files:
                msg_info = parse_msg_file(files["msg"])
                if msg_info:
                    status.errors = len(msg_info.error_lines)

            results.append(status)
            print(format_status(status, msg_info))
            print()

        if not watch:
            break

        # 检查是否所有作业都已结束
        all_done = all(s.status in ("COMPLETED", "TERMINATED", "ABORTED", "FILE_NOT_FOUND") for s in results)
        if all_done:
            print("所有作业已结束。")
            break

        print(f"--- 等待 {interval} 秒后刷新 ---")
        time.sleep(interval)

    return results


def main():
    parser = argparse.ArgumentParser(description="Abaqus 作业监控器")
    parser.add_argument("jobs", nargs="+", help="作业名称（不含扩展名）")
    parser.add_argument("--dir", default=".", help="搜索目录 (默认: 当前目录)")
    parser.add_argument("--watch", "-w", action="store_true", help="持续监控模式")
    parser.add_argument("--interval", "-i", type=int, default=10, help="刷新间隔秒数 (默认: 10)")
    args = parser.parse_args()

    monitor_jobs(args.jobs, args.dir, args.watch, args.interval)


if __name__ == "__main__":
    main()
