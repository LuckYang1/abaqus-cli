---
name: abaqus-compile
description: 编译 Abaqus 用户子程序（Fortran/C/C++）
---

# /abaqus-compile — 子程序编译

使用此命令编译 Abaqus 用户子程序。

## 使用方式

用户提供子程序源文件。你需要：

1. 调用 `abaqus make` 编译子程序
2. 支持 standard（默认）、explicit、cfd 求解器类型
3. 编译结果生成 `.obj` 或 `.so` 文件

## 编译流程

```
用户: /abaqus-compile UMAT.for

1. 检测源文件语言（Fortran/C/C++）
2. 调用 abaqus make
3. 输出编译结果
```

## 指定求解器

```
用户: /abaqus-compile VUMAT.for --explicit

调用 abaqus make library=vumat.for explicit
```

## 可用子程序类型

| 子程序 | 求解器 | 用途 |
|--------|--------|------|
| UMAT | Standard | 用户材料 |
| VUMAT | Explicit | 用户材料 |
| UEL | Standard | 用户单元 |
| VUEL | Explicit | 用户单元 |
| UEXPAN | Standard | 热膨胀 |
| UHARD | Standard | 硬化 |
| USDFLD | Standard | 场依赖 |
| UTRACLOAD | Standard | 分布载荷 |
| DLOAD | Standard | 分布载荷 |
| UVARM | Standard | 用户输出变量 |

## 前提条件

- 系统需安装 Fortran 编译器（Intel Fortran 或 gfortran）
- 编译器需与 Abaqus 版本兼容
- 编译器路径需在系统 PATH 中

## 常见错误

- **找不到编译器**: 确保 Fortran 编译器已安装并配置
- **版本不兼容**: 检查编译器与 Abaqus 版本的兼容性
- **语法错误**: 检查子程序源代码语法
