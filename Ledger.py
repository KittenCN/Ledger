import webview
import os
import sys
from pathlib import Path

BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, 'resource', 'IconGroup1.ico')
ACTIVATION_KEY = 'TJJtds@1q2w3e'
ACTIVATION_FILE_NAMES = ('activation.config', 'activation.txt', 'license.key')


def is_activated():
    for directory in (BASE_DIR, os.path.join(BASE_DIR, 'resource')):
        for file_name in ACTIVATION_FILE_NAMES:
            config_path = os.path.join(directory, file_name)
            if not os.path.isfile(config_path):
                continue

            try:
                with open(config_path, 'r', encoding='utf-8') as config_file:
                    return config_file.readline().strip() == ACTIVATION_KEY
            except OSError:
                return False

    return False

def create_window():
    # 确保文件路径正确
    activated = '1' if is_activated() else '0'
    html_path = f"{Path(BASE_DIR, 'resource', 'App.html').as_uri()}#activated={activated}"
    # 创建一个窗口并加载HTML页面
    webview.create_window('Ledger APP', html_path, fullscreen=False, js_api=True, maximized=True)

if __name__ == '__main__':
    create_window()
    webview.start(icon=ICON_PATH)
