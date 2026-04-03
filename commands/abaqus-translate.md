---
name: abaqus-translate
description: Abaqus 与其他求解器之间的文件格式转换
---

# /abaqus-translate — 文件翻译

使用此命令在 Abaqus 和其他有限元求解器之间转换模型文件。

## 使用方式

用户提供源文件和目标格式。你需要：

1. 调用 `scripts/abaqus_runner.py` 的 translate 类命令
2. 支持双向转换：导出到其他格式 / 从其他格式导入

## 支持的转换方向

### 导出（Abaqus → 其他）

| 命令 | 目标格式 | 说明 |
|------|----------|------|
| toNastran | Nastran (.bdf/.dat) | 导出为 Nastran 格式 |

### 导入（其他 → Abaqus）

| 命令 | 源格式 | 说明 |
|------|--------|------|
| fromNastran | Nastran (.bdf/.dat) | 从 Nastran 导入 |
| fromANSYS | ANSYS (.cdb/.inp) | 从 ANSYS 导入 |
| fromDyna | LS-DYNA (.k/.dyn) | 从 LS-DYNA 导入 |
| fromPamcrash | PAM-CRASH (.pc) | 从 PAM-CRASH 导入 |
| fromRadioss | RADIOSS (.rad) | 从 RADIOSS 导入 |
| fromMoldflow | Moldflow (.udm/.xml) | 从 Moldflow 导入 |
| fromSimpack | Simpack (.spd) | 从 Simpack 导入 |
| fromAdams | Adams (.adm) | 从 Adams 导入 |
| fromExcite | EXCITE (.dat) | 从 EXCITE 导入 |

## 执行示例

```
用户: /abaqus-translate toNastran model.inp

构建命令: abaqus toNastran input=model.inp
输出: model.bdf
```

```
用户: /abaqus-translate fromNastran nastran_model.bdf

构建命令: abaqus fromNastran input=nastran_model.bdf
```

```
用户: /abaqus-translate fromDyna dyna_model.k

构建命令: abaqus fromDyna input=dyna_model.k
```

## 注意事项

- 转换过程可能会丢失部分 Abaqus 特有特性
- 建议转换后使用 `/abaqus-run --datacheck` 验证模型完整性
- 某些高级材料模型可能无法完全转换
