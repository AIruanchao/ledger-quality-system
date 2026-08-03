#!/bin/bash
# 故障演练脚本 — kill进程验证自动恢复
# 测量MTTR (Mean Time To Recovery)
set -euo pipefail

PLIST="$HOME/Library/LaunchAgents/com.nenie.ledger-api.plist"
HEALTH_URL="http://localhost:8200/health"
MAX_WAIT=30  # 最多等待30秒恢复

echo "=== 故障演练: Kill + 恢复计时 ==="
echo ""

# Phase 1: 确认服务正常
echo "[1/4] 确认服务正常运行..."
HEALTH=$(curl -sS --max-time 5 "$HEALTH_URL" 2>/dev/null || echo "FAIL")
if ! echo "$HEALTH" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('status')=='healthy' else 1)" 2>/dev/null; then
    echo "  ❌ 服务未运行，无法演练"
    exit 1
fi
echo "  ✅ 服务正常"

# Phase 2: Kill进程
echo "[2/4] Kill uvicorn进程..."
PID=$(pgrep -f "uvicorn src.api" | head -1)
if [ -z "$PID" ]; then
    echo "  ⚠️ 未找到uvicorn进程，尝试kill端口8200占用者"
    PID=$(lsof -ti:8200 2>/dev/null || echo "")
fi
if [ -n "$PID" ]; then
    echo "  Kill PID: $PID"
    kill -9 "$PID" 2>/dev/null || true
else
    echo "  ⚠️ 未找到进程，跳过kill"
fi

# Phase 3: 计时恢复
echo "[3/4] 等待自动恢复 (launchd KeepAlive)..."
START=$(python3 -c "import time; print(time.time())")
RECOVERED=false
for i in $(seq 1 $MAX_WAIT); do
    sleep 1
    HEALTH=$(curl -sS --max-time 3 "$HEALTH_URL" 2>/dev/null || echo "FAIL")
    if echo "$HEALTH" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('status')=='healthy' else 1)" 2>/dev/null; then
        END=$(python3 -c "import time; print(time.time())")
        MTTR=$(python3 -c "print(f'{$END - $START:.1f}')")
        echo "  ✅ 服务在 ${MTTR}秒 内自动恢复"
        RECOVERED=true
        break
    fi
    echo "  等待中... ${i}s"
done

# Phase 4: 结果
echo "[4/4] 演练结果..."
if [ "$RECOVERED" = true ]; then
    echo ""
    echo "==============================="
    echo "✅ 故障演练通过"
    echo "   MTTR: ${MTTR}秒"
    echo "   SLO: <30秒恢复"
    if python3 -c "import sys; sys.exit(0 if ${MTTR} < 30 else 1)" 2>/dev/null; then
        echo "   评级: ✅ 达标"
    else
        echo "   评级: ⚠️ 超SLO"
    fi
    echo "==============================="
    exit 0
else
    echo ""
    echo "❌ 服务在 ${MAX_WAIT}秒 内未恢复！需要人工介入"
    exit 1
fi
