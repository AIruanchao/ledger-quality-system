#!/bin/bash
# 台账系统每日备份 — 飞书Base全量导出到NDJSON
# 用法: cron每天凌晨2点执行
set -euo pipefail

BACKUP_DIR="${TZ_BACKUP_DIR:-$HOME/.config/tz-cli/backups}"
DATE=$(date +%Y%m%d)
BACKUP_FILE="$BACKUP_DIR/ledger-backup-${DATE}.ndjson"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"

echo "=== 台账备份开始: $DATE ==="

# 用Python导出飞书全量数据
python3 -c "
import sys, json, os
sys.path.insert(0, '$PWD/src')
from config import TABLES, FEISHU_APP_ID, FEISHU_SECRET, FEISHU_BASE
from feishu_client import FeishuClient

client = FeishuClient(FEISHU_APP_ID, FEISHU_SECRET)
with open('$BACKUP_FILE', 'w') as f:
    for key, (table_id, table_name) in TABLES.items():
        records = client.fetch_records(table_id)
        for record in records:
            entry = {'table': key, 'table_name': table_name, 'fields': record.get('fields', {})}
            f.write(json.dumps(entry, ensure_ascii=False) + chr(10))
    print(f'Written to $BACKUP_FILE')
"

# 压缩
gzip -f "$BACKUP_FILE"
echo "压缩: ${BACKUP_FILE}.gz"

# 清理旧备份（保留30天）
find "$BACKUP_DIR" -name "ledger-backup-*.ndjson.gz" -mtime +${RETENTION_DAYS} -delete
echo "清理: 删除 ${RETENTION_DAYS}天前的备份"

# 记录备份元数据
echo "{\"date\": \"$DATE\", \"file\": \"${BACKUP_FILE}.gz\", \"size\": $(stat -f%z "${BACKUP_FILE}.gz" 2>/dev/null || stat -c%s "${BACKUP_FILE}.gz" 2>/dev/null)}" >> "$BACKUP_DIR/backup-history.jsonl"

echo "=== 备份完成 ==="
