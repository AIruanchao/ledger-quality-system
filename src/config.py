"""
统一配置模块 — fail-closed 模式
密钥从环境变量或 ~/.config/tz-cli/secrets.env 加载，缺失则报错退出。
"""
import os
import sys
from pathlib import Path

_SECRETS_FILE = Path.home() / ".config" / "tz-cli" / "secrets.env"


def _load_secrets() -> None:
    """从 secrets.env 加载密钥到 os.environ（如果尚未设置）。"""
    if not _SECRETS_FILE.exists():
        return
    for line in _SECRETS_FILE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


_load_secrets()

_REQUIRED = [
    "TZ_FEISHU_BASE",
    "TZ_FEISHU_APP_ID",
    "TZ_FEISHU_SECRET",
]


def _require(key: str) -> str:
    val = os.environ.get(key, "")
    if not val:
        missing = [k for k in _REQUIRED if not os.environ.get(k)]
        if missing:
            print(f"❌ 缺少环境变量: {', '.join(missing)}", file=sys.stderr)
            print(f"请配置 {_SECRETS_FILE} 或设置环境变量", file=sys.stderr)
            sys.exit(78)
    return val


# === 飞书配置 ===
FEISHU_BASE: str = _require("TZ_FEISHU_BASE")
FEISHU_APP_ID: str = _require("TZ_FEISHU_APP_ID")
FEISHU_SECRET: str = _require("TZ_FEISHU_SECRET")

# === ERP配置 ===
ERP_URL: str = os.environ.get("TZ_ERP_URL", "https://erp.nenie.vip")
ERP_TOKEN: str = os.environ.get("TZ_ERP_TOKEN", "")

# === HT配置 ===
HT_URL: str = os.environ.get("TZ_HT_URL", "https://ht.nenie.vip")
HT_SSH_HOST: str = os.environ.get("TZ_TEST_HT_HOST", "root@124.222.234.8")

# === 飞书表映射 ===
TABLES: dict[str, tuple[str, str]] = {
    "contracts": ("tblUoePy2xtMjEKw", "合同台账"),
    "orders": ("tblPz5NWcTLEIvzz", "订单台账"),
    "purchases": ("tblHksqo8ip6qVtS", "采购台账"),
    "invoices": ("tblQzV96UMpxsPoT", "发票管理"),
    "payments": ("tblYECXX2qnSJWGf", "回款单"),
    "deliveries": ("tbldwaTLyb4Ujlqw", "交付跟踪"),
    "quotes": ("tbllOfOsIlJcEQAR", "报价台账"),
    "logs": ("tblREjNGKJ0rUxRb", "操作日志"),
}
