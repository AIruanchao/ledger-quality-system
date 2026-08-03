"""
飞书 Base API 客户端 — 分页拉取 + token管理 + 空安全
修复 PIT-TZ-008: 空表 items=None → TypeError 崩溃
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any

from .config import FEISHU_APP_ID, FEISHU_BASE, FEISHU_SECRET


class FeishuClient:
    """飞书多维表格 API 客户端。"""

    def __init__(self, app_id: str = "", app_secret: str = ""):
        self._app_id = app_id or FEISHU_APP_ID
        self._app_secret = app_secret or FEISHU_SECRET
        self._token: str = ""
        self._token_expiry: float = 0

    def _get_token(self) -> str:
        """获取 tenant_access_token，带缓存。"""
        if self._token and time.time() < self._token_expiry - 60:
            return self._token
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        body = json.dumps({"app_id": self._app_id, "app_secret": self._app_secret}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        if data.get("code") != 0:
            raise RuntimeError(f"飞书token获取失败: {data.get('msg', '?')}")
        self._token = data["tenant_access_token"]
        self._token_expiry = time.time() + 7200
        return self._token

    def fetch_records(self, table_id: str, max_pages: int = 30) -> list[dict[str, Any]]:
        """
        分页拉取记录。返回规范化后的记录列表。
        PIT-TZ-008 修复: 空表 items=None → 返回空列表而非崩溃。
        """
        token = self._get_token()
        items: list[dict[str, Any]] = []
        page_token = None
        for _ in range(max_pages):
            body: dict[str, Any] = {"page_size": 500}
            if page_token:
                body["page_token"] = page_token
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE}/tables/{table_id}/records/search"
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode(),
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
            if data.get("code") != 0:
                break
            # PIT-TZ-008: data.items 可能是 None（空表）
            page_items = data.get("data", {}).get("items") or []
            items.extend(page_items)
            if not data.get("data", {}).get("has_more"):
                break
            page_token = data.get("data", {}).get("page_token")
        return items

    def count_records(self, table_id: str) -> int:
        """精确计数（用 records API 的 total 字段）。"""
        token = self._get_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE}/tables/{table_id}/records?page_size=1"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
            return data.get("data", {}).get("total", 0)
        except (urllib.error.URLError, KeyError, ValueError):
            return -1

    def get_fields(self, table_id: str) -> list[dict[str, Any]]:
        """获取表字段定义（用于 PIT-TZ-009 字段类型检查）。"""
        token = self._get_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE}/tables/{table_id}/fields"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return data.get("data", {}).get("items") or []

    @staticmethod
    def normalize(records: list[dict[str, Any]]) -> list[dict[str, str]]:
        """
        将飞书原始记录规范化为 {field_name: string_value} 字典。
        飞书字段值可能是 str / list[dict] / dict / None。
        """
        result = []
        for item in records:
            fields = item.get("fields", {})
            norm: dict[str, str] = {"_id": item.get("record_id", "")}
            for k, v in fields.items():
                norm[k] = _extract_text(v)
            result.append(norm)
        return result


def _extract_text(v: Any) -> str:
    """从飞书字段值中提取纯文本。"""
    if v is None:
        return ""
    if isinstance(v, list):
        return " ".join(
            str(x.get("text", x.get("name", ""))) if isinstance(x, dict) else str(x)
            for x in v
        )
    if isinstance(v, dict):
        return str(v.get("text", v.get("name", "")))
    return str(v)
