"""
PIT-TZ-006 单元测试: 垃圾数据膨胀检测。
"""
from src.gates.data_quality import check_garbage_threshold


class TestGarbageThreshold:
    """PIT-TZ-006: 飞书条数 ≤ 源系统条数×2。"""

    def test_normal_count_passes(self):
        """80条飞书 vs 80条源 → PASS。"""
        assert check_garbage_threshold(80, 80)

    def test_double_passes(self):
        """160条飞书 vs 80条源 → 刚好2倍 → PASS。"""
        assert check_garbage_threshold(160, 80)

    def test_excessive_detected(self):
        """15000条飞书 vs 80条源 → 超标 → FAIL。"""
        assert not check_garbage_threshold(15000, 80)

    def test_minimum_threshold(self):
        """小数据量有最低阈值。"""
        assert check_garbage_threshold(5, 1)
        assert not check_garbage_threshold(25, 1)
