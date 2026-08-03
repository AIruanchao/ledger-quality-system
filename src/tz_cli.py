"""
tz-cli 迁移包装器 — 从标准包结构调用台账CLI。
原始tz-cli在 /opt/hermes/agents/dachui80/scripts/tz-cli (315行Python)，
本模块提供importable接口，供CI和测试调用。

用法:
    from src.tz_cli import LedgerCLI
    cli = LedgerCLI()
    cli.stats()
"""
from __future__ import annotations

import json
from typing import Any

from .config import ERP_TOKEN, ERP_URL, TABLES


class LedgerCLI:
    """台账CLI — 三系统(飞书/ERP/HT)统一查询接口。"""

    def __init__(self) -> None:
        from .feishu_client import FeishuClient
        self.feishu = FeishuClient()

    def stats(self) -> dict[str, int]:
        """台账数据总览（8张飞书表+3个ERP端点）。"""
        result: dict[str, int] = {}
        for key, (tid, name) in TABLES.items():
            count = self.feishu.count_records(tid)
            result[name] = count
        return result

    def list_tables(self) -> list[str]:
        """列出所有台账表名。"""
        return [name for _, name in TABLES.values()]

    def query(self, table_key: str, keyword: str | None = None, limit: int = 20) -> list[dict[str, str]]:
        """查台账记录。"""
        if table_key not in TABLES:
            raise ValueError(f"未知表: {table_key}，可选: {list(TABLES.keys())}")
        tid, _ = TABLES[table_key]
        raw = self.feishu.fetch_records(tid)
        records = self.feishu_client_normalize(raw)
        if keyword:
            records = [r for r in records if keyword.lower() in str(r).lower()]
        return records[:limit]

    def feishu_client_normalize(self, raw: list[dict[str, Any]]) -> list[dict[str, str]]:
        """规范化飞书原始记录。"""
        from .feishu_client import FeishuClient
        return FeishuClient.normalize(raw)

    def erp_api(self, path: str) -> dict[str, Any]:
        """调用ERP外部API。"""
        import urllib.request
        url = f"{ERP_URL}/api/external/{path}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {ERP_TOKEN}"})
        import urllib.error
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read())
        except (urllib.error.HTTPError, OSError) as e:
            return {"error": str(e)[:100]}
