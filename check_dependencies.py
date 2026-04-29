"""Runtime dependency checks for the packaged Windows app."""
import ctypes
import winreg


WEBVIEW2_CLIENT_KEYS = (
    r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
    r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
)


def check_dotnet_framework():
    """Check for .NET Framework 4.8+."""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full")
        release, _ = winreg.QueryValueEx(key, "Release")
        winreg.CloseKey(key)
        return release >= 528040
    except OSError:
        return False


def check_webview2_runtime():
    """Check for Microsoft Edge WebView2 Runtime."""
    for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
        for key_path in WEBVIEW2_CLIENT_KEYS:
            try:
                key = winreg.OpenKey(hive, key_path)
                winreg.CloseKey(key)
                return True
            except OSError:
                pass

    return False


def show_error_message(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)


def check_all_dependencies():
    missing = []

    if not check_dotnet_framework():
        missing.append(".NET Framework 4.8 or higher")

    if not check_webview2_runtime():
        missing.append("Microsoft Edge WebView2 Runtime")

    if missing:
        message = "Ledger cannot start because required components are missing:\n\n"
        for item in missing:
            message += f"  - {item}\n"
        message += "\nInstall links:\n"
        message += ".NET Framework: https://dotnet.microsoft.com/download/dotnet-framework\n"
        message += "WebView2 Runtime: https://go.microsoft.com/fwlink/p/?LinkId=2124703"

        show_error_message("Missing system components", message)
        return False

    return True
