"""
PIT-TZ-002 单元测试: 产品型号不能串入配置信息。
"""

from src.gates.data_quality import check_config_contamination


class TestConfigContamination:
    """PIT-TZ-002: 产品型号字段不能串入存储配置信息。"""

    def test_clean_records_pass(self, sample_contract_records):
        """干净数据 → 无违规。"""
        violations = check_config_contamination(sample_contract_records)
        assert violations == [], f"发现违规: {violations}"

    def test_config_value_detected(self, sample_bad_records):
        """12+256 应被检测到。"""
        violations = check_config_contamination(sample_bad_records)
        assert any("12+256" in v for v in violations), f"未检测到配置串入: {violations}"

    def test_numeric_only_model_detected(self):
        """纯数字+符号的产品型号应被检测。"""
        records = [{"合同编号": "X1", "产品型号": "8+128-256", "对方公司": "某公司"}]
        violations = check_config_contamination(records)
        assert len(violations) > 0

    def test_normal_product_name_passes(self):
        """正常产品名不误报。"""
        records = [{"合同编号": "X1", "产品型号": "iPhone 15 Pro Max", "对方公司": "Apple"}]
        violations = check_config_contamination(records)
        assert violations == []
