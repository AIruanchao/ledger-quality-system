"""
PIT-TZ-009 单元测试: 幂等key字段必须是可写类型。
"""
from src.validators.schema import check_idempotency_field


class TestIdempotencyField:
    """PIT-TZ-009: 银行凭证号字段 type=1(Text/可写) 而非 type=1005(AutoNumber/不可写)。"""

    def test_text_type_passes(self):
        """type=1 是文本类型，可写 → PASS。"""
        assert check_idempotency_field({"field_name": "银行凭证号", "type": 1})

    def test_autonumber_fails(self):
        """type=1005 是自动编号，API写入被忽略 → FAIL。"""
        assert not check_idempotency_field({"field_name": "银行凭证号", "type": 1005})

    def test_other_type_fails(self):
        """其他类型也不可靠 → FAIL。"""
        assert not check_idempotency_field({"field_name": "银行凭证号", "type": 2})

    def test_missing_type_fails(self):
        """缺type字段 → FAIL。"""
        assert not check_idempotency_field({"field_name": "银行凭证号"})
