# -*- coding: utf-8 -*-
"""StudyTask —— 个人学习任务管理系统（实验一）

界面品牌名：CQL's World（项目代号沿用指导书要求的 StudyTask）。
依据《软件工程》实验指导书 附录A《StudyTask需求规格说明书》实现。
技术栈：Python 3.11+ / Flask / SQLite。
"""
import os
import sqlite3
from datetime import date, timedelta

from flask import Flask, flash, redirect, render_template, request, url_for

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("STUDYTASK_DB", os.path.join(BASE_DIR, "studytask.db"))

app = Flask(__name__)
app.config["SECRET_KEY"] = "studytask-lab1"  # 仅用于 flash 消息签名，非敏感凭据

PRIORITIES = ("高", "中", "低")
STATUSES = ("待完成", "进行中", "已完成")


# ---------------------------------------------------------------- 数据库
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            course      TEXT    NOT NULL,
            description TEXT    DEFAULT '',
            due_date    TEXT    NOT NULL,
            priority    TEXT    NOT NULL DEFAULT '中',
            status      TEXT    NOT NULL DEFAULT '待完成',
            created_at  TEXT    NOT NULL,
            updated_at  TEXT    NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def seed_demo_data():
    """云端演示用：数据库为空时写入一组示例任务。

    启用条件（满足其一）：
    1. 环境变量 STUDYTASK_SEED=1（Render 部署配置中显式设置）；
    2. 检测到云端 PaaS 运行环境（存在 PORT / RAILWAY_ENVIRONMENT / RENDER 等标志），
       便于在 Railway 等平台上零配置启用。

    本地运行与自动化测试均不触发，保证测试用例的干净初始状态。
    """
    explicit = os.environ.get("STUDYTASK_SEED") == "1"
    cloud_hint = any(
        os.environ.get(k)
        for k in ("PORT", "RAILWAY_ENVIRONMENT", "RENDER", "FLY_APP_NAME", "DYNO")
    )
    if not (explicit or cloud_hint):
        return
    conn = get_db()
    if conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] > 0:
        conn.close()
        return
    today = date.today()
    rows = [
        ("软件工程实验一报告", "软件工程", "完成实验报告并提交验收表", "中", 3, "已完成"),
        ("数据结构大作业", "数据结构", "平衡二叉树实现", "高", 1, "进行中"),
        ("操作系统第三章习题", "操作系统", "进程同步与死锁习题 3-8", "中", 2, "待完成"),
        ("计算机网络课后题", "计算机网络", "TCP 三次握手与四次挥手", "低", 5, "待完成"),
        ("英语四级听力练习", "大学英语", "听力真题 Day 12", "低", -1, "待完成"),
    ]
    now = today.isoformat()
    for name, course, desc, priority, offset, status in rows:
        due = (today + timedelta(days=offset)).isoformat()
        conn.execute(
            "INSERT INTO tasks (name, course, description, due_date, priority,"
            " status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
            (name, course, desc, due, priority, status, now, now),
        )
    conn.commit()
    conn.close()

def validate_form(form):
    """校验表单，返回 (data, errors)。规则见 SRS A.2 / FR-01。"""
    errors = []
    data = {}

    name = (form.get("name") or "").strip()
    if not name:
        errors.append("任务名称不能为空")
    elif len(name) > 100:
        errors.append("任务名称不能超过100字")
    data["name"] = name

    course = (form.get("course") or "").strip()
    if not course:
        errors.append("所属课程不能为空")
    elif len(course) > 60:
        errors.append("所属课程不能超过60字")
    data["course"] = course

    desc = (form.get("description") or "").strip()
    if len(desc) > 1000:
        errors.append("任务描述不能超过1000字")
    data["description"] = desc

    due = (form.get("due_date") or "").strip()
    try:
        date.fromisoformat(due)
    except (ValueError, TypeError):
        errors.append("截止日期无效，须为 YYYY-MM-DD 格式的合法日期")
    data["due_date"] = due

    priority = form.get("priority") or "中"
    if priority not in PRIORITIES:
        errors.append("优先级取值无效")
    data["priority"] = priority

    return data, errors


# ---------------------------------------------------------------- 标记逻辑
def deadline_flag(task, today=None):
    """FR-07：逾期 / 即将到期 标记。已完成任务不提示。"""
    today = today or date.today()
    try:
        due = date.fromisoformat(task["due_date"])
    except (ValueError, TypeError):
        return ""
    if task["status"] == "已完成":
        return ""
    if due < today:
        return "逾期"
    if due <= today + timedelta(days=3):
        return "即将到期"
    return ""


