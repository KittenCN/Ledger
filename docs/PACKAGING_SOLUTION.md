# 打包问题完整解决方案

## 问题总结

通过 `cx_Freeze` 打包的 exe 文件在全新 Windows 系统上无法运行，报错：
```
RuntimeError: Failed to resolve Python Runtime Loader initialize from Python.Runtime.dll
```

## 根本原因

`pywebview` 在 Windows 上依赖 `pythonnet`，而 `pythonnet` 需要 `Python.Runtime.dll` 才能工作。默认的 `cx_Freeze` 配置没有正确打包这个 DLL。

## 已完成的修复

### 1. 修改 setup.py ✅

添加了自动检测和包含 pythonnet DLL 的代码：

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
            print(f"Including pythonnet DLL: {dll_file.name}")
except ImportError:
    print("Warning: pythonnet not installed")

build_exe_options = {
    "packages": ["webview", "clr", "pythonnet"],
    "includes": [
        "ledger_embedded_resources",
        "webview.platforms.edgechromium",
        "webview.platforms.mshtml",
        "webview.platforms.winforms",
        "clr",
        "clr_loader",
    ],
    "include_files": include_files,
}
```

### 2. 添加启动时依赖检查 ✅

创建了 `check_dependencies.py` 模块，在应用启动时自动检查：
- .NET Framework 4.7.2+
- WebView2 Runtime

如果缺少任何组件，会显示友好的错误提示对话框，并提供下载链接，然后退出程序。

### 3. 验证构建完整性 ✅

创建了 `verify_build.py` 脚本，自动检查所有必需文件：

```bash
python verify_build.py
```

检查结果：
- [OK] 主程序和 Python 运行时
- [OK] pythonnet DLL (Python.Runtime.dll)
- [OK] CLR Loader DLL
- [OK] WebView2 组件
- [OK] Visual C++ 运行时
- [OK] 应用模块

## 目标系统要求

### 必须预装的组件

#### 1. .NET Framework 4.7.2 或更高版本
- **为什么需要**: pythonnet 依赖 .NET CLR
- **下载**: https://dotnet.microsoft.com/download/dotnet-framework
- **检查命令**:
  ```powershell
  Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full"
  ```

#### 2. Microsoft Edge WebView2 Runtime
- **为什么需要**: pywebview 使用 WebView2 渲染界面
- **下载**: https://developer.microsoft.com/microsoft-edge/webview2/
- **检查命令**:
  ```powershell
  Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
  ```

### 已包含的组件（无需额外安装）

- ✅ Python 3.13 运行时
- ✅ Visual C++ 运行时库（所有必需的 DLL）
- ✅ pythonnet 和 CLR Loader
- ✅ WebView2 .NET 组件
- ✅ 所有 Python 依赖库

## 部署方案

### 方案 1: 简单部署（需要用户手动安装依赖）

1. 将 `build/Ledger` 文件夹复制到目标机器
2. 确保目标机器已安装：
   - .NET Framework 4.7.2+
   - WebView2 Runtime
3. 运行 `Ledger.exe`

### 方案 2: 完整安装包（推荐）

使用 Inno Setup 创建安装程序，自动检测并安装依赖。

参考 `docs/DEPLOYMENT_CHECKLIST.md` 中的 Inno Setup 脚本示例。

## 测试清单

在部署前，建议在以下环境测试：

- [ ] 全新的 Windows 10 (21H2+)
- [ ] 全新的 Windows 11
- [ ] 已安装 .NET Framework 但无 WebView2 的系统
- [ ] 已安装 WebView2 但无 .NET Framework 的系统
- [ ] 完全干净的系统（两者都没有）
- [ ] 有防病毒软件的系统
- [ ] 不同用户权限（管理员/普通用户）

## 常见问题

### Q1: 仍然报 Python.Runtime.dll 错误
**A**: 检查目标系统是否安装了 .NET Framework 4.7.2+

### Q2: 应用启动后显示空白
**A**: 检查是否安装了 WebView2 Runtime

### Q3: 应用无法启动，没有错误提示
**A**: 以管理员权限运行，或检查防病毒软件是否拦截

## 构建命令

```bash
# 清理旧的构建
rm -rf build/

# 重新构建
.\.venv-build\Scripts\python.exe setup.py build

# 验证构建
.\.venv-build\Scripts\python.exe verify_build.py
```

## 相关文档

- [BUILD_FIX.md](BUILD_FIX.md) - 修复详情
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - 完整部署清单
- [BUILD.md](BUILD.md) - 构建说明

## 总结

经过完整检查，打包配置已经正确，所有必需的 DLL 和组件都已包含。只要目标系统安装了 .NET Framework 4.7.2+ 和 WebView2 Runtime，应用就能正常运行。

建议创建一个安装程序，自动检测并安装这两个依赖，以提供最佳的用户体验。
