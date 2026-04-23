# Ledger 项目功能与实现文档

生成日期：2026-04-23

## 1. 项目概览

Ledger 是一个以本地 HTML 页面为主体、通过 Python `pywebview` 封装成桌面窗口的加密资产管理界面原型。项目当前包含两类内容：

- 源码与静态资源：`Ledger.py` 与 `resource/` 目录，是当前可维护的核心代码。
- 打包产物：`Ledger/` 目录，包含 `Ledger.exe`、Python 运行时、Qt/WebView 相关库和少量资源文件，主要用于分发运行，不建议作为日常开发入口。

应用启动后会打开 `resource/App.html`，展示类似 Ledger Live 的资产组合、账户列表、发送/接收弹窗、My Ledger 状态页等界面。`resource/` 下还包含几套 Gate.io 风格的资产、现货、理财静态页面。

## 2. 顶层目录结构

```text
.
├── Ledger.py
├── resource/
│   ├── App.html
│   ├── myfunds.html
│   ├── myfunds.css
│   ├── spot.html
│   ├── spot.css
│   ├── wealth.html
│   ├── wealth.css
│   ├── autoinvest.html
│   ├── autoinvest.css
│   ├── myledger.png
│   └── path_to_logo.png
├── Ledger/
│   ├── Ledger.exe
│   ├── resource/
│   ├── lib/
│   └── ...
└── docs/
    └── PROJECT_DOCUMENTATION.md
```

## 3. 启动流程

入口文件是 `Ledger.py`。

核心流程：

1. 引入 `webview` 和 `os`。
2. 通过 `os.path.abspath('./resource/App.html')` 获取主 HTML 文件绝对路径。
3. 拼接成 `file://` URL。
4. 调用 `webview.create_window('Ledger APP', html_path, fullscreen=False, js_api=True, maximized=True)` 创建桌面窗口。
5. 在主程序块中调用 `create_window()`，再调用 `webview.start()` 启动 WebView 事件循环。

当前实现没有后端业务接口，也没有本地数据库或文件持久化。桌面程序本质上是一个本地静态 Web 应用容器。

## 4. 核心页面：resource/App.html

`App.html` 是桌面应用的主页面，文件内联了 CSS、HTML 结构和 JavaScript 逻辑。

### 4.1 外部依赖

- `Chart.js`：通过 CDN 加载，用于绘制 BTC 价格折线图。
- `Font Awesome 5.15.3`：通过 CDN 加载，用于侧边栏、按钮和弹窗中的图标。
- `CoinGecko API`：通过浏览器 `fetch` 获取比特币价格数据。

由于以上依赖都来自网络 CDN/API，离线环境下图标、图表或实时价格可能无法正常显示。

### 4.2 页面布局

主页面由以下区域组成：

- 顶部右侧图标区：状态、通知、邮件、设置、用户入口。
- 左侧侧边栏：Portfolio、Market、Accounts、Discover、Send、Receive、Earn、Buy/Sell、Swap、Refer、Card、Recover、My Ledger 等菜单。
- 主内容区：默认展示更新提示、风险提示、快捷卡片、添加账户按钮和资产图表容器。
- 弹窗区：页面底部定义了 Send 和 Receive 两个模态框。

### 4.3 默认 Portfolio 功能

Portfolio 页面展示资产组合概览：

- 使用固定 BTC 数量 `11.145 + 11 + 11` 作为资产数量。
- 通过 `getBitcoinPrices()` 获取今日和昨日 BTC 价格。
- 计算总资产美元价值。
- 计算价格涨跌值和涨跌方向。
- 调用 `fetchBitcoinPrices()` 拉取近 7 天价格序列，再由 `renderChart(data)` 绘制折线图。

这部分展示逻辑是动态的，但资产数量是写死在前端代码中的。

### 4.4 Accounts 功能

Accounts 页面通过 `activateAccounts(element)` 动态替换主内容区：

