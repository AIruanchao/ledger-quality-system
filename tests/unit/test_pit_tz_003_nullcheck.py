"""
PIT-TZ-003/010 单元测试: 空值检查排除草稿+已终止状态。
"""
from src.gates.data_quality import check_null_rate


class TestNullRateCheck:
    """PIT-TZ-003: 草稿空值不计入空值率。"""

    def test_active_contract_null_detected(self):
        """活跃合同空值率超10% → FAIL。"""
        records = [
            {"合同编号": "C1", "对方公司": "A公司", "合同状态": "✅ 已批准"},
            {"合同编号": "C2", "对方公司": "", "合同状态": "✅ 已批准"},  # 空值
        ]
        ok, rate = check_null_rate(records, "对方公司")
        assert not ok, f"空值率{rate}应该超标"
        assert rate == 0.5

    def test_draft_excluded_from_null_check(self):
        """草稿合同空值不计入。"""
        records = [
            {"合同编号": "C1", "对方公司": "A公司", "合同状态": "✅ 已批准"},
            {"合同编号": "D1", "对方公司": "", "合同状态": "📝 草稿"},  # 草稿排除
        ]
        ok, rate = check_null_rate(records, "对方公司")
        assert ok, f"草稿空值不该算，rate={rate}"
        assert rate == 0.0

    def test_terminated_excluded(self):
        """已终止合同排除。"""
        records = [
            {"合同编号": "C1", "对方公司": "A公司", "合同状态": "✅ 已批准"},
            {"合同编号": "T1", "对方公司": "", "合同状态": "⚪ 已终止"},
        ]
        ok, rate = check_null_rate(records, "对方公司")
        assert ok
        assert rate == 0.0

    def test_empty_records_passes(self):
        """空列表 → PASS。"""
        ok, rate = check_null_rate([], "对方公司")
        assert ok
        assert rate == 0.0
