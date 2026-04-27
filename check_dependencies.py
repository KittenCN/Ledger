"""检查系统依赖"""
import sys
import winreg
import ctypes


def check_dotnet_framework():
    """检查 .NET Framework 4.7.2+"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full")
        release, _ = winreg.QueryValueEx(key, "Release")
        winreg.CloseKey(key)
        return release >= 461808  # .NET Framework 4.7.2
    except:
        return False


def check_webview2_runtime():
    """检查 WebView2 Runtime"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}")
        winreg.CloseKey(key)
        return True
    except:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}")
            winreg.CloseKey(key)
            return True
        except:
            return False


def show_error_message(title, message):
    """显示错误对话框"""
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)


def check_all_dependencies():
    """检查所有依赖，返回 True 表示通过"""
    missing = []

    if not check_dotnet_framework():
        missing.append(".NET Framework 4.7.2 或更高版本")

    if not check_webview2_runtime():
        missing.append("Microsoft Edge WebView2 Runtime")

    if missing:
        message = "缺少必要组件，应用无法启动：\n\n"
        for item in missing:
            message += f"  • {item}\n"
        message += "\n请访问以下链接下载安装：\n"
        message += ".NET Framework: https://dotnet.microsoft.com/download/dotnet-framework\n"
        message += "WebView2 Runtime: https://go.microsoft.com/fwlink/p/?LinkId=2124703"

        show_error_message("缺少系统组件", message)
        return False

    return True
