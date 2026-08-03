"""
PIT-TZ-010 单元测试: 合同状态变更后排除规则同步。
"""
from src.gates.data_quality import check_null_rate
from src.validators.schema import ContractRecord


class TestStatusExclusion:
    """PIT-TZ-010: 已终止合同应被空值检查排除（同PIT-TZ-003逻辑）。"""

    def test_terminated_contract_excluded(self):
        """已终止合同空值不计入。"""
        records = [
            {"合同编号": "C1", "对方公司": "A公司", "合同状态": "✅ 已批准"},
            {"合同编号": "T1", "对方公司": "", "合同状态": "⚪ 已终止"},
        ]
        ok, rate = check_null_rate(records, "对方公司")
        assert ok
        assert rate == 0.0

    def test_contract_record_is_active(self):
        """ContractRecord.is_active 属性正确判断。"""
        active = ContractRecord(合同编号="C1", 对方公司="A", 合同金额=1000, 合同状态="✅ 已批准")
        draft = ContractRecord(合同编号="D1", 对方公司="B", 合同金额=0, 合同状态="📝 草稿")
        terminated = ContractRecord(合同编号="T1", 对方公司="C", 合同金额=0, 合同状态="⚪ 已终止")

        assert active.is_active
        assert not draft.is_active
        assert not terminated.is_active