- 获取 BTC 今日和昨日价格。
- 定义三个本地账户数据：Bitcoin 1、Bitcoin 2、Bitcoin 3。
- 每个账户包含固定 BTC 数量。
- 根据当前 BTC 价格计算账户美元价值。
- 根据今日/昨日价格差计算账户涨跌金额和涨跌比例。
- 生成 HTML 表格并写入 `.main` 容器。

账户数据没有持久化，也没有从真实钱包、交易所或后端接口读取。

### 4.5 图表实现

`renderChart(data)` 使用 Chart.js：

- 图表类型：`line`。
- 横轴标签：`getLastSixDays()` 生成最近 7 天日期。
- 纵轴数据：来自 CoinGecko 价格接口。
- 样式：绿色线条、半透明填充、隐藏图例、简化坐标网格。

价格数据来自 `fetchBitcoinPrices()`，接口地址为 CoinGecko 的 `market_chart/range`。

### 4.6 Send / Receive 弹窗

`activateSend(element)` 与 `activateReceive(element)` 分别控制两个模态框：

- 点击侧边栏 Send 或 Receive 时显示弹窗。
- 点击弹窗关闭按钮隐藏弹窗。
- 点击弹窗外部区域也会隐藏弹窗。
- Send 弹窗包含账户选择、收款地址输入、步骤指示器和 Submit 按钮。
- Receive 弹窗包含账户选择、步骤指示器和 Submit 按钮。

当前 Submit 按钮只复用通用按钮激活/加载逻辑，没有实际链上发送、地址校验或设备确认流程。

### 4.7 My Ledger 功能

`activateMyLedger(element)` 会替换主内容区：

- 保留更新提示条。
- 显示一张 `myledger.png` 图片。
- 显示 “Your device is genuine” 文案。

该页面用于模拟设备状态/真伪验证结果，没有真实硬件通信逻辑。

### 4.8 通用交互

页面中有几段 DOMContentLoaded 初始化逻辑：

- 对卡片点击做事件代理，点击后给卡片添加 `active` 状态。
- 为 `.preicon` 随机分配颜色。
- 为普通菜单按钮、添加账户按钮和 `.btn` 添加加载图标，1 秒后移除。

通用函数：

- `activateButton(element)`：切换按钮激活状态。
- `handleMenuButtonClick(button)`：右上角图标点击时显示短暂加载动画。
- `getLastSixDays()` / `formatDate(date)`：生成图表横轴日期标签。

## 5. 资产总览页面：resource/myfunds.html 与 myfunds.css

`myfunds.html` 是 Gate.io 风格的资产总览静态页面。

主要内容：

- 顶部导航栏：买币、行情、交易、衍生品、芝麻金融、交易机器人等入口。
- 左侧资产菜单：资产总览、现货账户、金融账户、账单明细、充值提现记录等。
- 主内容区：展示资产总值、今日盈亏、我的资产分类。
- 右侧面板：个人中心概览和公告中心。

`myfunds.css` 提供通用布局样式，包括顶部导航、侧边栏、主内容卡片、资产条目、右侧面板和按钮样式。`spot.html` 和 `wealth.html` 也复用了该样式文件。

## 6. 现货账户页面：resource/spot.html 与 spot.css

`spot.html` 展示静态现货账户信息。

主要内容：

- 复用 Gate.io 风格顶部导航和侧边栏。
- 展示现货总资产、可用资产、冻结资产。
- 展示币种列表表格，包括 USDT、BTC、LTC、ETH、BCH、ETC、ZEC、QTUM 等。
- 每行包含币种、可用、冻结、折合金额以及操作按钮。

`spot.css` 在 `myfunds.css` 基础上补充现货页面专用样式，例如现货面板、余额卡片、币种表格、表格 hover 效果和按钮样式。

## 7. 金融账户页面：resource/wealth.html 与 wealth.css

`wealth.html` 是金融/理财账户静态页面。

主要内容：

- 顶部导航。
- 筛选区：理财类型、资产类型、搜索框。
- 操作按钮：申购、赎回、转入、转出。
- 投资明细表：展示产品类型、币种、金额、收益、状态和操作。
- 交易记录表：展示交易时间、类型、金额、状态等。
- 分页按钮。

