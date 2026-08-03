#!/bin/bash
# 台账系统部署脚本 — systemd保活
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="ledger-api"
SERVICE_PATH="$HOME/Library/LaunchAgents/com.nenie.ledger-api.plist"

echo "=== 台账API部署 ==="

# macOS用launchd而非systemd
mkdir -p "$(dirname "$SERVICE_PATH")"
mkdir -p "$PROJECT_DIR/logs"

cat > "$SERVICE_PATH" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.nenie.ledger-api</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/maccc/Projects/ledger-quality-system/.venv311/bin/uvicorn</string>
        <string>src.api:app</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8200</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/maccc/Projects/ledger-quality-system</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>/Users/maccc/Projects/ledger-quality-system</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/maccc/Projects/ledger-quality-system/logs/ledger-api.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/maccc/Projects/ledger-quality-system/logs/ledger-api-error.log</string>
</dict>
</plist>
PLIST

# 停止旧的（如果有）
launchctl unload "$SERVICE_PATH" 2>/dev/null || true

# 启动
launchctl load "$SERVICE_PATH"
echo "✅ 台账API已部署 (launchd KeepAlive=true)"
echo "   端口: 8200"
echo "   日志: $PROJECT_DIR/logs/"
echo "   停止: launchctl unload $SERVICE_PATH"
echo "   启动: launchctl load $SERVICE_PATH"

# 等待启动
sleep 3

# 验证
curl -sS --max-time 5 http://localhost:8200/ 2>&1 || echo "⚠️ 服务还在启动中..."
