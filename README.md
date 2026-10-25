# Raft Survive（紧张木筏求生）

手机 / iPad 上的**紧张向**海上木筏求生游戏。引擎：**Godot 4**。

> 一句话：在波涛与匮乏中，用最简单的触控抛钩打捞、撑过 3～5 分钟的短关卡。

## 试玩（Level 1 原型）

**现在就能玩**，无需安装 Godot：

1. 打开 [`play/index.html`](play/index.html)  
   或在 `play/` 目录执行：

   ```bash
   cd play && python3 -m http.server 8080
   ```

   浏览器访问 <http://localhost:8080/>

2. 详细说明见 **[play/README.md](play/README.md)**（触控操作、胜负条件、存档）。

| 内容 | 说明 |
|------|------|
| 可玩构建 | [`play/`](play/) — HTML5 / Canvas 第 1 关垂直切片 |
| Godot 骨架 | [`godot/`](godot/) — Godot 4 工程（`project.godot`），正式开发迁入此处 |

第 1 关：拖动瞄准抛钩 → 收集 **5 块浮木**（约 4 分钟）→ 盯住口渴 / 饥饿 / 生命，小心鲨鱼。

## 文档入口

完整设计文档见 **[docs/](docs/README.md)**。

| 文档 | 内容 |
|------|------|
| [01 愿景与定位](docs/01-game-vision.md) | 基调、平台、引擎、非目标 |
| [02 核心循环](docs/02-core-loop.md) | 抛钩→生存压力→短局结算 |
| [03 操作与 UX](docs/03-controls-and-ux.md) | 触控、大按钮、上手原则 |
| [04 关卡与节奏](docs/04-levels-and-pacing.md) | 3～5 分钟关卡、难度递进 |
| [05 存档系统](docs/05-save-system.md) | 手动存档 + 30s/60s 自动存档 |
| [06 Godot 项目结构](docs/06-godot-project-structure.md) | 目录与场景拆分建议 |
| [07 待定项](docs/07-open-questions.md) | 尚未拍板的设计决策 |

## 技术要点（摘要）

- **平台**：iPhone / Android 手机 + iPad
- **引擎**：Godot 4（2D 优先）；当前 try-now 为 HTML5 原型以便零安装试玩
- **基调**：紧张求生，非 cozy
- **单局时长**：每关 / 每段 **3～5 分钟**
- **存档**：允许手动存档；自动存档默认 **60 秒**（可选 30 秒）

## 许可

设计文档仅作项目规划用途；具体开源许可待项目代码阶段再定。
