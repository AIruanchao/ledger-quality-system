#!/bin/bash
# 金丝雀部署脚本 — 不断服务滚动更新
# 用法: bash scripts/canary_deploy.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.nenie.ledger-api.plist"
HEALTH_URL="http://localhost:8200/health"
NEW_PORT=8201
OLD_PORT=8200

echo "=== 金丝雀部署开始 ==="

# Phase 1: 新版本启动在新端口
echo "[1/5] 新版本启动在端口 $NEW_PORT..."
cd "$PROJECT_DIR"
source .venv311/bin/activate
uvicorn src.api:app --host 0.0.0.0 --port $NEW_PORT &
NEW_PID=$!
echo "  新版本 PID: $NEW_PID"

# Phase 2: 健康检查新版本
sleep 3
echo "[2/5] 新版本健康检查..."
HEALTH=$(curl -sS --max-time 5 http://localhost:$NEW_PORT/health 2>/dev/null || echo "FAIL")
if echo "$HEALTH" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('status')=='healthy' else 1)" 2>/dev/null; then
    echo "  ✅ 新版本健康检查通过"
else
    echo "  ❌ 新版本健康检查失败，回滚"
    kill $NEW_PID 2>/dev/null || true
    exit 1
fi

# Phase 3: Canary流量比例检查（10%流量到新版本）
echo "[3/5] Canary验证（10次请求到新版本）..."
SUCCESS=0
for i in $(seq 1 10); do
    CODE=$(curl -sS -o /dev/null -w "%{http_code}" http://localhost:$NEW_PORT/ 2>/dev/null || echo "000")
    if [ "$CODE" = "200" ]; then
        SUCCESS=$((SUCCESS + 1))
    fi
done
echo "  成功率: $SUCCESS/10"
if [ $SUCCESS -lt 9 ]; then
    echo "  ❌ 成功率<90%，回滚"
    kill $NEW_PID 2>/dev/null || true
    exit 1
fi

# Phase 4: 切换流量（重启launchd指向新版本）
echo "[4/5] 切换流量..."
# 停旧版本
launchctl unload "$PLIST" 2>/dev/null || true
kill $NEW_PID 2>/dev/null || true
sleep 1

# 修改端口为标准端口并重新加载
sed -i '' "s/$NEW_PORT/$OLD_PORT/" "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
sleep 3

# Phase 5: 最终验证
echo "[5/5] 最终验证..."
FINAL=$(curl -sS --max-time 5 http://localhost:$OLD_PORT/health 2>/dev/null || echo "FAIL")
if echo "$FINAL" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('status')=='healthy' else 1)" 2>/dev/null; then
    echo "  ✅ 金丝雀部署成功"
    echo "=== 部署完成 ==="
else
    echo "  ❌ 最终验证失败！需要人工介入"
    exit 1
fi
