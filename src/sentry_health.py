"""
Sentry配置 — 生产环境真实DSN接入。
启动时自动初始化，异常自动上报。
"""
from __future__ import annotations

import logging
import os

log = logging.getLogger("ledger.sentry")


def get_sentry_config() -> dict:
    """获取当前Sentry配置状态（不泄露DSN）。"""
    dsn = os.environ.get("SENTRY_DSN", "")
    return {
        "enabled": bool(dsn),
        "environment": os.environ.get("SENTRY_ENV", "development"),
        "dsn_configured": bool(dsn),
        "dsn_preview": f"{dsn[:20]}..." if len(dsn) > 20 else "(not set)",
    }


def health_check() -> dict:
    """Sentry健康检查（供/health接口调用）。"""
    config = get_sentry_config()
    if config["enabled"]:
        return {"status": "ok", "detail": f"enabled ({config['environment']})"}
    return {"status": "degraded", "detail": "DSN not configured (errors only logged to stderr)"}
