"""
config.py 单元测试 — 密钥加载和fail-closed逻辑。
注意: test_missing_secret在独立进程执行（防止sys.exit杀掉pytest）。
"""
import subprocess
import sys
from pathlib import Path


class TestConfigLoader:
    """config.py 密钥加载测试。"""

    def test_tables_dict_structure(self):
        """TABLES字典结构正确。"""
        from src.config import TABLES
        assert isinstance(TABLES, dict)
        assert len(TABLES) == 8
        for key, val in TABLES.items():
            assert isinstance(val, tuple)
            assert len(val) == 2
            assert isinstance(val[0], str)  # table_id
            assert isinstance(val[1], str)  # table_name

    def test_required_env_vars_defined(self):
        """必需的环境变量列表正确。"""
        from src.config import FEISHU_APP_ID, FEISHU_BASE, FEISHU_SECRET
        assert FEISHU_BASE
        assert FEISHU_APP_ID
        assert FEISHU_SECRET

    def test_erp_url_has_default(self):
        """ERP_URL有默认值。"""
        from src.config import ERP_URL
        assert "enie.vip" in ERP_URL or "localhost" in ERP_URL

    def test_ht_ssh_host_defined(self):
        """HT_SSH_HOST有默认值。"""
        from src.config import HT_SSH_HOST
        assert HT_SSH_HOST

    def test_missing_secret_exits_with_78(self):
        """密钥缺失时sys.exit(78)。在子进程执行，不影响pytest主进程。"""
        # 在独立进程中测试，设置HOME到不存在的路径
        result = subprocess.run(
            [sys.executable, "-c",
             """
import sys, os
# 清除密钥环境变量
for k in ['TZ_FEISHU_BASE', 'TZ_FEISHU_APP_ID', 'TZ_FEISHU_SECRET']:
    os.environ.pop(k, None)
# 设置HOME到不存在的路径（secrets.env不存在）
os.environ['HOME'] = '/nonexistent_path_12345'
sys.path.insert(0, 'src')
try:
    import config
except SystemExit as e:
    assert e.code == 78, f"Expected exit code 78, got {e.code}"
else:
    raise AssertionError("Expected SystemExit(78) but import succeeded")
"""],
            capture_output=True, text=True, timeout=10,
            cwd=str(Path(__file__).parent.parent.parent),
        )
        assert result.returncode == 0, f"Subprocess failed: {result.stderr[:200]}"
