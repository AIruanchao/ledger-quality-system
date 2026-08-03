"""
Pydantic Schema 契约测试 — 验证数据模型本身的约束。
"""
import pytest
from pydantic import ValidationError

from src.validators.schema import ContractRecord, validate_null_rate


class TestContractSchema:
    """ContractRecord 数据契约验证。"""

    def test_valid_contract(self):
        """合法合同 → 创建成功。"""
        c = ContractRecord(
            合同编号="HT-2026-001",
            对方公司="深圳科技",
            合同金额=50000,
            台数=10,
            单价=5000,
            合同状态="✅ 已批准",
        )
        assert c.合同金额 == 50000

    def test_empty_contract_no_rejected(self):
        """空合同编号 → 拒绝。"""
        with pytest.raises(ValidationError):
            ContractRecord(合同编号="", 对方公司="A", 合同金额=100)

    def test_negative_amount_rejected(self):
        """负金额 → 拒绝。"""
        with pytest.raises(ValidationError):
            ContractRecord(合同编号="X1", 对方公司="A", 合同金额=-100)

    def test_amount_mismatch_rejected(self):
        """金额≠单价×台数 → 拒绝。"""
        with pytest.raises(ValidationError) as exc_info:
            ContractRecord(
                合同编号="X1", 对方公司="A", 合同金额=99999,
                台数=10, 单价=100,
            )
        assert "PIT-TZ-004" in str(exc_info.value)

    def test_config_contamination_rejected(self):
        """产品型号串入配置 → 拒绝。"""
        with pytest.raises(ValidationError) as exc_info:
            ContractRecord(
                合同编号="X1", 对方公司="A", 合同金额=1000,
                产品型号="12+256",
            )
        assert "PIT-TZ-002" in str(exc_info.value)

    def test_null_rate_function(self):
        """validate_null_rate 函数测试。"""
        records = [
            {"合同编号": "C1", "对方公司": "A", "合同状态": "✅ 已批准"},
            {"合同编号": "C2", "对方公司": "", "合同状态": "✅ 已批准"},
        ]
        ok, rate = validate_null_rate(records, "对方公司")
        assert not ok
        assert rate == 0.5
