import os
import sys
from pathlib import Path

from check_dependencies import check_all_dependencies

# 检查系统依赖
if not check_all_dependencies():
    sys.exit(1)

import webview

from ledger_runtime import get_runtime_resource_dir


BASE_DIR = Path(sys.executable).resolve().parent if getattr(sys, "frozen", False) else Path(__file__).resolve().parent
RESOURCE_DIR = get_runtime_resource_dir()
ICON_PATH = RESOURCE_DIR / "IconGroup1.ico"
ACTIVATION_KEY = "TJJtds@1q2w3e"
ACTIVATION_FILE_NAMES = ("activation.config", "activation.txt", "license.key")


def is_activated():
    for directory in (BASE_DIR, BASE_DIR / "resource"):
        for file_name in ACTIVATION_FILE_NAMES:
            config_path = directory / file_name
            if not config_path.is_file():
                continue

            try:
                with open(config_path, "r", encoding="utf-8") as config_file:
                    return config_file.readline().strip() == ACTIVATION_KEY
            except OSError:
                return False

    return False


def create_window():
    activated = "1" if is_activated() else "0"
    html_path = f"{(RESOURCE_DIR / 'App.html').as_uri()}#activated={activated}"
    webview.create_window("Ledger APP", html_path, fullscreen=False, js_api=True, maximized=True)


if __name__ == "__main__":
    create_window()
    webview.start(icon=str(ICON_PATH))
