import sys
from pathlib import Path
from tools.embed_resources import build_resource_module

ROOT = Path(__file__).resolve().parent
RESOURCE_DIR = ROOT / "resource"
ICON_FILE = RESOURCE_DIR / "IconGroup1.ico"
EMBEDDED_RESOURCE_MODULE = ROOT / "ledger_embedded_resources.py"
RTHOOK = ROOT / "rthook_ctypes.py"

# 构建嵌入式资源模块
build_resource_module(RESOURCE_DIR, EMBEDDED_RESOURCE_MODULE)

# 查找 Python DLL 和 pythonnet DLL
add_binary = []
add_data = []

# -----------------------------------------------------------------------
# 关键修复：
# 1. 用 sys.base_exec_prefix（基础 Python 安装目录）而非 sys.executable
#    的父目录来查找 DLL（venv 中 sys.executable 指向 .venv/Scripts/python.exe）
# 2. conda 环境的 libffi 叫 ffi.dll，位于 {base}/Library/bin/ 而非 DLLs/
#    标准 CPython 的 libffi 叫 libffi-7.dll / libffi-8.dll，位于 DLLs/
# -----------------------------------------------------------------------
python_base_dir = Path(sys.base_exec_prefix)

print(f"Python base: {python_base_dir}")

# 所有需要扫描的目录（兼容标准 CPython 和 conda）
dll_search_dirs = [
    python_base_dir,                      # python313.dll 在根目录
    python_base_dir / "DLLs",             # 标准 CPython: libffi-7.dll 在此
    python_base_dir / "Library" / "bin",  # conda: ffi.dll 在此
]

# 需要包含的 DLL 文件名（精确匹配，不遗漏也不过度包含）
CRITICAL_DLL_NAMES = {
    "ffi.dll",         # conda Python 3.13 _ctypes 依赖
    "libffi-7.dll",    # 标准 CPython 3.8-3.10
    "libffi-8.dll",    # 标准 CPython 3.11+
}

# 也收集 python*.dll（python313.dll 等），PyInstaller 有时会漏掉
def _glob_case_insensitive(directory: Path, pattern: str):
    pattern_lower = pattern.lower()
    try:
        for f in directory.iterdir():
            if f.is_file() and f.name.lower().startswith(pattern_lower.rstrip("*")):
                yield f
    except OSError:
        pass

seen_dlls: set = set()

for search_dir in dll_search_dirs:
    if not search_dir.is_dir():
        continue
    try:
        for dll_file in search_dir.iterdir():
            if not dll_file.is_file():
                continue
            name_lower = dll_file.name.lower()
            if name_lower in seen_dlls:
                continue
            # 精确名称匹配
            if dll_file.name in CRITICAL_DLL_NAMES:
                add_binary.append(f"{dll_file};.")
                seen_dlls.add(name_lower)
                print(f"Including critical DLL: {dll_file} -> .")
            # python3XX.dll（主解释器 DLL）
            elif name_lower.startswith("python3") and name_lower.endswith(".dll"):
                add_binary.append(f"{dll_file};.")
                seen_dlls.add(name_lower)
                print(f"Including Python DLL: {dll_file} -> .")
    except OSError:
        pass

# 查找 pythonnet DLL 文件
try:
    import pythonnet
    pythonnet_path = Path(pythonnet.__file__).parent
    runtime_dir = pythonnet_path / "runtime"
    if runtime_dir.exists():
        for dll_file in runtime_dir.glob("*.dll"):
            add_data.append(f"{dll_file};pythonnet/runtime")
            print(f"Including pythonnet DLL: {dll_file.name}")
except ImportError:
    print("Warning: pythonnet not installed")

# PyInstaller 参数
args = [
    "Ledger.py",
    "--name=Ledger",
    "--windowed",
    f"--icon={ICON_FILE}",
    "--onedir",
    "--clean",
    "--noconfirm",
    f"--distpath={ROOT / 'build'}",
    f"--workpath={ROOT / 'build' / 'temp'}",
    f"--specpath={ROOT / 'build'}",
    # -----------------------------------------------------------------------
    # 运行时 hook：在 Python 加载任何模块前，把 _internal/ 目录加入
    # os.add_dll_directory()，解决 Python 3.8+ Windows DLL 搜索策略变更问题。
    # -----------------------------------------------------------------------
    f"--runtime-hook={RTHOOK}",
    "--hidden-import=ledger_embedded_resources",
    "--hidden-import=webview.platforms.edgechromium",
    "--hidden-import=webview.platforms.mshtml",
    "--hidden-import=webview.platforms.winforms",
    "--hidden-import=clr",
    "--hidden-import=clr_loader",
    "--hidden-import=pythonnet",
    "--hidden-import=_ctypes",
    "--hidden-import=ctypes",
    "--hidden-import=winreg",
    "--collect-all=pythonnet",
    "--collect-all=clr_loader",
    # 让 PyInstaller 自动收集 ctypes 模块的所有二进制依赖
    "--collect-binaries=ctypes",
    "--noupx",
]

# 添加关键 Python DLL
for binary in add_binary:
    args.append(f"--add-binary={binary}")

# 添加 pythonnet DLL
for data in add_data:
    args.append(f"--add-data={data}")

# 运行 PyInstaller
try:
    import PyInstaller.__main__  # type: ignore
    PyInstaller.__main__.run(args)
except ImportError:
    print("Error: PyInstaller not installed. Run: pip install pyinstaller")
    exit(1)
