import webview
import os

def create_window():
    # 确保文件路径正确
    html_path = 'file://' + os.path.abspath('./resource/App.html')
    # 创建一个窗口并加载HTML页面
    webview.create_window('Ledger APP', html_path, fullscreen=False, js_api=True, maximized=True)

if __name__ == '__main__':
    create_window()
    webview.start()
