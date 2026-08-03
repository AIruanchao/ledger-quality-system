"""
PIT-TZ-001 单元测试: 日期格式化验证。
"""
from src.gates.data_quality import check_date_format


class TestDateFormat:
    """PIT-TZ-001: 日期应格式化为YYYY-MM-DD，不是毫秒时间戳。"""

    def test_valid_date_passes(self):
        assert check_date_format("2026-12-31")

    def test_valid_date_passes_2(self):
        assert check_date_format("2027-06-30")

    def test_timestamp_detected(self):
        """13位毫秒时间戳 → 格式不对。"""
        assert not check_date_format("1778601600000")

    def test_empty_date_fails(self):
        assert not check_date_format("")

    def test_none_fails(self):
        assert not check_date_format(None)  # type: ignore
