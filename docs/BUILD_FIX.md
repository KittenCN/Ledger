# cx_Freeze 打包问题修复说明

## 问题描述

使用 `cx_Freeze` 打包的 exe 文件在全新的 Windows 系统上运行时报错：

```
RuntimeError: Failed to resolve Python Runtime Loader initialize from 
C:\Users\tw0h\OneDrive\桌面\Ledger (1)\Ledger\lib\pythonnet\runtime\Python.Runtime.dll
```

## 问题原因

`pywebview` 在 Windows 平台上依赖 `pythonnet` 库来调用 .NET 框架。`pythonnet` 需要 `Python.Runtime.dll` 文件才能正常工作，但默认的 `cx_Freeze` 配置没有正确打包这个 DLL 文件。

## 解决方案

修改 `setup.py` 文件，添加以下内容：

### 1. 添加 pythonnet DLL 文件的自动检测和包含

在 `build_resource_module` 调用后添加：

```python
# Find pythonnet DLL files
include_files = []
try:
    import pythonnet
    pythonnet_path = Path(pythonnet.__file__).parent
    runtime_dir = pythonnet_path / "runtime"
    if runtime_dir.exists():
        for dll_file in runtime_dir.glob("*.dll"):
            include_files.append((str(dll_file), f"lib/pythonnet/runtime/{dll_file.name}"))
except ImportError:
    pass
```

### 2. 更新 build_exe_options

```python
build_exe_options = {
    "build_exe": str(ROOT / "build" / "Ledger"),
    "packages": ["webview", "clr", "pythonnet"],  # 添加 clr 和 pythonnet
    "includes": [
        "ledger_embedded_resources",
        "webview.platforms.edgechromium",
        "webview.platforms.mshtml",
        "webview.platforms.winforms",
        "clr",           # 添加
        "clr_loader",    # 添加
    ],
    "include_msvcr": True,
    "include_files": include_files,  # 添加 DLL 文件列表
}
```

## 验证

构建完成后，检查以下文件是否存在：

```bash
./build/Ledger/lib/pythonnet/runtime/Python.Runtime.dll
```

## 重新构建

```bash
.\.venv-build\Scripts\python.exe setup.py build
```

构建完成后，生成的 exe 文件应该可以在全新的 Windows 系统上正常运行。
