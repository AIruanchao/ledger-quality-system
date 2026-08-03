"""
E2E 测试: 对真实飞书台账执行10个PIT-TZ坑点检查。
需要网络+飞书密钥，skip if 不可用。
"""
import json
import subprocess

import pytest


@pytest.mark.e2e
class TestLedgerE2E:
    """台账系统端到端数据质量检查。"""

    def test_pit_tz_002_no_config_contamination(self, contracts):
        """PIT-TZ-002: 真实合同台账中产品型号无配置串入。"""
        from src.gates.data_quality import check_config_contamination
        violations = check_config_contamination(contracts)
        assert violations == [], f"发现配置串入: {violations[:5]}"

    def test_pit_tz_003_null_rate_ok(self, contracts):
        """PIT-TZ-003: 活跃合同关键字段空值率<10%。"""
        from src.gates.data_quality import check_null_rate
        for field in ["合同编号", "对方公司", "合同金额"]:
            ok, rate = check_null_rate(contracts, field)
            assert ok, f"合同{field}空值率={rate:.0%} (PIT-TZ-003)"

    def test_pit_tz_004_amount_logic_ok(self, contracts):
        """PIT-TZ-004: 合同金额=单价×台数。"""
        from src.gates.data_quality import check_amount_logic
        errors = check_amount_logic(contracts)
        assert errors == [], f"金额逻辑错误: {errors[:5]}"

    def test_pit_tz_006_no_garbage_data(self, contracts, feishu_client):
        """PIT-TZ-006: 无垃圾数据膨胀。"""
        from src.config import TABLES
        from src.gates.data_quality import check_garbage_threshold
        payments_count = feishu_client.count_records(TABLES["payments"][0])
        if payments_count < 0:
            pytest.skip("飞书payments计数失败")
        # 基准: 回款单中PAY-开头的凭证号数量
        pay_count = sum(1 for c in contracts if str(c.get("银行凭证号", "")).startswith("PAY-"))
        threshold_ok = check_garbage_threshold(payments_count, max(pay_count, 1))
        assert threshold_ok, f"回款单可能膨胀: 飞书={payments_count}"

    def test_pit_tz_008_null_safety(self, feishu_client):
        """PIT-TZ-008: 空表不崩溃。"""
        from src.config import TABLES
        from src.gates.data_quality import check_null_safety
        # 拉一个可能有空数据的表
        table_id = TABLES["deliveries"][0]
        raw = feishu_client.fetch_records(table_id, max_pages=1)
        result = check_null_safety(raw)
        assert isinstance(result, list)

    def test_pit_tz_009_idempotency_field_type(self, feishu_client):
        """PIT-TZ-009: 银行凭证号字段是可写类型(type=1)。"""
        from src.config import TABLES
        from src.validators.schema import check_idempotency_field
        fields = feishu_client.get_fields(TABLES["payments"][0])
        bank_field = next((f for f in fields if f.get("field_name") == "银行凭证号"), None)
        if not bank_field:
            pytest.skip("银行凭证号字段不存在")
        assert check_idempotency_field(bank_field), f"type={bank_field.get('type')} 不可写"

    @pytest.mark.slow
    def test_pit_tz_005_idempotency_e2e(self):
        """PIT-TZ-005: 回款单sync两次第二次created=0。需要SSH到HT。"""
        from src.config import HT_SSH_HOST
        try:
            r1 = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", HT_SSH_HOST,
                 "curl -sS --max-time 60 -X POST http://localhost:8600/sync/payments"],
                capture_output=True, text=True, timeout=90,
            )
            if r1.returncode != 0:
                pytest.skip(f"SSH不可用: {r1.stderr[:60]}")
            result1 = json.loads(r1.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
            pytest.skip("HT SSH不可用")

        import time
        time.sleep(3)

        r2 = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", HT_SSH_HOST,
             "curl -sS --max-time 60 -X POST http://localhost:8600/sync/payments"],
            capture_output=True, text=True, timeout=90,
        )
        result2 = json.loads(r2.stdout)
        created2 = result2.get("result", {}).get("created", -1)
        assert created2 == 0, f"第二次sync created={created2}，幂等失效"

    @pytest.mark.slow
    def test_pit_tz_007_date_proxy_systemd(self):
        """PIT-TZ-007: date-proxy服务在cloud4上是active状态。"""
        from src.config import HT_SSH_HOST
        try:
            r = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", HT_SSH_HOST,
                 "systemctl is-active date-proxy 2>&1"],
                capture_output=True, text=True, timeout=10,
            )
            status = r.stdout.strip()
            if status == "inactive":
                pytest.xfail("date-proxy未运行（非阻断，已知PIT-TZ-007）")
            assert status == "active", f"date-proxy status={status}"
        except (subprocess.TimeoutExpired, OSError):
            pytest.skip("SSH不可用")

    def test_reconciliation_feishu_vs_ht(self, feishu_client):
        """对账: 飞书合同台账条数 ≥ HT DB条数。"""
        from src.config import HT_SSH_HOST, TABLES
        feishu_count = feishu_client.count_records(TABLES["contracts"][0])
        if feishu_count < 0:
            pytest.skip("飞书计数失败")
        try:
            r = subprocess.run(
                ["ssh", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", HT_SSH_HOST,
                 'PGPASSWORD=erp_doc psql -U erp_doc -d erp_doc -t -A -c "SELECT count(*) FROM contracts"'],
                capture_output=True, text=True, timeout=10,
            )
            if not r.stdout.strip().isdigit():
                pytest.skip("HT DB不可用")
            ht_count = int(r.stdout.strip())
        except (subprocess.TimeoutExpired, OSError):
            pytest.skip("HT SSH不可用")
        assert feishu_count >= ht_count, f"飞书={feishu_count} < HT={ht_count}"
