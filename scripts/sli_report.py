#!/usr/bin/env python3
"""
SLI报告生成器 — 从探针数据计算可用率和延迟分布。
用法: python3 scripts/sli_report.py [days]
"""
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".config" / "tz-cli" / "sli_data.jsonl"
SLO_TARGET = 99.5
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 1


def main():
    if not DATA_FILE.exists():
        print(f"❌ 无SLI数据: {DATA_FILE}")
        print("   先运行: bash scripts/uptime_probe.sh")
        sys.exit(1)

    cutoff = (datetime.now(UTC) - timedelta(days=DAYS)).isoformat()
    records = []
    for line in DATA_FILE.read_text().splitlines():
        try:
            d = json.loads(line)
            if d.get("ts", "") >= cutoff:
                records.append(d)
        except json.JSONDecodeError:
            continue

    if not records:
        print(f"❌ 最近{DAYS}天无SLI数据")
        sys.exit(1)

    total = len(records)
    up = sum(1 for r in records if r["status"] == "up")
    down = total - up
    availability = (up / total * 100) if total else 0

    # 延迟统计
    latencies = sorted(r["latency_ms"] for r in records if r["status"] == "up")
    if latencies:
        p50 = latencies[len(latencies) // 2]
        p99 = latencies[int(len(latencies) * 0.99)]
        avg = sum(latencies) / len(latencies)
    else:
        p50 = p99 = avg = 0

    print(f"{'=' * 50}")
    print(f"台账系统 SLI 报告 (最近{DAYS}天)")
    print(f"{'=' * 50}")
    print(f"总探测次数: {total}")
    print(f"可用: {up} | 不可用: {down}")
    print("")
    print(f"可用率: {availability:.2f}%")
    print(f"SLO目标: {SLO_TARGET}%")
    if availability >= SLO_TARGET:
        print("状态: ✅ 达标")
    else:
        budget_used = (100 - availability) / (100 - SLO_TARGET) * 100
        print(f"状态: ❌ 未达标 (Error Budget已用 {budget_used:.0f}%)")
    print("")
    print("延迟分布 (可用时):")
    print(f"  P50: {p50}ms")
    print(f"  P99: {p99}ms")
    print(f"  平均: {avg:.0f}ms")
    print("")

    # 故障时间段
    if down > 0:
        print("故障记录:")
        for r in records:
            if r["status"] == "down":
                print(f"  {r['ts']}: HTTP={r['http_code']}")

    return 0 if availability >= SLO_TARGET else 1


if __name__ == "__main__":
    sys.exit(main())
