# Godot 4 项目骨架

引擎选择仍为 **Godot 4**。当前可立即试玩的是仓库根下的 [`../play/`](../play/) HTML5 原型（无需安装 Godot）。

## 打开方式

1. 安装 [Godot 4.2+](https://godotengine.org/download/)
2. 项目管理器 → **导入** → 选择本目录的 `project.godot`
3. 主场景：`scenes/boot/boot.tscn`（占位）

## 目录（与 docs/06 对齐）

```
godot/
├── project.godot
├── scenes/   boot, meta, level, raft, hook, items, ui
├── scripts/  systems, data, util
├── assets/   art, audio, fonts
├── resources/
└── saves/
```

下一步：把 `play/index.html` 中已验证的 Level 1 循环（抛钩、三维生存、浮木目标、鲨、存档）迁入对应场景与 `SurvivalSystem` / `HookController` / `SaveService`。
