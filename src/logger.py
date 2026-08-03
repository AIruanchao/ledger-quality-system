"""
结构化日志模块 — JSON格式输出，可对接ELK/Loki/Sentry。
替代 print() 的企业级日志方案。
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

# Python 3.11+ 用 UTC alias，3.10 用 timezone.utc
try:
    from datetime import UTC as _UTC
except ImportError:
    _UTC = timezone.utc
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON行格式化器，每条日志一行JSON。"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(_UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        # 合并extra字段
        for key, value in record.__dict__.items():
            if key not in ("name", "msg", "args", "levelname", "levelno", "pathname",
                           "filename", "module", "exc_info", "exc_text", "stack_info",
                           "lineno", "funcName", "created", "msecs", "relativeCreated",
                           "thread", "threadName", "processName", "process", "message"):
                log_entry[key] = value
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logger(name: str = "ledger", level: str = "INFO") -> logging.Logger:
    """
    设置结构化日志器。

    用法:
        from src.logger import setup_logger
        log = setup_logger("ledger")
        log.info("备份完成", extra={"records": 15135, "table": "contracts"})
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)

    return logger
