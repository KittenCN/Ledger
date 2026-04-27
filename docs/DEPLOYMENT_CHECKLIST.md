# 部署检查清单

## ✅ 已验证的组件

### 1. Python 运行时
- ✅ `python313.dll` - Python 3.13 运行时
- ✅ `zlib.dll` - 压缩库

### 2. Visual C++ 运行时 (已包含)
- ✅ `vcruntime140.dll`
- ✅ `vcruntime140_1.dll`
- ✅ `vcruntime140_threads.dll`
- ✅ `msvcp140.dll`
- ✅ `msvcp140_1.dll`
- ✅ `msvcp140_2.dll`
- ✅ `msvcp140_atomic_wait.dll`
- ✅ `msvcp140_codecvt_ids.dll`
- ✅ `concrt140.dll`
- ✅ `vcamp140.dll`
- ✅ `vccorlib140.dll`
- ✅ `vcomp140.dll`

### 3. pythonnet 依赖 (已修复)
- ✅ `Python.Runtime.dll` (在 lib/ 和 lib/pythonnet/runtime/)
- ✅ `clr_loader` 模块及其 DLL

### 4. WebView2 组件
- ✅ `Microsoft.Web.WebView2.Core.dll`
- ✅ `Microsoft.Web.WebView2.WinForms.dll`
- ✅ `WebBrowserInterop.x64.dll`
- ✅ `WebBrowserInterop.x86.dll`
- ✅ `WebView2Loader.dll` (win-x64, win-x86, win-arm64)

### 5. 应用程序模块
- ✅ `ledger_embedded_resources.pyc` (在 library.zip 中)
- ✅ `ledger_runtime.pyc` (在 library.zip 中)
- ✅ 资源文件已嵌入

## ⚠️ 目标系统要求

### 必须安装的组件

#### 1. .NET Framework 4.7.2 或更高版本
**原因**: pythonnet 需要 .NET Framework 来加载 CLR

**检查方法**:
```powershell
Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" | Select-Object Release, Version
```

**下载地址**:
- https://dotnet.microsoft.com/download/dotnet-framework

#### 2. Microsoft Edge WebView2 Runtime
**原因**: pywebview 使用 WebView2 来渲染网页界面

**检查方法**:
```powershell
Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" -ErrorAction SilentlyContinue
```

**下载地址**:
- https://developer.microsoft.com/microsoft-edge/webview2/

**安装选项**:
1. **Evergreen Bootstrapper** (推荐) - 自动下载并安装最新版本
2. **Evergreen Standalone Installer** - 离线安装包
3. **Fixed Version** - 固定版本（不推荐）

## 📋 部署步骤

### 方案 1: 手动安装依赖
1. 在目标机器上安装 .NET Framework 4.7.2+
2. 在目标机器上安装 WebView2 Runtime
3. 复制 `build/Ledger` 文件夹到目标机器
4. 运行 `Ledger.exe`

### 方案 2: 创建安装程序（推荐）
使用 Inno Setup 或 NSIS 创建安装程序，自动检测并安装依赖：

```iss
[Setup]
AppName=Ledger
AppVersion=1.0.0
DefaultDirName={pf}\Ledger
OutputDir=installer
OutputBaseFilename=LedgerSetup

[Files]
Source: "build\Ledger\*"; DestDir: "{app}"; Flags: recursesubdirs

[Run]
; 检查并安装 .NET Framework
Filename: "https://go.microsoft.com/fwlink/?linkid=2088631"; \
    StatusMsg: "Installing .NET Framework..."; \
    Check: NeedsDotNetFramework

; 检查并安装 WebView2 Runtime
Filename: "{tmp}\MicrosoftEdgeWebview2Setup.exe"; \
    Parameters: "/silent /install"; \
    StatusMsg: "Installing WebView2 Runtime..."; \
    Check: NeedsWebView2Runtime

[Code]
function NeedsDotNetFramework: Boolean;
begin
  // 检查 .NET Framework 是否已安装
  Result := not RegKeyExists(HKLM, 'SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full');
end;

function NeedsWebView2Runtime: Boolean;
begin
  // 检查 WebView2 Runtime 是否已安装
  Result := not RegKeyExists(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}');
end;
```

## 🧪 测试清单

在全新的 Windows 系统上测试：

- [ ] Windows 10 (21H2 或更高)
- [ ] Windows 11
- [ ] 无 .NET Framework 的系统
- [ ] 无 WebView2 Runtime 的系统
- [ ] 有防病毒软件的系统
- [ ] 不同用户权限（管理员/普通用户）

## 🔍 常见问题排查

### 问题 1: "Python.Runtime.dll 无法加载"
**原因**: 缺少 .NET Framework
**解决**: 安装 .NET Framework 4.7.2 或更高版本

### 问题 2: "WebView2 Runtime 未找到"
**原因**: 缺少 WebView2 Runtime
**解决**: 安装 Microsoft Edge WebView2 Runtime

### 问题 3: "应用程序无法启动"
**原因**: 缺少 Visual C++ 运行时
**解决**: 已包含在打包文件中，如果仍有问题，安装 Visual C++ Redistributable 2015-2022

### 问题 4: "激活文件无法读取"
**原因**: 文件路径或权限问题
**解决**: 确保激活文件在正确位置，且有读取权限

## 📦 最终打包建议

1. **创建完整安装包**，包含：
   - Ledger.exe 及所有依赖文件
   - .NET Framework 离线安装包
   - WebView2 Runtime 离线安装包
   - 安装脚本（自动检测并安装依赖）

2. **提供便携版**（需要用户手动安装依赖）

3. **创建用户文档**，说明系统要求和安装步骤
