from pathlib import Path
import sys

from cx_Freeze import Executable, setup
from tools.embed_resources import build_resource_module


ROOT = Path(__file__).resolve().parent
RESOURCE_DIR = ROOT / "resource"
ICON_FILE = RESOURCE_DIR / "IconGroup1.ico"
EMBEDDED_RESOURCE_MODULE = ROOT / "ledger_embedded_resources.py"

build_resource_module(RESOURCE_DIR, EMBEDDED_RESOURCE_MODULE)

# Find pythonnet DLL files
include_files = []
try:
    import pythonnet
    pythonnet_path = Path(pythonnet.__file__).parent
    runtime_dir = pythonnet_path / "runtime"
    if runtime_dir.exists():
        for dll_file in runtime_dir.glob("*.dll"):
            include_files.append((str(dll_file), f"lib/pythonnet/runtime/{dll_file.name}"))
            print(f"Including pythonnet DLL: {dll_file.name}")
    else:
        print("Warning: pythonnet runtime directory not found")
except ImportError:
    print("Warning: pythonnet not installed, skipping DLL inclusion")

build_exe_options = {
    "build_exe": str(ROOT / "build" / "Ledger"),
    "packages": ["webview", "clr", "pythonnet"],
    "includes": [
        "ledger_embedded_resources",
        "webview.platforms.edgechromium",
        "webview.platforms.mshtml",
        "webview.platforms.winforms",
        "clr",
        "clr_loader",
    ],
    "include_msvcr": True,
    "include_files": include_files,
}

base = "gui" if sys.platform == "win32" else None

executables = [
    Executable(
        script="Ledger.py",
        base=base,
        target_name="Ledger.exe",
        icon=str(ICON_FILE),
    )
]

setup(
    name="Ledger",
    version="1.0.0",
    description="Ledger desktop shell built with pywebview",
    options={"build_exe": build_exe_options},
    executables=executables,
)
