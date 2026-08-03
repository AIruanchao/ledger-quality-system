"""
feishu_client.py 网络层测试 — 用mock测fetch/count/get_fields。
"""
import json
from unittest.mock import MagicMock, patch

from src.feishu_client import FeishuClient


class TestFeishuClientNetwork:
    """FeishuClient网络方法mock测试。"""

    def _mock_client(self):
        """创建带mock token的客户端。"""
        client = FeishuClient("test_app_id", "test_secret")
        client._token = "mock_token"
        client._token_expiry = 9999999999
        return client

    @patch("src.feishu_client.urllib.request.urlopen")
    def test_fetch_records_success(self, mock_urlopen):
        """fetch_records 正常分页拉取。"""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "code": 0,
            "data": {"items": [{"record_id": "r1", "fields": {"x": "y"}}], "has_more": False}
        }).encode()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = self._mock_client()
        records = client.fetch_records("tbl123")
        assert len(records) == 1
        assert records[0]["record_id"] == "r1"

    @patch("src.feishu_client.urllib.request.urlopen")
    def test_fetch_records_empty_table(self, mock_urlopen):
        """PIT-TZ-008: 空表 items=None 不崩溃。"""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "code": 0,
            "data": {"items": None, "has_more": False}
        }).encode()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = self._mock_client()
        records = client.fetch_records("tbl123")
        assert records == []

    @patch("src.feishu_client.urllib.request.urlopen")
    def test_fetch_records_error_code(self, mock_urlopen):
        """飞书返回非0 code → 空列表。"""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"code": 9999, "msg": "error"}).encode()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = self._mock_client()
        records = client.fetch_records("tbl123")
        assert records == []

    @patch("src.feishu_client.urllib.request.urlopen")
    def test_count_records_success(self, mock_urlopen):
        """count_records 正常返回条数。"""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "data": {"total": 42}
        }).encode()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = self._mock_client()
        assert client.count_records("tbl123") == 42

    @patch("src.feishu_client.urllib.request.urlopen")
    def test_count_records_network_error(self, mock_urlopen):
        """count_records 网络错误 → 返回-1。"""
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("network error")
        client = self._mock_client()
        assert client.count_records("tbl123") == -1

    @patch("src.feishu_client.urllib.request.urlopen")
    def test_get_fields_success(self, mock_urlopen):
        """get_fields 正常返回字段列表。"""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "data": {"items": [{"field_name": "合同编号", "type": 1}]}
        }).encode()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = self._mock_client()
        fields = client.get_fields("tbl123")
        assert len(fields) == 1
        assert fields[0]["field_name"] == "合同编号"

    @patch("src.feishu_client.urllib.request.urlopen")
    def test_get_fields_empty(self, mock_urlopen):
        """get_fields 空表 → 空列表。"""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "data": {"items": None}
        }).encode()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = self._mock_client()
        assert client.get_fields("tbl123") == []

    @patch("src.feishu_client.urllib.request.urlopen")
    def test_get_token_cached(self, mock_urlopen):
        """token缓存：未过期不重新获取。"""
        client = FeishuClient("app_id", "secret")
        client._token = "cached_token"
        client._token_expiry = 9999999999
        # 不应调用urlopen
        token = client._get_token()
        assert token == "cached_token"
        mock_urlopen.assert_not_called()

    @patch("src.feishu_client.urllib.request.urlopen")
    def test_get_token_refresh(self, mock_urlopen):
        """token过期时重新获取。"""
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "code": 0,
            "tenant_access_token": "new_token"
        }).encode()
        mock_urlopen.return_value.__enter__ = MagicMock(return_value=mock_resp)
        mock_urlopen.return_value.__exit__ = MagicMock(return_value=False)

        client = FeishuClient("app_id", "secret")
        client._token = ""
        client._token_expiry = 0
        token = client._get_token()
        assert token == "new_token"