`wealth.css` 定义了投资明细、筛选器、操作按钮、表格、分页、锁仓状态和交易记录区的样式。

## 8. 定投/金融账户页面：resource/autoinvest.html 与 autoinvest.css

`autoinvest.html` 也是 Gate.io 风格的金融账户静态页面，重点展示不同金融产品账户概览。

主要内容：

- 顶部导航和侧边栏。
- 金融账户标题。
- 账户概览卡片：定投理财、锁仓理财、双币宝、流动性挖矿、插槽拍卖、余币宝、财富管理。
- 每个卡片展示 USD 金额和 BTC 折算值。

`autoinvest.css` 与 `myfunds.css` 内容高度相似，并增加了金融账户卡片网格样式。

## 9. 图片资源

- `resource/myledger.png`：主应用 My Ledger 页面中展示的设备或状态图片。
- `resource/path_to_logo.png`：Gate.io 风格静态页面顶部导航中的 logo 图片。
- `Ledger/resource/App.html` 与 `Ledger/resource/myledger.png`：打包目录中的运行副本。

## 10. 打包目录 Ledger/

`Ledger/` 目录看起来是 Windows 桌面应用打包输出：

- `Ledger.exe`：可执行文件。
- `python38.dll`、`python3.dll`：Python 运行时。
- `lib/`：Python 标准库、第三方库、Qt/PySide/PyQt/WebView 依赖。
- `resource/`：运行时使用的页面资源副本。
- `frozen_application_license.txt`：打包应用许可证文件。

该目录文件量很大，绝大多数属于第三方运行时依赖，不应被视为业务源码。后续维护应优先修改根目录 `Ledger.py` 和 `resource/`，再重新打包生成 `Ledger/`。

## 11. 数据流与运行时依赖

当前数据来源分为两类：

- 静态硬编码数据：账户余额、资产分类、现货币种、理财记录、交易记录等大部分展示数据直接写在 HTML 中。
- 网络实时数据：`App.html` 中的 BTC 今日/昨日价格和近 7 天价格来自 CoinGecko API。

运行时依赖：

- Python 运行环境需要安装 `pywebview`。
- 主页面需要浏览器/WebView 能访问 CDN 和 CoinGecko API。
- 打包版依赖 `Ledger/` 目录中随包携带的 Python 和 GUI 运行时。

## 12. 已观察到的维护风险

- `Ledger.py` 中中文注释出现乱码，可能是历史编码不一致导致，建议统一保存为 UTF-8。
- `App.html` 同时包含大量 CSS、HTML 和 JavaScript，文件较长，后续维护可拆分为独立 CSS/JS 文件。
- 多个页面的顶部导航、侧边栏结构重复，建议抽取模板或复用组件。
- `myfunds.html`、`spot.html`、`wealth.html` 中部分 `<a>` 标签写法不规范，例如 `href` 后直接拼接 `<i>`，浏览器可能容错显示，但不利于维护。
- CoinGecko API 请求没有用户可见的错误提示，网络失败时主要写入控制台。
- 资产数量、账户记录、理财记录均为硬编码模拟数据，不适合作为真实财务数据来源。
- `js_api=True` 已开启，但当前没有传入 Python API 对象，也没有前后端桥接逻辑。
- `Ledger/` 打包目录中包含大量二进制和第三方库，如果纳入版本管理会导致仓库体积膨胀，建议确认是否需要用 `.gitignore` 或发布产物管理策略隔离。

## 13. 后续改进建议

- 将 `App.html` 拆分为 `app.css`、`app.js` 和结构化 HTML。
- 将模拟资产数据集中到单独 JSON 文件，便于替换为真实接口。
- 为网络请求增加 loading、失败提示和兜底数据。
- 修正 HTML 标签结构并通过格式化工具统一代码风格。
- 明确源码目录和打包目录边界，避免直接修改打包产物。
- 如果要接入真实钱包或交易所数据，应新增后端 API 层，并对私钥、助记词、交易签名等敏感流程做严格安全设计。
