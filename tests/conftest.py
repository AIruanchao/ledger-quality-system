"""
pytest 全局配置和 fixture。
- unit 测试：纯逻辑，不需要外部依赖
- integration 测试：需要飞书API
- E2E测试：需要飞书+HT+ERP
"""
import sys
from pathlib import Path

import pytest

# 确保 src 在 import path 中
sys.path.insert(0, str(Path(__file__).parent.parent))


# ==================== Unit Test Fixtures ====================

@pytest.fixture
def sample_contract_records():
    """模拟合同台账数据（用于unit test）。"""
    return [
        {"合同编号": "HT-2026-001", "对方公司": "深圳科技有限公司", "合同金额": "50000",
         "合同状态": "✅ 已批准", "台数": "10", "单价": "5000", "产品型号": "iPhone 15 Pro",
         "到期日期": "2026-12-31"},
        {"合同编号": "HT-2026-002", "对方公司": "北京网络科技公司", "合同金额": "36000",
         "合同状态": "✅ 已批准", "台数": "12", "单价": "3000", "产品型号": "MacBook Pro",
         "到期日期": "2027-06-30"},
        {"合同编号": "HT-2026-003", "对方公司": "", "合同金额": "0",
         "合同状态": "📝 草稿", "台数": "", "单价": "", "产品型号": "",
         "到期日期": ""},
    ]


@pytest.fixture
def sample_bad_records():
    """包含各种PIT-TZ问题的脏数据（用于unit test验证检测能力）。"""
    return [
        # PIT-TZ-002: 配置串入
        {"合同编号": "BAD-001", "产品型号": "12+256", "对方公司": "某公司",
         "合同金额": "10000", "合同状态": "✅ 已批准", "台数": "5", "单价": "2000"},
        # PIT-TZ-004: 金额≠单价×台数
        {"合同编号": "BAD-002", "合同金额": "99999", "单价": "100", "台数": "10",
         "合同状态": "✅ 已批准", "对方公司": "某公司", "产品型号": "正常型号"},
        # PIT-TZ-001: 日期是时间戳
        {"合同编号": "BAD-003", "到期日期": "1778601600000",
         "合同金额": "100", "合同状态": "✅ 已批准", "对方公司": "某公司"},
    ]


# ==================== Integration/E2E Fixtures ====================

@pytest.fixture(scope="session")
def feishu_client():
    """飞书客户端实例（session级别共享token）。"""
    try:
        from src.feishu_client import FeishuClient
        return FeishuClient()
    except SystemExit:
        pytest.skip("飞书密钥未配置，跳过集成测试")


@pytest.fixture(scope="session")
def contracts(feishu_client):
    """拉取合同台账全量数据（session级别缓存）。"""
    from src.config import TABLES
    table_id = TABLES["contracts"][0]
    raw = feishu_client.fetch_records(table_id)
    return feishu_client.normalize(raw)
