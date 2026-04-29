from pathlib import Path
from tools.embed_resources import build_resource_module

ROOT = Path(__file__).resolve().parent
RESOURCE_DIR = ROOT / "resource"
ICON_FILE = RESOURCE_DIR / "IconGroup1.ico"
EMBEDDED_RESOURCE_MODULE = ROOT / "ledger_embedded_resources.py"

# 构建嵌入式资源模块
build_resource_module(RESOURCE_DIR, EMBEDDED_RESOURCE_MODULE)

# 查找 pythonnet DLL 文件
add_data = []
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
    "--onefile",
    "--clean",
    "--noconfirm",
    f"--distpath={ROOT / 'build'}",
    f"--workpath={ROOT / 'build' / 'temp'}",
    f"--specpath={ROOT / 'build'}",
    "--hidden-import=ledger_embedded_resources",
    "--hidden-import=webview.platforms.edgechromium",
    "--hidden-import=webview.platforms.mshtml",
    "--hidden-import=webview.platforms.winforms",
    "--hidden-import=clr",
    "--hidden-import=clr_loader",
    "--hidden-import=pythonnet",
]

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
