#!/usr/bin/env bash
# ============================================================
# StudyTask 一键启动（固定公网地址版）
#   本地 Flask(8088) + localtunnel 固定子域名 -> https://studytask.loca.lt
# 用法：bash start_public.sh        启动
#       bash start_public.sh stop   停止
# ============================================================
set -u

PROJ="/d/workBuddy/StudyTask"
PY="/c/Users/yhxwan/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
NODE="/c/Users/yhxwan/.workbuddy/binaries/node/versions/22.22.2/node.exe"
LT_WS="/c/Users/yhxwan/.workbuddy/binaries/node/workspace"
LT_LOG="/d/workBuddy/lt.log"
PUBLIC_URL="https://studytask.loca.lt"

stop_all() {
    echo "正在停止..."
    taskkill //F //IM node.exe >/dev/null 2>&1
    taskkill //F //IM cloudflared.exe >/dev/null 2>&1
    pkill -f "app.py" >/dev/null 2>&1
    echo "已停止。"
}

case "${1:-start}" in
stop) stop_all; exit 0 ;;
esac

cd "$PROJ" || exit 1

# 1) 启动 Flask（后台）
PORT=8088 nohup "$PY" app.py > "$PROJ/server.log" 2>&1 &
sleep 4
CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 8 http://127.0.0.1:8088/)
if [ "$CODE" != "200" ]; then
    echo "本地服务启动失败（HTTP $CODE），请查看 $PROJ/server.log"
    exit 1
fi
echo "本地服务已启动：http://127.0.0.1:8088"

# 2) 启动 localtunnel 固定子域名（后台）
if [ ! -d "$LT_WS/node_modules/localtunnel" ]; then
    echo "未找到 localtunnel，请先在 $LT_WS 下执行：npm install localtunnel"
    exit 1
fi
cd "$LT_WS" || exit 1
nohup "$NODE" node_modules/localtunnel/bin/lt.js --port 8088 --subdomain studytask > "$LT_LOG" 2>&1 &
sleep 12

if ! grep -q "$PUBLIC_URL" "$LT_LOG" 2>/dev/null; then
    echo "隧道启动中，请稍候再访问：$PUBLIC_URL"
else
    echo ""
    echo "==============================================="
    echo " 固定公网地址： $PUBLIC_URL"
    echo " 停止服务：     bash start_public.sh stop"
    echo " 注：地址永久固定，无需修改 README"
    echo "==============================================="
fi
