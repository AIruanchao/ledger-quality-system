#!/bin/bash
# 外部探针 — 每分钟探测台账API可用性，记录SLI数据
# cron: * * * * * bash scripts/uptime_probe.sh
set -euo pipefail

DATA_FILE="${TZ_SLI_DATA:-$HOME/.config/tz-cli/sli_data.jsonl}"
URL="http://localhost:8200/health"
mkdir -p "$(dirname "$DATA_FILE")"

# 探测+记录
TIMESTAMP=$(python3 -c "from datetime import datetime,timezone; print(datetime.now(timezone.utc).isoformat())")
START=$(python3 -c "import time; print(time.time())")

HTTP_CODE=$(curl -sS -o /tmp/ledger_probe.json -w "%{http_code}" --max-time 5 "$URL" 2>/dev/null || echo "000")
END=$(python3 -c "import time; print(time.time())")
LATENCY_MS=$(python3 -c "print(int(($END - $START) * 1000))")

# 判断可用
if [ "$HTTP_CODE" = "200" ]; then
    STATUS="up"
    # 解析健康检查结果
    OVERALL=$(python3 -c "import json; print(json.load(open('/tmp/ledger_probe.json')).get('status','?'))" 2>/dev/null || echo "?")
else
    STATUS="down"
    OVERALL="unreachable"
fi

# 追加SLI记录
echo "{\"ts\": \"$TIMESTAMP\", \"status\": \"$STATUS\", \"http_code\": \"$HTTP_CODE\", \"latency_ms\": $LATENCY_MS, \"health\": \"$OVERALL\"}" >> "$DATA_FILE"

# 保留最近7天数据
python3 -c "
import json
from datetime import datetime, timezone, timedelta
cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
lines = []
for line in open('$DATA_FILE'):
    try:
        d = json.loads(line)
        if d.get('ts','') >= cutoff:
            lines.append(line)
    except: pass
with open('$DATA_FILE', 'w') as f:
    f.writelines(lines)
"

# 如果down，输出告警（cron可捕获到飞书通知）
if [ "$STATUS" = "down" ]; then
    echo "🚨 台账API不可达: HTTP=$HTTP_CODE ($TIMESTAMP)"
    exit 1
fi
