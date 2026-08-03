"""
PIT-TZ-008 单元测试: 空表 NoneType 安全。
"""
from src.gates.data_quality import check_null_safety


class TestNullSafety:
    """PIT-TZ-008: 空表 items=None 不应崩溃。"""

    def test_none_returns_empty_list(self):
        """None → 空列表。"""
        result = check_null_safety(None)
        assert result == []

    def test_empty_list_returns_empty(self):
        """空列表 → 空列表。"""
        result = check_null_safety([])
        assert result == []

    def test_non_empty_returns_as_is(self):
        """有数据 → 原样返回。"""
        data = [{"id": 1}]
        result = check_null_safety(data)
        assert result == data

    def test_iteration_over_none_safe(self):
        """对 check_null_safety(None) 的结果迭代不崩溃。"""
        result = check_null_safety(None)
        for item in result:  # 不应 TypeError
            pass
