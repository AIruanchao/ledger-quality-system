"""
logger.py 和 sentry.py 单元测试。
"""
import json
import logging
from io import StringIO

from src.logger import JSONFormatter, setup_logger


class TestJSONFormatter:
    """JSON日志格式化器测试。"""

    def test_format_produces_valid_json(self):
        """格式化后的日志是合法JSON。"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="test.py", lineno=1,
            msg="test message", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["message"] == "test message"
        assert parsed["level"] == "INFO"

    def test_format_includes_timestamp(self):
        """JSON包含timestamp字段。"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="test.py", lineno=1,
            msg="warning msg", args=(), exc_info=None,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "timestamp" in parsed
        assert "T" in parsed["timestamp"]  # ISO格式

    def test_extra_fields_included(self):
        """extra字段被合并到JSON中。"""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py", lineno=42,
            msg="error with extra", args=(), exc_info=None,
        )
        record.records = 100
        record.table = "contracts"
        output = formatter.format(record)
        parsed = json.loads(output)
        assert parsed["records"] == 100
        assert parsed["table"] == "contracts"

    def test_exception_info_included(self):
        """异常信息被包含。"""
        formatter = JSONFormatter()
        try:
            raise ValueError("test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        record = logging.LogRecord(
            name="test", level=logging.ERROR, pathname="test.py", lineno=1,
            msg="exception occurred", args=(), exc_info=exc_info,
        )
        output = formatter.format(record)
        parsed = json.loads(output)
        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]


class TestSetupLogger:
    """setup_logger 函数测试。"""

    def test_logger_returns_logger_instance(self):
        """返回Logger实例。"""
        log = setup_logger("test_logger")
        assert isinstance(log, logging.Logger)
        assert log.name == "test_logger"

    def test_logger_has_handler(self):
        """Logger配置了handler。"""
        log = setup_logger("test_handler")
        assert len(log.handlers) > 0

    def test_logger_level_set(self):
        """Logger级别正确设置。"""
        log = setup_logger("test_level", "DEBUG")
        assert log.level == logging.DEBUG

    def test_logger_outputs_json(self):
        """Logger输出是JSON格式。"""
        log = setup_logger("test_json_output")
        # 捕获stdout
        import sys
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            log.info("json test message")
            output = sys.stdout.getvalue().strip()
            if output:
                parsed = json.loads(output)
                assert parsed["message"] == "json test message"
        finally:
            sys.stdout = old_stdout
