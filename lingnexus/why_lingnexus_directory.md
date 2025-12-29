# 为什么需要 `lingnexus` 目录？

## 原因

`lingnexus` 目录是为了满足 `uv sync` 和 `hatchling` 构建系统的要求。

### 技术原因

1. **`uv sync` 的行为**：
   - `uv sync` 会尝试将项目构建为一个可编辑安装的 Python 包
   - 它使用 `hatchling` 作为构建后端

2. **`hatchling` 的要求**：
   - `hatchling` 需要找到一个与项目名称（`lingnexus`）匹配的包目录
   - 如果找不到，构建会失败并报错：
     ```
     ValueError: Unable to determine which files to ship inside the wheel
     The most likely cause is that there is no directory that matches
     the name of your project (lingnexus).
     ```

3. **`pyproject.toml` 配置**：
   ```toml
   [tool.hatch.build.targets.wheel]
   packages = ["lingnexus"]  # 必须与项目名称匹配
   ```

## 当前状态

- ✅ **必需**：`uv sync` 需要它来成功构建项目
- 📦 **用途**：目前仅作为占位符，满足构建要求
- 🔮 **未来**：可以作为项目的 Python 包入口，存放共享代码

## 如果不需要这个目录

如果你不想有这个目录，有几个选择：

### 选项 1：保留它（推荐）
- 最简单，满足构建要求
- 未来可以作为项目的 Python 包入口
- 不影响项目功能

### 选项 2：改为应用模式
- 需要调整 `pyproject.toml`，移除 `build-system` 配置
- 但 `uv sync` 可能仍然需要它
- 更复杂，可能带来其他问题

### 选项 3：使用不同的项目结构
- 将项目改为纯应用（不使用包管理）
- 但会失去 `uv` 的依赖管理优势

## 建议

**保留 `lingnexus` 目录**，因为：
1. 它满足构建系统的要求
2. 不影响项目功能
3. 未来可以作为项目的 Python 包入口
4. 符合 Python 项目的最佳实践

## 参考

- [Hatchling 文档](https://hatch.pypa.io/latest/config/build/)
- [uv 文档](https://docs.astral.sh/uv/)

