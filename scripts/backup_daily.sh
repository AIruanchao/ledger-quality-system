#!/bin/bash
# 台账系统每日备份 — 飞书Base全量导出到NDJSON
# 用法: cron每天凌晨2点执行
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${TZ_BACKUP_DIR:-$HOME/.config/tz-cli/backups}"
DATE=$(date +%Y%m%d)
BACKUP_FILE="$BACKUP_DIR/ledger-backup-${DATE}.ndjson"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

echo "=== 台账备份开始: $DATE ==="

# 用Python导出飞书全量数据（从项目根目录运行，确保package import正确）
cd "$PROJECT_DIR"
python3 -c "
import sys, json, os
# 从secrets.env加载密钥
from src.config import TABLES, FEISHU_APP_ID, FEISHU_SECRET
from src.feishu_client import FeishuClient

client = FeishuClient(FEISHU_APP_ID, FEISHU_SECRET)
with open('$BACKUP_FILE', 'w') as f:
    total = 0
    for key, (table_id, table_name) in TABLES.items():
        records = client.fetch_records(table_id)
        for record in records:
            entry = {'table': key, 'table_name': table_name, 'fields': record.get('fields', {})}
            f.write(json.dumps(entry, ensure_ascii=False) + chr(10))
            total += 1
    print(f'Written {total} records to $BACKUP_FILE')
"

# 压缩
gzip -f "$BACKUP_FILE"
echo "压缩: ${BACKUP_FILE}.gz"

# 清理旧备份（保留30天）
find "$BACKUP_DIR" -name "ledger-backup-*.ndjson.gz" -mtime +${RETENTION_DAYS} -delete
echo "清理: 删除 ${RETENTION_DAYS}天前的备份"

# 记录备份元数据
GZ_FILE="${BACKUP_FILE}.gz"
SIZE=$(stat -f%z "$GZ_FILE" 2>/dev/null || stat -c%s "$GZ_FILE" 2>/dev/null)
echo "{\"date\": \"$DATE\", \"file\": \"$GZ_FILE\", \"size\": $SIZE}" >> "$BACKUP_DIR/backup-history.jsonl"

echo "=== 备份完成 ==="
