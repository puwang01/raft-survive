# Raft Survive（紧张木筏求生）

手机 / iPad 上的**紧张向**海上木筏求生。引擎：**Godot 4.7.2**。

> 一句话：在波涛与匮乏中，用最简单的触控抛钩打捞，撑过 3～5 分钟的短关卡。

## 安卓安装（推荐）

已导出 **debug APK**（可用调试签名侧载安装）。

| 获取方式 | 链接 |
|----------|------|
| GitHub Release | **[直接下载 APK](https://github.com/puwang01/raft-survive/releases/download/v0.2.3/RaftSurvive-level1-debug.apk)** |
| 仓库内文件 | [`dist/RaftSurvive-level1-debug.apk`](dist/RaftSurvive-level1-debug.apk) |

### 手机安装步骤

1. 用手机浏览器打开上述 APK 链接并下载（或用电脑下载后传到手机）。
2. **允许安装未知来源应用**：
   - 一般路径：`设置 → 安全 / 应用 → 安装未知应用`，对「文件管理 / Chrome / 浏览器」开启允许。
   - 部分国产系统：`设置 → 应用管理 → 特殊权限 → 安装未知应用`。
3. 打开下载的 `RaftSurvive-level1-debug.apk` → 安装 → 打开 **Raft Survive**。
4. 若系统提示「面向旧版 Android / 调试版」：点继续安装即可（debug 包用于试玩）。

包名：`com.puwang.raftsurvive` · 版本：`0.2.3`

### 操作

- **按住拖动**瞄准，**松手**抛钩；点「收回钩」可提前拉回。
- 目标：收集 **5 块浮木**（约 4 分钟时限）。
- 盯住 **生命 / 饥饿 / 口渴**；用「吃喝」消耗食物/淡水。
- 暂停里可**手动存档**；游戏中每 **60 秒**自动存档（进后台也会存）。

## 画面（相对旧 HTML 原型）

**v0.2.3** 对齐参考截图 + 显示适配：

- **角色**：侧视站立精灵（头上脚下、靴底阴影），甲板脚原点，不再读成趴卧/俯视
- **木筏**：近方形 3×3 粗圆木平台、绳结、金属护角；帆 / 蓝色集水桶 / 箱 / 烤鱼架 / 绿垫
- **海水**：半透明见底、表面涟漪与反光、焦散；海底轮廓 + 游动鱼群
- **显示**：Android edge-to-edge + 沉浸式、安全区避让刘海/状态栏；拉伸适配多分辨率，清色与背景对齐海水（去掉顶栏白条）
- HUD：按安全区 insets 缩进；相机随屏幕比例微调

## 工程与备选构建

| 内容 | 说明 |
|------|------|
| [`godot/`](godot/) | **正式 Godot 4 工程**（请用此目录继续开发） |
| [`dist/RaftSurvive-level1-debug.apk`](dist/RaftSurvive-level1-debug.apk) | Android 试玩包 |
| [Release 内 Linux 二进制](https://github.com/puwang01/raft-survive/releases/tag/v0.2.0-level1) | `RaftSurvive-level1.x86_64` + `.pck`（可选） |
| [`play/`](play/) | 旧 HTML5 原型（仅作对照，已非主交付） |
| [`docs/`](docs/) | 设计文档 |

本地用编辑器打开：`godot/project.godot`（Godot **4.7.2**）。

## 技术摘要

- **平台**：Android（已出包）/ 亦可导出 iOS、Web
- **引擎**：Godot **4.7.2**（2D + 水面着色器，mobile 渲染）
- **单局**：第 1 关约 **3～5 分钟**
- **存档**：手动 + 默认 **60 秒**自动 + 进后台强制存

## 文档

见 **[docs/](docs/README.md)**。

## 许可

设计与原型代码用途以仓库后续声明为准。
