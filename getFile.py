import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class AnyShareCrawler:
    def __init__(self, url):
        self.driver = webdriver.Edge()
        self.url = url
        self.wait = WebDriverWait(self.driver, 15)

    def get_all_items_with_scroll(self):
        """滚动获取当前目录下完整的条目列表"""
        print("正在滚动扫描完整列表...")
        items_dict = {}
        try:
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "as-controls-data-grid-body")))
            grid_body = self.driver.find_element(By.CLASS_NAME, "as-controls-data-grid-body")

            last_scroll_top = -1
            while True:
                # 获取当前可见的条目
                elements = self.driver.find_elements(By.CSS_SELECTOR, ".item-name.loaction-hover")
                for el in elements:
                    name = el.get_attribute("title")
                    if name:
                        # 常用文件后缀名列表
                        file_extensions = (
                            # 办公文档与文本
                            '.doc', '.docx', '.pdf', '.txt', '.rtf', '.odt', '.wps', '.pages', 
                            '.md', '.markdown', '.log', '.tex', '.epub', '.mobi',
                            # 表格与数据
                            '.xls', '.xlsx', '.csv', '.tsv', '.json', '.xml', '.yaml', '.yml', 
                            '.ini', '.toml', '.sql', '.db', '.mdb', '.accdb', '.ods',
                            # 演示文稿
                            '.ppt', '.pptx', '.key', '.odp', '.pps', '.ppsx',
                            # 图像
                            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.svg', 
                            '.webp', '.ico', '.psd', '.ai', '.eps', '.raw', '.heic',
                            # 音频
                            '.mp3', '.wav', '.aac', '.flac', '.ogg', '.wma', '.m4a', '.aiff', 
                            '.mid', '.midi', '.amr', '.opus',
                            # 视频
                            '.mp4', '.avi', '.mov', '.wmv', '.mkv', '.flv', '.webm', '.mpeg', 
                            '.mpg', '.m4v', '.3gp', '.ts', '.vob',
                            # 压缩与归档
                            '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', 
                            '.dmg', '.img', '.pkg', '.deb', '.rpm', '.jar', '.war', '.ear',
                            # 编程与代码
                            '.py', '.pyw', '.java', '.c', '.cpp', '.h', '.hpp', '.cs', '.js', 
                            '.ts', '.html', '.htm', '.css', '.scss', '.less', '.php', '.rb', 
                            '.go', '.rs', '.swift', '.kt', '.kts', '.sh', '.bat', '.ps1', '.ipynb',
                            '.cmd', '.pl', '.lua', '.vb', '.vbs', '.asm', '.dockerfile', '.yml', '.docker-compose',
                            # 系统与可执行
                            '.exe', '.msi', '.dll', '.sys', '.tmp', '.temp', '.bak', '.old', 
                            '.cfg', '.conf', '.reg', '.lnk', '.so', '.dylib', 
                            # 移动端与其他
                            '.apk', '.ipa', '.crdownload', '.torrent', '.crx', '.xpi'
                        )
                        
                        if name.lower().endswith(file_extensions):
                            items_dict[name] = "file"
                        elif "【" in name:
                            items_dict[name] = "folder"
                        else:
                            # 既无文件后缀，也不含文件夹特征字符，默认为文件夹
                            items_dict[name] = "folder"

                # 向下滚动
                self.driver.execute_script("arguments[0].scrollTop += arguments[0].offsetHeight;", grid_body)
                time.sleep(1.2)  # 等待虚拟列表渲染

                new_scroll_top = self.driver.execute_script("return arguments[0].scrollTop;", grid_body)
                if new_scroll_top == last_scroll_top:  # 无法再向下滚动
                    break
                last_scroll_top = new_scroll_top

            # 回到顶部以便后续操作（如果需要点击）
            self.driver.execute_script("arguments[0].scrollTop = 0;", grid_body)
            print(f"扫描完毕，共 {len(items_dict)} 条目")
            return items_dict
        except Exception as e:
            print(f"扫描失败: {e}")
            return {}

    def scroll_to_element(self, name):
        """在当前窗口滚动寻找并返回元素"""
        grid_body = self.driver.find_element(By.CLASS_NAME, "as-controls-data-grid-body")
        last_top = -1
        while True:
            try:
                el = self.driver.find_element(By.XPATH, f"//div[@title='{name}']")
                if el.is_displayed():
                    return el
            except:
                pass

            self.driver.execute_script("arguments[0].scrollTop += 200;", grid_body)
            time.sleep(0.5)
            new_top = self.driver.execute_script("return arguments[0].scrollTop;", grid_body)
            if new_top == last_top: return None
            last_top = new_top

    def crawl_recursive(self, current_node):
        """递归抓取函数"""
        # 1. 扫描当前层级
        items = self.get_all_items_with_scroll()
        parent_handle = self.driver.current_window_handle

        for name, item_type in items.items():
            if item_type == "folder":
                print(f"📂 准备处理文件夹: {name}")
                current_node[name] = {"type": "folder", "children": {}}

                try:
                    # --- 多窗口核心改进：克隆当前页面 ---
                    current_url = self.driver.current_url
                    self.driver.execute_script(f"window.open('{current_url}', '_blank');")

                    # 切换到新开的标签页
                    time.sleep(1)
                    new_handle = self.driver.window_handles[-1]
                    self.driver.switch_to.window(new_handle)

                    # 在新标签页中找到并进入文件夹
                    folder_el = self.scroll_to_element(name)
                    if folder_el:
                        # 使用 JS 点击进入
                        self.driver.execute_script("arguments[0].click();", folder_el)
                        time.sleep(2)  # 等待子文件夹内容加载

                        # 递归
                        self.crawl_recursive(current_node[name]["children"])

                    # 处理完毕，关闭子标签页，切回父标签页
                    self.driver.close()
                    self.driver.switch_to.window(parent_handle)
                    print(f"⬅️ 子目录 {name} 处理完毕，已切回父窗口")

                except Exception as e:
                    print(f"❌ 无法在新窗口处理 {name}: {e}")
                    # 万一失败了，尝试清理窗口
                    if len(self.driver.window_handles) > 1 and self.driver.current_window_handle != parent_handle:
                        self.driver.close()
                        self.driver.switch_to.window(parent_handle)
            else:
                print(f"📄 记录文件: {name}")
                current_node[name] = {"type": "file"}

    def run(self):
        print(f"🚀 开始爬取同济云盘 (多窗口克隆模式)...")
        self.driver.get(self.url)
        time.sleep(8)

        file_tree = {}
        try:
            self.crawl_recursive(file_tree)
        finally:
            with open("tj_yunpan_tree.json", "w", encoding="utf-8") as f:
                json.dump(file_tree, f, ensure_ascii=False, indent=4)
            print("✅ 任务结束，文件树已更新")
            # self.driver.quit()


if __name__ == "__main__":
    target_url = "https://yunpan.tongji.edu.cn/anyshare/zh-cn/link/AA1F2D357016FA4B61B53E66779AAC63FF?_tb=none"
    crawler = AnyShareCrawler(target_url)
    crawler.run()