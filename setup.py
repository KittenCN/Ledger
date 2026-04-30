from pathlib import Path
import sys

from cx_Freeze import Executable, setup
from tools.embed_resources import build_resource_module


ROOT = Path(__file__).resolve().parent
RESOURCE_DIR = ROOT / "resource"
ICON_FILE = RESOURCE_DIR / "IconGroup1.ico"
EMBEDDED_RESOURCE_MODULE = ROOT / "ledger_embedded_resources.py"

build_resource_module(RESOURCE_DIR, EMBEDDED_RESOURCE_MODULE)

include_files = []

# -----------------------------------------------------------------------
# pythonnet runtime – Python.Runtime.dll + deps.json
# Path(__file__).parent is used at runtime to find Python.Runtime.dll,
# so it must land at  lib/pythonnet/runtime/  in the bundle.
# -----------------------------------------------------------------------
try:
    import pythonnet
    pythonnet_runtime_dir = Path(pythonnet.__file__).parent / "runtime"
    if pythonnet_runtime_dir.exists():
        for f in pythonnet_runtime_dir.iterdir():
            if f.is_file():
                include_files.append((str(f), f"lib/pythonnet/runtime/{f.name}"))
                print(f"Including pythonnet runtime: {f.name}")
    else:
        print("Warning: pythonnet runtime directory not found")
except ImportError:
    print("Warning: pythonnet not installed")

# -----------------------------------------------------------------------
# clr_loader native DLLs – ClrLoader.dll (amd64 + x86)
# clr_loader/ffi/__init__.py resolves these via Path(__file__).parent,
# so they must land at  lib/clr_loader/ffi/dlls/<arch>/  in the bundle.
# WITHOUT these DLLs, pyclr_get_function returns NULL and you get:
#   RuntimeError: Failed to resolve Python.Runtime.Loader.Initialize
# -----------------------------------------------------------------------
try:
    import clr_loader
    clr_dlls_dir = Path(clr_loader.__file__).parent / "ffi" / "dlls"
    if clr_dlls_dir.exists():
        for arch_dir in clr_dlls_dir.iterdir():
            if arch_dir.is_dir():
                for f in arch_dir.iterdir():
                    if f.is_file():
                        dest = f"lib/clr_loader/ffi/dlls/{arch_dir.name}/{f.name}"
                        include_files.append((str(f), dest))
                        print(f"Including clr_loader DLL: {arch_dir.name}/{f.name}")
    else:
        print("Warning: clr_loader ffi/dlls directory not found")
except ImportError:
    print("Warning: clr_loader not installed")

# -----------------------------------------------------------------------
# webview native DLLs – WebView2Loader.dll, WebBrowserInterop, etc.
# pywebview looks for its lib files at  os.path.dirname(webview.__file__)/lib/
# which maps to  lib/webview/lib/  inside the bundle.
# -----------------------------------------------------------------------
try:
    import webview as _wv
    webview_lib_dir = Path(_wv.__file__).parent / "lib"
    if webview_lib_dir.exists():
        for f in webview_lib_dir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(webview_lib_dir.parent)
                include_files.append((str(f), f"lib/{rel.as_posix()}"))
                print(f"Including webview lib: {rel}")
    else:
        print("Warning: webview/lib directory not found")
except ImportError:
    print("Warning: webview not installed")

build_exe_options = {
    "build_exe": str(ROOT / "build" / "Ledger"),
    "packages": ["webview", "clr", "pythonnet", "clr_loader"],
    "includes": [
        "ledger_embedded_resources",
        "webview.platforms.edgechromium",
        "webview.platforms.mshtml",
        "webview.platforms.winforms",
        "clr",
        "clr_loader",
        "clr_loader.ffi",
    ],
    "include_msvcr": True,
    "include_files": include_files,
    # Prevent critical packages from being ZIPped:
    # if they were inside library.zip, Path(__file__).parent would point
    # inside the ZIP and ffi.dlopen() / open() on those paths would fail.
    "zip_exclude_packages": ["clr_loader", "pythonnet", "webview", "cffi", "clr"],
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
