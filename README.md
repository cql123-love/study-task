# CQL's World —— 个人学习任务管理系统

《软件工程》实验一：AI 驱动的个人学习任务管理系统（项目代号 StudyTask，界面品牌名 **CQL's World**）。
单用户学习任务管理 Web 应用，支持任务增删改查、状态流转、组合筛选、逾期/即将到期识别、完成率统计与本地持久化。
界面为粉紫渐变风格，含欢迎横幅、渐变统计卡片与圆角卡片体系。

> 完整需求依据：《软件工程》实验指导书 附录A《StudyTask 需求规格说明书》（SRS）

## 在线地址

| 项目 | 地址 |
|---|---|
| **代码仓库（GitHub，提交用）** | **https://github.com/cql123-love/study-task** |
| GitHub 个人主页 | https://github.com/cql123-love |
| **Web 访问地址（云端常驻，无需本机开机）** | **https://studytask-production-44f96ffe.up.railway.app** |
| Web 访问地址（本机固定地址，需本机开机） | https://studytask.loca.lt |
| 本地运行访问地址 | http://127.0.0.1:5000 |

**部署说明（重要）**

本项目提供两种公网访问方式，均已实测可用：

| 方式 | 地址 | 是否依赖本机开机 | 说明 |
|---|---|---|---|
| **云端常驻部署（推荐，已上线）** | `https://studytask-production-44f96ffe.up.railway.app` | **否** | 已部署到 Railway 免费实例，**任何人任何时候打开都是同一个网址**，本机关机不影响；仓库内含 `railway.json`，3 步可复现部署 |
| 本机固定隧道 | `https://studytask.loca.lt` | 是 | 本机 Flask(8088) + localtunnel 固定子域名，地址永久固定；需本机开机且服务在运行 |

- 云端地址已实测：首页 HTTP 200（响应约 1.2 秒），新建/校验/状态流转/统计/组合筛选/删除确认全链路 10 项端到端实测全部通过。
- 本机固定地址的一键启动：`bash start_public.sh`（停止：`bash start_public.sh stop`）。
- 免费云实例闲置后会休眠（Railway 约 5 分钟无请求后休眠），首次打开需等待十几秒唤醒。
- 云端实例磁盘为临时盘，**重新部署后数据会重置**；因此云端首次启动会自动写入 5 条演示数据（由环境变量 `STUDYTASK_SEED=1` 或云端环境自动检测触发，仅云端启用，本地运行与自动化测试不受影响）。
- **持久化验收（T10）以本地运行为准**：本地 SQLite 数据文件 `studytask.db` 随项目目录保存，重启服务后数据仍在。

### 云端部署（免费，无需信用卡）

仓库已内置两套部署配置（`railway.json` 与 `render.yaml`），任选其一，**均不需要绑定信用卡**。

**方案一：Railway（✅ 本项目实际采用，已上线）**

仓库内 `railway.json` 已配置好 Nixpacks 构建与启动命令，部署后自动获得固定域名。

1. 打开 <https://railway.com/new> → 用 GitHub 登录 → 选择 **GitHub Repository**
2. 首次需先点 **Configure GitHub App** 授权（Repository access 选 *Only select repositories* 并勾选 `study-task`），授权后点 **Refresh**
3. 选择 `cql123-love/study-task` → Railway 自动读取 `railway.json` 完成构建
4. 构建完成后自动分配固定域名（形如 `https://studytask-production-xxxx.up.railway.app`）

**本项目当前部署地址：`https://studytask-production-44f96ffe.up.railway.app`**（Free 计划，$0/月，免信用卡，30 天 $5 试用额度后 $1/月）

**方案二：Render（备选）**

配置（仓库内 `render.yaml` 已自动填好）：Build `pip install -r requirements.txt` / Start `gunicorn app:app --bind 0.0.0.0:$PORT` / Plan `Free`。

1. 打开 <https://dashboard.render.com/blueprint/new?repo=https%3A%2F%2Fgithub.com%2Fcql123-love%2Fstudy-task>
2. 页面确认后点击 **Apply**（首次需先「用 GitHub 登录」并授权仓库访问）
3. 等待构建完成（约 2~5 分钟），生成 `https://studytask-xxxx.onrender.com` 固定地址

