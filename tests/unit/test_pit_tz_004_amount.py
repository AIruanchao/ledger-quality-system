"""
PIT-TZ-004 单元测试: 金额 = 单价 × 台数。
"""
from src.gates.data_quality import check_amount_logic


class TestAmountLogic:
    """PIT-TZ-004: 金额必须等于单价×台数（偏差<1%）。"""

    def test_correct_amount_passes(self, sample_contract_records):
        """金额正确的记录 → 无错误。"""
        errors = check_amount_logic(sample_contract_records)
        # sample_contract_records[0]: 5000*10=50000 ✓
        # sample_contract_records[1]: 3000*12=36000 ✓
        # sample_contract_records[2]: 草稿，price/qty为空→跳过
        assert errors == [], f"金额逻辑错误: {errors}"

    def test_wrong_amount_detected(self, sample_bad_records):
        """金额≠单价×台数 → 检测到错误。"""
        errors = check_amount_logic(sample_bad_records)
        # BAD-002: 99999 ≠ 100×10=1000
        assert any("BAD-002" in e for e in errors), f"未检测到金额错误: {errors}"

    def test_zero_price_skipped(self):
        """单价或台数为0 → 跳过检查。"""
        records = [
            {"合同编号": "Z1", "合同金额": "100", "单价": "0", "台数": "5"},
        ]
        errors = check_amount_logic(records)
        assert errors == []

    def test_missing_amount_skipped(self):
        """金额为空 → 跳过检查。"""
        records = [
            {"合同编号": "M1", "合同金额": "", "单价": "100", "台数": "5"},
        ]
        errors = check_amount_logic(records)
        assert errors == []
