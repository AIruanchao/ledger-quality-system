"""
统一告警 — 飞书通知。
"""
from __future__ import annotations

import json
import os
import urllib.request


class AlertManager:
    """台账系统告警管理器。"""

    def __init__(self) -> None:
        self._webhook_url = os.environ.get("TZ_ALERT_WEBHOOK", "")

    def send(self, level: str, title: str, detail: str) -> bool:
        """
        发送告警通知。
        level: CRITICAL / WARNING / INFO
        """
        if not self._webhook_url:
            # 没配webhook时只打stdout
            print(f"[{level}] {title}: {detail}")
            return False

        emoji = {"CRITICAL": "🚨", "WARNING": "⚠️", "INFO": "ℹ️"}.get(level, "❓")
        msg = f"{emoji} [{level}] {title}\n{detail}"

        body = json.dumps({"msg_type": "text", "content": {"text": msg}}).encode()
        req = urllib.request.Request(
            self._webhook_url, data=body,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.status == 200
        except Exception:
            return False

    def alert_on_unhealthy(self, health_summary: dict[str, str]) -> list[str]:
        """根据健康检查结果发送告警。返回告警的组件列表。"""
        alerted: list[str] = []
        for component, status in health_summary.items():
            if status != "ok":
                self.send(
                    level="CRITICAL",
                    title=f"台账系统: {component} 不可用",
                    detail=f"组件状态: {status}",
                )
                alerted.append(component)
        return alerted
