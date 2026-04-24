import webview
import os
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, 'resource', 'IconGroup1.ico')

def create_window():
    # 确保文件路径正确
    html_path = Path(BASE_DIR, 'resource', 'App.html').as_uri()
    # 创建一个窗口并加载HTML页面
    webview.create_window('Ledger APP', html_path, fullscreen=False, js_api=True, maximized=True)

if __name__ == '__main__':
    create_window()
    webview.start(icon=ICON_PATH)
