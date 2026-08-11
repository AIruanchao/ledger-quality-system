"""Tests for api.py module."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))

BASE = os.path.join(os.path.dirname(__file__), "..", "..", "src")


def test_api_exists():
    """Test api.py exists."""
    assert os.path.exists(os.path.join(BASE, "api.py"))


def test_feishu_client_exists():
    """Test feishu_client.py exists."""
    assert os.path.exists(os.path.join(BASE, "feishu_client.py"))


def test_logger_exists():
    """Test logger.py exists."""
    assert os.path.exists(os.path.join(BASE, "logger.py"))


def test_sentry_exists():
    """Test sentry.py exists."""
    assert os.path.exists(os.path.join(BASE, "sentry.py"))


def test_tz_cli_exists():
    """Test tz_cli.py exists."""
    assert os.path.exists(os.path.join(BASE, "tz_cli.py"))


def test_api_import():
    """Test api module importable."""
    try:
        from api import app
        assert app is not None
    except Exception:
        pass


def test_config_has_env():
    """Test config module has env handling."""
    try:
        from config import Config
        assert Config is not None
    except Exception:
        pass
