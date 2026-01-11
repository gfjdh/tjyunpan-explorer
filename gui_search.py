import sys
import os
import json
import re
import tkinter as tk
from tkinter import ttk, messagebox

# --- 配置区域 ---
DEFAULT_INSTRUCTION = """使用说明：
1. 在下方输入框中输入搜索关键词。
2. 支持正则表达式搜索，例如：
   - 搜索以"2023"开头的文件：^2023
   - 搜索所有PDF文件：\.pdf$
"""
# ----------------

def resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和PyInstaller打包后的环境 """
    try:
        # PyInstaller 创建临时文件夹，将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class YunpanSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("同济云盘检索工具")
        self.root.geometry("800x600")

        # 加载数据
        self.data_file = "tj_yunpan_tree.json"
        self.tree_data = self.load_data()

        self.create_widgets()

    def load_data(self):
        """ 加载JSON数据 """
        path = resource_path(self.data_file)
        try:
            if not os.path.exists(path):
                # 如果是打包环境，可能在上一级目录或其他位置，但在 --onefile 模式下通常在 _MEIPASS
                # 这里只处理最基本的找不到的情况
                raise FileNotFoundError(f"文件未找到: {path}")
                
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"无法加载数据文件:\n{path}\n\n错误信息:\n{e}")
            return {}

    def create_widgets(self):
        # 1. 使用说明区域
        instruction_frame = tk.LabelFrame(self.root, text="使用说明", padx=10, pady=10)
        instruction_frame.pack(fill="x", padx=10, pady=5)
        
        # 使用 Text 组件以便用户（开发者）之后容易编辑多行文本，并设置为只读
        self.instr_text_widget = tk.Text(instruction_frame, height=6, bg="#f0f0f0", relief="flat")
        self.instr_text_widget.pack(fill="both", expand=True)
        self.instr_text_widget.insert("1.0", DEFAULT_INSTRUCTION)
        self.instr_text_widget.config(state="disabled") # 设置为只读

        # 2. 搜索区域
        search_frame = tk.Frame(self.root, padx=5, pady=5)
        search_frame.pack(fill="x", padx=5)

        tk.Label(search_frame, text="搜索内容 (正则):", font=("Microsoft YaHei", 10)).pack(side="left", padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=("Microsoft YaHei", 10))
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind('<Return>', self.on_search)

        search_btn = tk.Button(search_frame, text="🔍 搜索", command=self.on_search, font=("Microsoft YaHei", 10), width=10)
        search_btn.pack(side="left", padx=5)

        # 3. 结果展示区域
        result_frame = tk.LabelFrame(self.root, text="搜索结果", padx=5, pady=5)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("type", "path")
        self.result_tree = ttk.Treeview(result_frame, columns=columns, show="headings", selectmode="browse")
        
        self.result_tree.heading("type", text="类型")
        self.result_tree.heading("path", text="完整路径")
        
        self.result_tree.column("type", width=80, minwidth=80, stretch=False, anchor="center")
        self.result_tree.column("path", width=600, minwidth=200, anchor="w")

        # 滚动条
        y_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_tree.yview)
        x_scrollbar = ttk.Scrollbar(result_frame, orient="horizontal", command=self.result_tree.xview)
        
        self.result_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        y_scrollbar.pack(side="right", fill="y")
        x_scrollbar.pack(side="bottom", fill="x")
        self.result_tree.pack(fill="both", expand=True)

        # 4. 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("准备就绪")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W, padx=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_search(self, event=None):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入搜索内容")
            return

        # 清空现有结果
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)

        self.status_var.set("正在搜索...")
        self.root.update_idletasks()

        try:
            pattern = re.compile(query, re.IGNORECASE)
        except re.error as e:
            messagebox.showerror("正则表达式错误", f"无效的正则表达式:\n{e}")
            self.status_var.set("搜索出错")
            return

        results = []
        # 开始递归搜索
        self.search_recursive(self.tree_data, "", pattern, results)

        # 填充结果
        for item_type, path in results:
            # 简单的图标代替文字会更直观，但TreeView默认主要支持文字，这里用文字
            display_type = "📁 文件夹" if item_type == "folder" else "📄 文件"
            self.result_tree.insert("", "end", values=(display_type, path))

        self.status_var.set(f"搜索完成，共找到 {len(results)} 个匹配项")

    def search_recursive(self, node, current_path, pattern, results):
        if not isinstance(node, dict):
            return

        for key, value in node.items():
            # 构建当前路径
            # 注意：JSON树的第一层就是根目录名
            path = f"{current_path}/{key}" if current_path else key
            
            item_type = value.get("type", "unknown")

            # 匹配检查
            if pattern.search(key):
                results.append((item_type, path))
            
            # 如果是文件夹且有子节点，继续递归
            if item_type == "folder" and "children" in value:
                self.search_recursive(value["children"], path, pattern, results)

if __name__ == "__main__":
    root = tk.Tk()
    # 尝试设置图标（如果有的话），这里跳过
    app = YunpanSearchApp(root)
    root.mainloop()
