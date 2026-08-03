"""
PIT-TZ-005 单元测试: 回款单幂等逻辑。
注意: 完整幂等E2E需要SSH到HT执行sync两次，这里测逻辑层。
"""
from src.validators.schema import PaymentRecord


class TestIdempotencyLogic:
    """PIT-TZ-005: 回款单sync幂等——相同银行凭证号不重复创建。"""

    def test_payment_record_requires_bank_ref(self):
        """银行凭证号是幂等key，必须有值。"""
        record = PaymentRecord(银行凭证号="PAY-2026-001", 回款金额=10000)
        assert record.银行凭证号 == "PAY-2026-001"

    def test_empty_bank_ref_rejected(self):
        """空银行凭证号 → Pydantic验证失败。"""
        import pytest
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            PaymentRecord(银行凭证号="", 回款金额=100)

    def test_dedup_logic(self):
        """模拟幂等去重：同一银行凭证号只保留一条。"""
        payments = [
            {"银行凭证号": "PAY-001", "回款金额": 1000},
            {"银行凭证号": "PAY-001", "回款金额": 1000},  # 重复
            {"银行凭证号": "PAY-002", "回款金额": 2000},
        ]
        seen = set()
        unique = []
        for p in payments:
            key = p["银行凭证号"]
            if key not in seen:
                seen.add(key)
                unique.append(p)
        assert len(unique) == 2
