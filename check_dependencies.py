"""Runtime dependency checks for the packaged Windows app."""
from pathlib import Path
import ctypes
import os
import winreg


WEBVIEW2_CLIENT_KEYS = (
    r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
    r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
)


def check_dotnet_framework():
    """Check for .NET Framework 4.7.2+."""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full")
        release, _ = winreg.QueryValueEx(key, "Release")
        winreg.CloseKey(key)
        return release >= 461808
    except OSError:
        return False


def check_dotnet_desktop_runtime():
    """Check for Microsoft.WindowsDesktop.App 6.0+ used by pythonnet CoreCLR."""
    roots = []
    for env_name in ("ProgramFiles", "ProgramW6432"):
        program_files = os.environ.get(env_name)
        if program_files:
            roots.append(Path(program_files) / "dotnet" / "shared" / "Microsoft.WindowsDesktop.App")

    for root in roots:
        if not root.is_dir():
            continue

        for version_dir in root.iterdir():
            if not version_dir.is_dir():
                continue

            try:
                major = int(version_dir.name.split(".", 1)[0])
            except ValueError:
                continue

            if major >= 6:
                return True

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
        missing.append(".NET Framework 4.7.2 or higher")

    if not check_dotnet_desktop_runtime():
        missing.append(".NET Desktop Runtime 6.0 or higher")

    if not check_webview2_runtime():
        missing.append("Microsoft Edge WebView2 Runtime")

    if missing:
        message = "Ledger cannot start because required components are missing:\n\n"
        for item in missing:
            message += f"  - {item}\n"
        message += "\nInstall links:\n"
        message += ".NET Desktop Runtime: https://dotnet.microsoft.com/download/dotnet/6.0\n"
        message += ".NET Framework: https://dotnet.microsoft.com/download/dotnet-framework\n"
        message += "WebView2 Runtime: https://go.microsoft.com/fwlink/p/?LinkId=2124703"

        show_error_message("Missing system components", message)
        return False

    return True
