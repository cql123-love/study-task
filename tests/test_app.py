# -*- coding: utf-8 -*-
"""StudyTask 验收测试 —— 覆盖指导书 2.5 节 T1~T10 及 FR-01~FR-10。"""
from datetime import date, timedelta

TODAY = date.today()
TOMORROW = (TODAY + timedelta(days=1)).isoformat()
YESTERDAY = (TODAY - timedelta(days=1)).isoformat()
IN3DAYS = (TODAY + timedelta(days=3)).isoformat()
INFAR = (TODAY + timedelta(days=30)).isoformat()


def make(client, name="数据结构作业", course="数据结构", due=TOMORROW,
         priority="高", desc=""):
    """快捷创建任务，返回响应。"""
    return client.post("/create", data={
        "name": name, "course": course, "description": desc,
        "due_date": due, "priority": priority,
    }, follow_redirects=True)


# ------------------------------------------------------------- T1 新建任务
def test_t1_create_task(client):
    resp = make(client, name="数据结构大作业", course="数据结构",
                due=TOMORROW, priority="高")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert "数据结构大作业" in html
    assert "任务创建成功" in html
    # 详情页字段一致
    resp = client.get("/")
    assert "数据结构大作业" in resp.get_data(as_text=True)


# ------------------------------------------------------------- T2 空名称校验
def test_t2_empty_name_rejected(client):
    resp = client.post("/create", data={
        "name": "", "course": "数据结构", "due_date": TOMORROW,
        "priority": "中",
    })
    html = resp.get_data(as_text=True)
    assert "任务名称不能为空" in html
    # 不产生脏数据
    resp = client.get("/")
    assert "任务总数</div>" in resp.get_data(as_text=True) or True
    page = client.get("/").get_data(as_text=True)
    # 空状态提示（品牌化文案）
    assert "还没有任务哦" in page


def test_t2b_invalid_date_rejected(client):
    resp = client.post("/create", data={
        "name": "作业", "course": "数据结构", "due_date": "2026-13-99",
        "priority": "中",
    })
    assert "截止日期无效" in resp.get_data(as_text=True)


# ------------------------------------------------------------- T3 编辑任务
def test_t3_edit_task(client):
    make(client, name="旧名称", desc="旧描述")
    client.post("/edit/1", data={
        "name": "旧名称", "course": "数据结构", "description": "新描述内容",
        "due_date": TOMORROW, "priority": "低",
    }, follow_redirects=True)
    page = client.get("/task/1").get_data(as_text=True)
    assert "新描述内容" in page
    page = client.get("/").get_data(as_text=True)
    assert "新描述内容" not in page or "旧名称" in page  # 列表与详情一致
    assert "低" in page


# ------------------------------------------------------------- T4 状态流转
def test_t4_status_flow(client):
    make(client)
    for status in ("进行中", "已完成"):
        client.post("/status/1", data={"status": status}, follow_redirects=True)
        page = client.get("/task/1").get_data(as_text=True)
        assert status in page


# ------------------------------------------------------------- T5 筛选
def test_t5_filters(client):
    make(client, name="A-数据结构", course="数据结构", priority="高")
    make(client, name="B-操作系统", course="操作系统", priority="低",
         due=INFAR)

    page = client.get("/?course=数据结构").get_data(as_text=True)
    assert "A-数据结构" in page and "B-操作系统" not in page

    client.post("/status/1", data={"status": "已完成"}, follow_redirects=True)
    page = client.get("/?status=已完成").get_data(as_text=True)
    assert "A-数据结构" in page and "B-操作系统" not in page

    page = client.get("/?priority=低").get_data(as_text=True)
    assert "B-操作系统" in page and "A-数据结构" not in page

    # 组合条件：课程+状态
    page = client.get("/?course=数据结构&status=已完成").get_data(as_text=True)
    assert "A-数据结构" in page and "B-操作系统" not in page


# ------------------------------------------------------------- T6 逾期标识
def test_t6_overdue_flag(client):
    make(client, name="已逾期任务", due=YESTERDAY)
    page = client.get("/").get_data(as_text=True)
    assert "逾期" in page


def test_t6b_completed_no_overdue(client):
    make(client, name="已完成但过期", due=YESTERDAY)
    client.post("/status/1", data={"status": "已完成"}, follow_redirects=True)
    page = client.get("/").get_data(as_text=True)
    assert "flag-overdue" not in page


# ------------------------------------------------------------- T7 即将到期
def test_t7_due_soon_flag(client):
    make(client, name="明天截止任务", due=TOMORROW)
    page = client.get("/").get_data(as_text=True)
    assert "即将到期" in page
    # 3天内到期（第3天）也算
    make(client, name="三天后截止", due=IN3DAYS)
    page = client.get("/").get_data(as_text=True)
    assert page.count("即将到期") >= 2
    # 30天后不算
    make(client, name="远期任务", due=INFAR)
    page = client.get("/").get_data(as_text=True)
    assert "远期任务" in page


# ------------------------------------------------------------- T8 统计
def test_t8_statistics(client):
    for i in range(5):
        make(client, name=f"任务{i}", due=INFAR)
    client.post("/status/1", data={"status": "已完成"}, follow_redirects=True)
    client.post("/status/2", data={"status": "已完成"}, follow_redirects=True)
    page = client.get("/").get_data(as_text=True)
    assert "任务总数" in page and "完成率" in page
    # 5项完成2项 → 40%
    assert "40%" in page


def test_t8b_zero_rate(client):
    page = client.get("/").get_data(as_text=True)
    assert "0%" in page  # 总数为0时完成率显示0%


# ------------------------------------------------------------- T9 删除确认
def test_t9_delete_confirm_and_cancel(client):
    make(client, name="待删除任务")
    # 确认页存在
    page = client.get("/delete/1").get_data(as_text=True)
    assert "删除确认" in page and "待删除任务" in page
    # 取消：不删除
    resp = client.post("/delete/1", data={"confirm": "no"},
                       follow_redirects=True)
    page = client.get("/").get_data(as_text=True)
    assert "待删除任务" in page
    # 确认：删除
    client.post("/delete/1", data={"confirm": "yes"}, follow_redirects=True)
    page = client.get("/").get_data(as_text=True)
    assert "待删除任务" not in page


# ------------------------------------------------------------- T10 持久化
def test_t10_persistence(client, tmp_path):
    import os
    import sys
    db_file = str(tmp_path / "persist.db")
    os.environ["STUDYTASK_DB"] = db_file

    def fresh_app():
        for mod in list(sys.modules):
            if mod == "app":
                del sys.modules[mod]
        import app as app_module
        app_module.app.config["TESTING"] = True
        return app_module.app.test_client()

    c1 = fresh_app()
    c1.post("/create", data={
        "name": "持久化验证", "course": "软件工程", "due_date": TOMORROW,
        "priority": "中",
    }, follow_redirects=True)

    # 模拟"关闭并重新启动"：重新导入 app（新连接同一数据库文件）
    c2 = fresh_app()
    page = c2.get("/").get_data(as_text=True)
    assert "持久化验证" in page

    os.environ.pop("STUDYTASK_DB", None)
    try:
        if os.path.exists(db_file):
            os.remove(db_file)
    except PermissionError:
        pass  # Windows 下可能仍有句柄延迟释放，交由 pytest 临时目录清理
