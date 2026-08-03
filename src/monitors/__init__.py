"""
分组件健康检查 — 监控台账系统各服务可用性。
"""
from __future__ import annotations

import subprocess
import urllib.error
import urllib.request
from typing import Any

from ..config import ERP_URL, FEISHU_BASE, HT_SSH_HOST, HT_URL


class HealthChecker:
    """台账系统健康检查器。"""

    def check_all(self) -> dict[str, dict[str, Any]]:
        """检查所有组件，返回 {component: {status, detail}}。"""
        return {
            "feishu": self._check_feishu(),
            "erp": self._check_erp(),
            "ht": self._check_ht(),
            "ht_db": self._check_ht_db(),
        }

    def _check_feishu(self) -> dict[str, Any]:
        """检查飞书API可达性。"""
        try:
            url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{FEISHU_BASE}"
            req = urllib.request.Request(url, headers={"Authorization": "Bearer check"})
            urllib.request.urlopen(req, timeout=10)
            return {"status": "ok", "detail": "reachable"}
        except urllib.error.HTTPError as e:
            # 401 = API可达但token无效（对于健康检查来说API本身是通的）
            return {"status": "ok", "detail": f"reachable (http {e.code})"}
        except Exception as e:
            return {"status": "down", "detail": str(e)[:100]}

    def _check_erp(self) -> dict[str, Any]:
        """检查ERP API可达性。"""
        try:
            url = f"{ERP_URL}/api/external/products"
            req = urllib.request.Request(url)
            urllib.request.urlopen(req, timeout=10)
            return {"status": "ok", "detail": "reachable"}
        except urllib.error.HTTPError as e:
            return {"status": "ok", "detail": f"reachable (http {e.code})"}
        except Exception as e:
            return {"status": "down", "detail": str(e)[:100]}

    def _check_ht(self) -> dict[str, Any]:
        """检查HT商务系统可达性。"""
        try:
            url = f"{HT_URL}/health"
            req = urllib.request.Request(url)
            urllib.request.urlopen(req, timeout=10)
            return {"status": "ok", "detail": "reachable"}
        except urllib.error.HTTPError as e:
            return {"status": "ok", "detail": f"reachable (http {e.code})"}
        except Exception as e:
            return {"status": "down", "detail": str(e)[:100]}

    def _check_ht_db(self) -> dict[str, Any]:
        """检查HT Postgres DB可达性。"""
        try:
            r = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", HT_SSH_HOST,
                 'PGPASSWORD=erp_doc psql -U erp_doc -d erp_doc -t -A -c "SELECT 1"'],
                capture_output=True, text=True, timeout=10,
            )
            if r.stdout.strip() == "1":
                return {"status": "ok", "detail": "queryable"}
            return {"status": "down", "detail": f"unexpected output: {r.stdout[:50]}"}
        except (subprocess.TimeoutExpired, OSError) as e:
            return {"status": "down", "detail": str(e)[:100]}

    def summary(self) -> dict[str, str]:
        """返回简要状态摘要。"""
        results = self.check_all()
        return {k: v["status"] for k, v in results.items()}