# ---------------------------------------------------------------- 路由
@app.route("/")
def index():
    """FR-02/FR-06/FR-08：列表（可按课程、状态、优先级组合筛选）+ 统计。"""
    course = (request.args.get("course") or "").strip()
    status = request.args.get("status") or ""
    priority = request.args.get("priority") or ""

    sql = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if course:
        sql += " AND course LIKE ?"
        params.append(f"%{course}%")
    if status:
        sql += " AND status = ?"
        params.append(status)
    if priority:
        sql += " AND priority = ?"
        params.append(priority)
    sql += " ORDER BY due_date ASC, id DESC"

    conn = get_db()
    tasks = conn.execute(sql, params).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    done = conn.execute(
        "SELECT COUNT(*) FROM tasks WHERE status = '已完成'"
    ).fetchone()[0]
    conn.close()

    rate = round(done / total * 100) if total else 0  # FR-08：总数0时完成率0%
    tasks = [dict(t, flag=deadline_flag(t)) for t in tasks]

    conn_c = get_db()
    courses = [
        r["course"]
        for r in conn_c.execute("SELECT DISTINCT course FROM tasks ORDER BY course")
    ]
    conn_c.close()

    return render_template(
        "index.html",
        tasks=tasks,
        total=total,
        done=done,
        rate=rate,
        courses=courses,
        f_course=course,
        f_status=status,
        f_priority=priority,
        statuses=STATUSES,
        priorities=PRIORITIES,
    )


@app.route("/task/<int:task_id>")
def detail(task_id):
    """FR-02：详情页。"""
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if row is None:
        flash("任务不存在")
        return redirect(url_for("index"))
    return render_template("detail.html", task=dict(row, flag=deadline_flag(row)))


@app.route("/create", methods=["GET", "POST"])
def create():
    """FR-01：创建任务，校验名称、课程、截止日期有效性。"""
    if request.method == "POST":
        data, errors = validate_form(request.form)
        if errors:
            for e in errors:
                flash(e)
            return render_template(
                "form.html", mode="create", task=request.form,
                statuses=STATUSES, priorities=PRIORITIES
            ), 400
        now = date.today().isoformat()
        conn = get_db()
        conn.execute(
            "INSERT INTO tasks (name, course, description, due_date, priority,"
            " status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)",
            (
                data["name"], data["course"], data["description"],
                data["due_date"], data["priority"], "待完成", now, now,
            ),
        )
        conn.commit()
        conn.close()
        flash("任务创建成功")
        return redirect(url_for("index"))
    return render_template(
        "form.html", mode="create", task=None,
        statuses=STATUSES, priorities=PRIORITIES
    )


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit(task_id):
    """FR-03：修改任务各字段，修改后列表与详情保持一致。"""
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        conn.close()
        flash("任务不存在")
        return redirect(url_for("index"))
    if request.method == "POST":
        data, errors = validate_form(request.form)
        if errors:
            conn.close()
            for e in errors:
                flash(e)
            return render_template(
                "form.html", mode="edit", task=request.form,
                statuses=STATUSES, priorities=PRIORITIES
            ), 400
        conn.execute(
            "UPDATE tasks SET name=?, course=?, description=?, due_date=?,"
            " priority=?, updated_at=? WHERE id=?",
            (
                data["name"], data["course"], data["description"],
                data["due_date"], data["priority"],
                date.today().isoformat(), task_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("任务修改成功")
        return redirect(url_for("detail", task_id=task_id))
    conn.close()
    return render_template(
        "form.html", mode="edit", task=row,
        statuses=STATUSES, priorities=PRIORITIES
    )


@app.route("/delete/<int:task_id>", methods=["GET", "POST"])
def delete(task_id):
    """FR-04：删除前要求确认，确认后从数据库删除。"""
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        conn.close()
        flash("任务不存在")
        return redirect(url_for("index"))
    if request.method == "POST":
        if request.form.get("confirm") != "yes":
            conn.close()
            flash("已取消删除")
            return redirect(url_for("index"))
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        flash("任务已删除")
        return redirect(url_for("index"))
    conn.close()
    return render_template("confirm_delete.html", task=row)


@app.route("/status/<int:task_id>", methods=["POST"])
def change_status(task_id):
    """FR-05：在 待完成/进行中/已完成 间调整状态。"""
    new_status = request.form.get("status")
    if new_status not in STATUSES:
        flash("状态取值无效")
        return redirect(url_for("index"))
    conn = get_db()
    cur = conn.execute(
        "UPDATE tasks SET status=?, updated_at=? WHERE id=?",
        (new_status, date.today().isoformat(), task_id),
    )
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if not changed:
        flash("任务不存在")
    else:
        flash(f"状态已更新为「{new_status}」")
    return redirect(request.referrer or url_for("index"))


@app.errorhandler(404)
def not_found(_e):
    return render_template("error.html", msg="页面不存在"), 404


init_db()
seed_demo_data()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
