# StudyTask —— 个人学习任务管理系统

《软件工程》实验一：AI 驱动的个人学习任务管理系统（项目代号 StudyTask）。
单用户学习任务管理 Web 应用，支持任务增删改查、状态流转、组合筛选、逾期/即将到期识别、完成率统计与本地持久化。

> 完整需求依据：《软件工程》实验指导书 附录A《StudyTask 需求规格说明书》（SRS）

## 在线地址

| 项目 | 地址 |
|---|---|
| **代码仓库（GitHub，提交用）** | **https://github.com/cql123-love/study-task** |
| GitHub 个人主页 | https://github.com/cql123-love |
| **Web 访问地址（公网在线）** | **https://pest-brochures-valves-breakfast.trycloudflare.com** |
| 本地运行访问地址 | http://127.0.0.1:5000 |

**部署说明（重要）**

- 上表公网地址由本机经 Cloudflare Tunnel 临时穿透发布，**任意时间均可访问**（经实测返回 200）。
- 该临时地址的前提是**本机保持开机且 Flask 服务与隧道进程运行中**；关机或进程结束后地址失效，届时需重新发布并回填本行。
- 永久云端部署配置已随仓库提供（`render.yaml`）：Build `pip install -r requirements.txt`，Start `gunicorn app:app --bind 0.0.0.0:$PORT`，Plan 选 Free，即可得到固定地址 `https://studytask-xxxx.onrender.com`。Render 免费实例 15 分钟无访问会休眠，首次打开需等待约 30~60 秒唤醒。
- 免费实例磁盘为临时盘，**重新部署后数据会重置**，因此**持久化验收（T10）以本地运行为准**，本地 SQLite 数据文件为 `studytask.db`，随项目目录保存。

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
