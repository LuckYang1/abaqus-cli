#!/usr/bin/env python3
"""Abaqus ODB 数据提取器 — 从输出数据库中提取场/历史数据。"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


# 用于生成 Abaqus Python 提取脚本的模板
ODB_EXTRACT_TEMPLATE = """\
# -*- coding: utf-8 -*-
\"\"\"自动生成的 ODB 数据提取脚本。\"\"\"
from odbAccess import *
from abaqusConstants import *
import csv

odb_path = r'{odb_path}'
output_file = r'{output_file}'

odb = openOdb(path=odb_path, readOnly=True)

# 提取场输出
step = odb.steps['{step_name}']
frame_index = {frame_index}
frame = step.frames[frame_index]

field = frame.fieldOutputs['{field_name}']

with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['node_or_element', 'label', 'value_1', 'value_2', 'value_3'])
    for val in field.values:
        components = val.data if hasattr(val.data, '__len__') else [val.data]
        row = [val.instance.name if val.instance else 'ASSEMBLY', val.nodeLabel or val.elementLabel]
        row.extend(list(components)[:3])
        while len(row) < 5:
            row.append('')
        writer.writerow(row)

print("场输出已写入: {{}}".format(output_file))
odb.close()
"""


def _cmd_not_found(abaqus_cmd: str, cmd: list[str]) -> subprocess.CompletedProcess:
    """返回命令未找到的标准错误结果。"""
    return subprocess.CompletedProcess(
        args=cmd, returncode=127,
        stdout="", stderr=f"命令 '{abaqus_cmd}' 未找到。请确认 Abaqus 已安装且在 PATH 中。",
    )


def run_odbreport(
    odb_path: str,
    output: Optional[str] = None,
    abaqus_cmd: str = "abaqus",
) -> subprocess.CompletedProcess:
    """调用 abaqus odbreport 生成 ODB 报告。"""
    if not os.path.exists(odb_path):
        raise FileNotFoundError(f"ODB 文件不存在: {odb_path}")

    cmd = [abaqus_cmd, "odbreport", f"odb={odb_path}"]
    if output:
        cmd.append(f"results={output}")

    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        return _cmd_not_found(abaqus_cmd, cmd)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            args=cmd, returncode=124,
            stdout="", stderr="命令执行超时 (300s)",
        )


def extract_field_output(
    odb_path: str,
    step_name: str = "Step-1",
    frame_index: int = -1,
    field_name: str = "S",
    output_file: Optional[str] = None,
    abaqus_cmd: str = "abaqus",
) -> str:
    """从 ODB 提取场输出数据到 CSV 文件。

    生成一个 Abaqus Python 脚本并执行。
    """
    if not os.path.exists(odb_path):
        raise FileNotFoundError(f"ODB 文件不存在: {odb_path}")

    if output_file is None:
        stem = Path(odb_path).stem
        output_file = f"{stem}_{field_name}_{step_name}.csv"

    # 生成提取脚本
    script_content = ODB_EXTRACT_TEMPLATE.format(
        odb_path=odb_path,
        output_file=output_file,
        step_name=step_name,
        frame_index=frame_index,
        field_name=field_name,
    )

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(script_content)
        script_path = tmp.name

    try:
        try:
            result = subprocess.run(
                [abaqus_cmd, "python", script_path],
                capture_output=True,
                text=True,
                timeout=600,
            )
        except FileNotFoundError:
            print(f"错误: 命令 '{abaqus_cmd}' 未找到。请确认 Abaqus 已安装且在 PATH 中。", file=sys.stderr)
            return ""
        except subprocess.TimeoutExpired:
            print("错误: 命令执行超时 (600s)", file=sys.stderr)
            return ""
        if result.returncode == 0:
            print(f"数据已提取到: {output_file}")
        else:
            print(f"提取失败: {result.stderr}", file=sys.stderr)
        return result.stdout
    finally:
        os.unlink(script_path)


def run_odb2sim(
    odb_path: str,
    output: Optional[str] = None,
    abaqus_cmd: str = "abaqus",
) -> subprocess.CompletedProcess:
    """将 ODB 转换为 Simpack 格式。"""
    if not os.path.exists(odb_path):
        raise FileNotFoundError(f"ODB 文件不存在: {odb_path}")

    cmd = [abaqus_cmd, "odb2sim", f"odb={odb_path}"]
    if output:
        cmd.append(f"output={output}")

    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        return _cmd_not_found(abaqus_cmd, cmd)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            args=cmd, returncode=124,
            stdout="", stderr="命令执行超时 (300s)",
        )


def run_restartjoin(
    output: str,
    input_files: list[str],
    abaqus_cmd: str = "abaqus",
) -> subprocess.CompletedProcess:
    """合并重启动文件。"""
    cmd = [abaqus_cmd, "restartjoin", f"output={output}"]
    for inp in input_files:
        cmd.append(f"input={inp}")

    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except FileNotFoundError:
        return _cmd_not_found(abaqus_cmd, cmd)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            args=cmd, returncode=124,
            stdout="", stderr="命令执行超时 (600s)",
        )


def main():
    parser = argparse.ArgumentParser(description="Abaqus ODB 数据提取器")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # odbreport
    p_report = subparsers.add_parser("report", help="生成 ODB 报告")
    p_report.add_argument("odb", help="ODB 文件路径")
    p_report.add_argument("--output", help="输出文件路径")
    p_report.add_argument("--abaqus-cmd", default="abaqus", help="Abaqus 命令名")

    # extract
    p_extract = subparsers.add_parser("extract", help="提取场输出到 CSV")
    p_extract.add_argument("odb", help="ODB 文件路径")
    p_extract.add_argument("--step", default="Step-1", help="分析步名称")
    p_extract.add_argument("--frame", type=int, default=-1, help="帧索引")
    p_extract.add_argument("--field", default="S", help="场输出变量名")
    p_extract.add_argument("--output", help="输出 CSV 路径")
    p_extract.add_argument("--abaqus-cmd", default="abaqus", help="Abaqus 命令名")

    # odb2sim
    p_sim = subparsers.add_parser("odb2sim", help="ODB 转 Simpack")
    p_sim.add_argument("odb", help="ODB 文件路径")
    p_sim.add_argument("--output", help="输出文件路径")
    p_sim.add_argument("--abaqus-cmd", default="abaqus", help="Abaqus 命令名")

    # restartjoin
    p_join = subparsers.add_parser("restartjoin", help="合并重启动文件")
    p_join.add_argument("--output", required=True, help="输出文件名")
    p_join.add_argument("--input", dest="inputs", action="append", required=True, help="输入文件（可多次指定）")
    p_join.add_argument("--abaqus-cmd", default="abaqus", help="Abaqus 命令名")

    args = parser.parse_args()

    if args.command == "report":
        result = run_odbreport(args.odb, args.output, args.abaqus_cmd)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    elif args.command == "extract":
        extract_field_output(args.odb, args.step, args.frame, args.field, args.output, args.abaqus_cmd)

    elif args.command == "odb2sim":
        result = run_odb2sim(args.odb, args.output, args.abaqus_cmd)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    elif args.command == "restartjoin":
        result = run_restartjoin(args.output, args.inputs, args.abaqus_cmd)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        sys.exit(result.returncode)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
