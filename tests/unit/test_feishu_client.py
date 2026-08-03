"""
feishu_client.py 单元测试 — normalize和_extract_text逻辑。
不调真实API（测纯逻辑层）。
"""
from src.feishu_client import FeishuClient, _extract_text


class TestExtractText:
    """_extract_text 飞书字段值提取。"""

    def test_none_returns_empty(self):
        assert _extract_text(None) == ""

    def test_string_passthrough(self):
        assert _extract_text("hello") == "hello"

    def test_int_passthrough(self):
        assert _extract_text(42) == "42"

    def test_list_of_dicts(self):
        """飞书富文本格式: [{"text": "内容"}]。"""
        val = [{"text": "hello"}, {"text": "world"}]
        assert _extract_text(val) == "hello world"

    def test_list_of_dicts_with_name(self):
        """人员格式: [{"name": "张三"}]。"""
        val = [{"name": "张三"}, {"name": "李四"}]
        assert _extract_text(val) == "张三 李四"

    def test_list_of_strings(self):
        assert _extract_text(["a", "b"]) == "a b"

    def test_dict_with_text(self):
        assert _extract_text({"text": "value"}) == "value"

    def test_dict_with_name(self):
        assert _extract_text({"name": "标签"}) == "标签"

    def test_dict_without_text_or_name(self):
        """字典没有text/name字段 → 空字符串。"""
        assert _extract_text({"foo": "bar"}) == ""


class TestNormalize:
    """FeishuClient.normalize 记录规范化。"""

    def test_empty_list(self):
        assert FeishuClient.normalize([]) == []

    def test_simple_record(self):
        """简单记录规范化。"""
        raw = [{"record_id": "rec1", "fields": {"合同编号": [{"text": "HT-001"}]}}]
        result = FeishuClient.normalize(raw)
        assert len(result) == 1
        assert result[0]["_id"] == "rec1"
        assert result[0]["合同编号"] == "HT-001"

    def test_null_fields_safe(self):
        """PIT-TZ-008: fields值为None不崩溃。"""
        raw = [{"record_id": "rec2", "fields": {"备注": None}}]
        result = FeishuClient.normalize(raw)
        assert result[0]["备注"] == ""

    def test_mixed_types(self):
        """混合类型字段。"""
        raw = [{
            "record_id": "rec3",
            "fields": {
                "名称": "测试合同",
                "金额": 50000,
                "标签": [{"name": "VIP"}],
                "备注": None,
            }
        }]
        result = FeishuClient.normalize(raw)
        assert result[0]["名称"] == "测试合同"
        assert result[0]["金额"] == "50000"
        assert result[0]["标签"] == "VIP"
        assert result[0]["备注"] == ""

    def test_missing_record_id(self):
        """缺record_id → 空字符串。"""
        raw = [{"fields": {"x": "y"}}]
        result = FeishuClient.normalize(raw)
        assert result[0]["_id"] == ""

    def test_missing_fields(self):
        """缺fields字段 → 只有_id。"""
        raw = [{"record_id": "rec4"}]
        result = FeishuClient.normalize(raw)
        assert result[0]["_id"] == "rec4"
