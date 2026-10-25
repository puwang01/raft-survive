# Godot 工程（正式可玩构建）

**引擎：Godot 4.7.2** · 第 1 关垂直切片（抛钩打捞 + 三维生存条 + 存档）

## 打开工程

1. 安装 [Godot 4.7+](https://godotengine.org/download)
2. 导入本目录（含 `project.godot`）
3. 按 F5 运行

## 导出 Android

本仓库已提供预编译 debug APK，见仓库根目录 `dist/` 或 GitHub Release。

自行导出：

1. 编辑器 → 编辑器设置 → Export → Android：配置 JDK / Android SDK
2. 项目 → 导出 → Android → 导出项目

## 画面（v0.2.1 精修）

- 晴朗白天天空 + 太阳光晕与云层
- 水面着色器（波浪 / 泡沫 / 焦散）
- 木筏：木板纹理、白帆、烧烤架（烤鱼）、木箱、集水器、床垫、角色与钩子
- 漂流物：浮木 / 木桶 / 木箱 / 鱼 / 水瓶；水下珊瑚
- HUD：生命/饥饿/口渴条、DAY/天气、目标、底部 8 格物品栏与大按钮