> ⚠️ 若创建服务时看到 **Starter / $7 per month** 之类的选项，**务必选 Free**——Render 仅在选择付费实例时才要求绑定信用卡；Free 实例全程免卡。
> 若 `render.com` 主域名因网络 DNS 污染打不开，改用 **https://dashboard.render.com/** 亦可（该域名可正常访问），路径为 Dashboard → New → Web Service → 选择仓库 → Instance Type 选 Free → Create Web Service。


## 技术栈

- Python 3.11+ / Flask 3.x
- SQLite（标准库 `sqlite3`，无需单独安装数据库）
- pytest（自动化验收测试）
- gunicorn（云端部署使用）

## 从零开始的运行步骤

```bash
# 1. 克隆仓库
git clone https://github.com/cql123-love/study-task.git
cd study-task

# 2. 创建并激活虚拟环境（Python 3.11+）
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动（默认端口 5000；数据库文件 studytask.db 首次运行自动创建）
python app.py
```

浏览器访问 http://127.0.0.1:5000 即可使用。

### 运行自动化测试

```bash
pytest tests/ -v
```

共 13 条测试，覆盖指导书 2.5 节 T1~T10 全部验收用例（T2 含两个子用例、T6 含已完成不提示逾期、T8 含零任务完成率为 0%）。

## 功能清单（对应 SRS FR-01~FR-10）

| 编号 | 功能 | 验收重点 |
|---|---|---|
| FR-01 | 表单创建任务，校验名称(1-100字)、课程(1-60字)、截止日期(YYYY-MM-DD) | 必填项校验，错误提示，不产生脏数据 |
| FR-02 | 列表展示名称/课程/截止日期/状态/优先级 + 详情页 | 字段完整一致 |
| FR-03 | 修改任务各字段 | 修改后列表与详情一致 |
| FR-04 | 删除任务（先确认再删除） | 取消不删除、确认后删除 |
| FR-05 | 状态在 待完成/进行中/已完成 间调整 | 变更后持久保存 |
| FR-06 | 按课程、状态、优先级筛选，支持组合条件 | 筛选结果准确 |
| FR-07 | 逾期 / 即将到期（今日起3天内到期）标记，已完成不提示 | 日期逻辑正确 |
| FR-08 | 统计总数、完成数、完成率（总数0时显示0%） | 统计结果正确 |
| FR-09 | 关闭重启后数据保持不变 | SQLite 本地持久化 |
| FR-10 | 中文界面、基本错误提示、404 页面，不因错误输入崩溃 | 健壮性 |

## 项目结构

```
StudyTask/
├── app.py                  # Flask 应用（路由、校验、逾期逻辑、SQLite）
├── requirements.txt        # 依赖清单
├── render.yaml             # Render 部署配置
├── templates/              # Jinja2 模板（base/index/form/detail/confirm_delete/error）
├── static/style.css        # 样式
├── tests/
│   ├── conftest.py         # pytest 夹具（每个用例独立临时数据库）
│   └── test_app.py         # T1~T10 验收测试
├── docs/
│   ├── 需求验收表.md        # T1~T10 逐条验收记录（实际结果/预期/是否通过/证据）
│   ├── AI_DEV_LOG.md       # AI 开发过程记录（提示词、问题、修复、人工判断）
│   └── 实验一实验报告.docx  # 实验报告（≤4页）
└── README.md
```

## 部署（Render）

仓库已含 `render.yaml`。在 GitHub fork/推送本仓库后，于 Render 创建 Web Service 选择该仓库即可，构建/启动命令：

- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app --bind 0.0.0.0:$PORT`

## 范围外（SRS A.5，未实现）

用户注册、多用户权限、共享任务、邮件/短信发送、第三方日历同步、移动 App、云数据库。

## 已知限制

- 单用户设计，无登录与并发控制；
- Render 免费实例重启后 SQLite 数据重置（本地运行无此问题）；
- 界面为服务端渲染的轻量页面，未引入前端框架（符合 SRS"不强制特定前端框架"）。
