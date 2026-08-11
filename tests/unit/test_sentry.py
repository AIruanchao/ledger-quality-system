"""
sentry.py 单元测试。
"""

import sys

from src.sentry import capture_exception, init_sentry


class TestSentryInit:
    """Sentry初始化测试。"""

    def test_init_without_dsn_returns_false(self, monkeypatch):
        """SENTRY_DSN未配置 → 返回False。"""
        monkeypatch.delenv("SENTRY_DSN", raising=False)
        assert init_sentry() is False

    def test_init_with_dsn_but_no_sdk(self, monkeypatch):
        """有DSN但sentry-sdk未安装 → 返回False。"""
        monkeypatch.setenv("SENTRY_DSN", "https://fake@sentry.io/1")
        # 模拟sentry-sdk未安装：sys.modules中置None使import引发ImportError
        monkeypatch.setitem(sys.modules, "sentry_sdk", None)
        monkeypatch.setitem(sys.modules, "sentry_sdk.integrations.logging", None)
        result = init_sentry()
        assert result is False


class TestCaptureException:
    """capture_exception 降级测试。"""

    def test_capture_without_sentry(self, monkeypatch, capsys):
        """Sentry未启用时降级到stderr。"""
        monkeypatch.delenv("SENTRY_DSN", raising=False)
        exc = ValueError("test error")
        capture_exception(exc, extra={"table": "contracts"})
        captured = capsys.readouterr()
        assert "ValueError" in captured.err
        assert "test error" in captured.err

    def test_capture_with_extra(self, monkeypatch, capsys):
        """extra字段输出。"""
        monkeypatch.delenv("SENTRY_DSN", raising=False)
        capture_exception(RuntimeError("boom"), extra={"count": 42})
        captured = capsys.readouterr()
        assert "42" in captured.err
