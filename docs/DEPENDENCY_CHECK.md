# 启动时依赖检查说明

## 功能

应用程序在启动时会自动检查以下系统依赖：

1. **.NET Framework 4.7.2 或更高版本**
2. **Microsoft Edge WebView2 Runtime**

如果缺少任何组件，会显示友好的错误对话框，提示用户需要安装的组件和下载链接，然后自动退出。

## 实现

### check_dependencies.py

```python
def check_dotnet_framework():
    """检查 .NET Framework 4.7.2+"""
    # 通过注册表检查 Release 版本号

def check_webview2_runtime():
    """检查 WebView2 Runtime"""
    # 检查 HKLM 和 HKCU 注册表项

def check_all_dependencies():
    """检查所有依赖，返回 True 表示通过"""
    # 如果缺少组件，显示错误对话框并返回 False
```

### Ledger.py

```python
from check_dependencies import check_all_dependencies

# 检查系统依赖
if not check_all_dependencies():
    sys.exit(1)

# 继续正常启动
import webview
...
```

## 错误提示示例

当缺少依赖时，用户会看到如下对话框：

```
标题: 缺少系统组件

内容:
缺少必要组件，应用无法启动：

  • .NET Framework 4.7.2 或更高版本
  • Microsoft Edge WebView2 Runtime

请访问以下链接下载安装：
.NET Framework: https://dotnet.microsoft.com/download/dotnet-framework
WebView2 Runtime: https://go.microsoft.com/fwlink/p/?LinkId=2124703
```

## 优点

1. **用户友好** - 清楚地告诉用户缺少什么，以及如何解决
2. **防止崩溃** - 在依赖缺失时优雅退出，而不是运行时崩溃
3. **提供解决方案** - 直接提供下载链接
4. **轻量级** - 只使用 Windows 标准 API，无额外依赖

## 测试

在开发环境测试：
```bash
python -c "from check_dependencies import check_all_dependencies; check_all_dependencies()"
```

在打包后的 exe 中，检查逻辑会在应用启动的最开始执行。
