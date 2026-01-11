# 同济云盘检索工具 (Tongji Yunpan Search Tool)

本项目包含一个针对特定同济云盘分享链接的本地检索工具，以及用于获取文件目录结构的爬虫脚本。

主要用于快速检索云盘中的文件，支持正则表达式搜索，方便查找特定年份或特定类型的文件。

## 项目结构

*   `gui_search.py`: 图形界面搜索工具的主程序。
*   `getFile.py`: 基于 Selenium 的爬虫脚本，用于抓取云盘目录结构并保存为 JSON 文件。
*   `tj_yunpan_tree.json`: 数据文件，存储了云盘的文件目录结构（由爬虫生成）。
*   `build_exe.cmd`: 用于将 Python 脚本打包成 EXE 可执行文件的批处理脚本。

## 依赖环境

*   Python 3.x
*   依赖库：
    *   `selenium` (用于爬虫)
    *   `tkinter` (Python 内置，用于 GUI)
    *   `pyinstaller` (用于打包)

可以使用 pip 安装所需依赖：

```bash
pip install selenium pyinstaller
```

**注意**：`getFile.py` 默认使用 Edge 浏览器驱动 (`webdriver.Edge()`)，请确保你的系统已安装 Edge 浏览器及对应的 WebDriver（通常现代 Windows 系统自带及自动更新）。

## 使用说明

### 1. 更新数据 (可选)

如果你需要最新的文件列表，可以运行爬虫脚本：

```bash
python getFile.py
```

该脚本会自动打开 Edge 浏览器，访问预设的云盘链接，递归抓取所有文件名，最终生成/更新 `tj_yunpan_tree.json` 文件。

*注意：爬取过程可能需要较长时间，取决于云盘文件数量。脚本会自动处理滚动加载和文件夹递归。*

### 2. 运行搜索工具

直接运行 GUI 脚本启动图形界面：

```bash
python gui_search.py
```

### 3. 功能特性

*   **本地检索**：基于本地 JSON 数据，检索速度极快，无需联网。
*   **正则搜索**：支持 Python 正则表达式进行精准或模糊匹配。
    *   示例：搜索 2023 年开头的文件 `^2023`
    *   示例：搜索所有 PDF 文件 `\.pdf$`
*   **结果展示**：以列表形式清晰展示文件类型（文件/文件夹）和其在网盘中的完整路径。

### 4. 打包发布

如果你想将工具分享给其他不便安装 Python 环境的用户，可以使用提供的脚本打包成 EXE 文件：

双击运行 `build_exe.cmd`，或者在命令行执行：

```cmd
build_exe.cmd
```

脚本会自动安装 `pyinstaller`并执行打包命令。打包成功后，独立的可执行文件位于 `dist/YunpanSearchTool.exe`。

## 注意事项

*   **数据同步**：`YunpanSearchTool.exe`运行时依赖内部打包的 `json` 数据。如果云盘内容更新了，你需要重新运行 `getFile.py` 生成新的 json，并重新打包 exe。
*   **使用范围**：本工具仅供同济大学师生内部交流使用，请勿随意传播云盘链接或未公开的文件。

## 开源协议

MIT
