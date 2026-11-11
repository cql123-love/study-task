# -*- coding: utf-8 -*-
"""pytest 共享夹具：每个用例使用独立的临时 SQLite 数据库。"""
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = str(tmp_path / "test_studytask.db")
    monkeypatch.setenv("STUDYTASK_DB", db_file)
    # app 模块在首次导入时读取 STUDYTASK_DB，这里强制重新加载以保证隔离
    for mod in list(sys.modules):
        if mod == "app":
            del sys.modules[mod]
    import app as app_module

    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c
    if os.path.exists(db_file):
        os.remove(db_file)
