"""
Sentry错误追踪集成 — 生产环境异常自动上报。
开发环境禁用（DSN为空）。
"""
from __future__ import annotations

import logging
import os
from typing import Any


def init_sentry() -> bool:
    """
    初始化Sentry。SENTRY_DSN未配置时跳过。

    用法:
        from src.sentry import init_sentry
        init_sentry()
    """
    dsn = os.environ.get("SENTRY_DSN", "")
    if not dsn:
        return False

    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_sdk.init(
            dsn=dsn,
            environment=os.environ.get("SENTRY_ENV", "production"),
            traces_sample_rate=0.1,
            send_default_pii=False,
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,
                    event_level=logging.ERROR,
                ),
            ],
        )
        return True
    except ImportError:
        # sentry-sdk未安装，降级为print
        print("[WARN] sentry-sdk not installed, error tracking disabled")
        return False


def capture_exception(exc: Exception, extra: dict[str, Any] | None = None) -> None:
    """手动上报异常。Sentry未启用时降级为日志。"""
    dsn = os.environ.get("SENTRY_DSN", "")
    if dsn:
        try:
            import sentry_sdk
            if extra:
                sentry_sdk.set_context("extra", extra)
            sentry_sdk.capture_exception(exc)
        except ImportError:
            pass
    else:
        # 降级：输出到stderr
        import sys
        print(f"[ERROR] {type(exc).__name__}: {exc}", file=sys.stderr)
        if extra:
            print(f"  extra: {extra}", file=sys.stderr)
