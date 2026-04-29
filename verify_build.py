"""
验证打包后的应用程序是否包含所有必需的文件
"""
import sys
from pathlib import Path


def check_file(build_dir: Path, file_path: str, description: str) -> bool:
    """检查文件是否存在"""
    full_path = build_dir / file_path
    exists = full_path.exists()
    status = "[OK]" if exists else "[FAIL]"
    print(f"{status} {description}: {file_path}")
    return exists


def main():
    if len(sys.argv) > 1:
        build_dir = Path(sys.argv[1])
    else:
        build_dir = Path(__file__).parent / "build" / "Ledger"

    if not build_dir.exists():
        print(f"错误: 构建目录不存在: {build_dir}")
        return False

    print(f"检查构建目录: {build_dir}\n")

    all_ok = True

    # 检查主程序
    print("=== 主程序 ===")
    all_ok &= check_file(build_dir, "Ledger.exe", "主程序")
    all_ok &= check_file(build_dir, "python313.dll", "Python 运行时")
    all_ok &= check_file(build_dir, "ledger.runtimeconfig.json", "CoreCLR runtime config")

    # 检查 pythonnet
    print("\n=== pythonnet 依赖 ===")
    all_ok &= check_file(build_dir, "lib/Python.Runtime.dll", "Python.Runtime.dll (lib)")
    all_ok &= check_file(build_dir, "lib/pythonnet/runtime/Python.Runtime.dll", "Python.Runtime.dll (runtime)")

    # 检查 clr_loader
    print("\n=== CLR Loader ===")
    all_ok &= check_file(build_dir, "lib/clr_loader/ffi/dlls/amd64/ClrLoader.dll", "ClrLoader.dll (x64)")
    all_ok &= check_file(build_dir, "lib/clr_loader/ffi/dlls/x86/ClrLoader.dll", "ClrLoader.dll (x86)")

    # 检查 WebView2
    print("\n=== WebView2 组件 ===")
    all_ok &= check_file(build_dir, "lib/webview/lib/Microsoft.Web.WebView2.Core.dll", "WebView2 Core")
    all_ok &= check_file(build_dir, "lib/webview/lib/Microsoft.Web.WebView2.WinForms.dll", "WebView2 WinForms")
    all_ok &= check_file(build_dir, "lib/webview/lib/WebBrowserInterop.x64.dll", "WebBrowserInterop x64")
    all_ok &= check_file(build_dir, "lib/webview/lib/runtimes/win-x64/native/WebView2Loader.dll", "WebView2Loader x64")

    # 检查 Visual C++ 运行时
    print("\n=== Visual C++ 运行时 ===")
    all_ok &= check_file(build_dir, "vcruntime140.dll", "vcruntime140.dll")
    all_ok &= check_file(build_dir, "msvcp140.dll", "msvcp140.dll")

    # 检查应用模块
    print("\n=== 应用模块 ===")
    all_ok &= check_file(build_dir, "lib/library.zip", "Python 库文件")

    # 统计
    print("\n" + "="*50)
    if all_ok:
        print("[OK] All required files are included")
        print("\nWARNING: Target system still needs:")
        print("  1. .NET Framework 4.7.2 or higher")
        print("  2. .NET Desktop Runtime 6.0 or higher")
        print("  3. Microsoft Edge WebView2 Runtime")
        return True
    else:
        print("[FAIL] Missing required files, please check build configuration")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
