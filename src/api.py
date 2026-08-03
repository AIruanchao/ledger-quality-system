"""
台账系统 REST API — FastAPI with OpenAPI/Swagger自动文档。

运行:
    uvicorn src.api:app --reload --port 8000
Swagger文档:
    http://localhost:8000/docs
ReDoc:
    http://localhost:8000/redoc
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from .config import TABLES
from .feishu_client import FeishuClient
from .monitors import HealthChecker

app = FastAPI(
    title="台账系统质量保障API",
    description="""
    台账系统统一查询/健康检查/数据质量门禁接口。

    ## 功能
    * **台账查询**: 合同/订单/回款/采购等8张表
    * **健康检查**: 飞书/ERP/HT/DB 四组件探活
    * **数据质量**: PIT-TZ坑点门禁检查
    """,
    version="1.0.0",
    contact={"name": "大锤80", "url": "https://github.com/AIruanchao/ledger-quality-system"},
    license_info={"name": "MIT"},
)

feishu = FeishuClient()


# ==================== 数据模型 ====================

class HealthResponse(BaseModel):
    status: str
    components: dict[str, dict[str, Any]]
    timestamp: str


class TableSummary(BaseModel):
    table: str
    name: str
    count: int


class RecordList(BaseModel):
    table: str
    total: int
    records: list[dict[str, str]]


# ==================== 接口 ====================

@app.get("/", tags=["meta"])
async def root():
    """API根信息。"""
    return {"service": "台账系统质量保障API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", response_model=HealthResponse, tags=["监控"])
async def health():
    """系统健康检查 — 四组件探活。"""
    checker = HealthChecker()
    results = checker.check_all()
    all_ok = all(v["status"] == "ok" for v in results.values())
    return HealthResponse(
        status="healthy" if all_ok else "degraded",
        components=results,
        timestamp=datetime.now().isoformat(),
    )


@app.get("/tables", response_model=list[TableSummary], tags=["台账"])
async def list_tables():
    """列出所有台账表及记录数。"""
    summaries = []
    for key, (table_id, table_name) in TABLES.items():
        count = feishu.count_records(table_id)
        summaries.append(TableSummary(table=key, name=table_name, count=count))
    return summaries


@app.get("/tables/{table_key}", response_model=RecordList, tags=["台账"])
async def get_records(
    table_key: str,
    limit: int = Query(default=20, ge=1, le=500, description="返回条数上限"),
):
    """
    查询台账记录。

    - **contracts**: 合同台账
    - **orders**: 订单台账
    - **payments**: 回款单
    - **purchases**: 采购台账
    """
    if table_key not in TABLES:
        raise HTTPException(status_code=404, detail=f"表 '{table_key}' 不存在，可选: {list(TABLES.keys())}")
    table_id, table_name = TABLES[table_key]
    raw = feishu.fetch_records(table_id)
    records = FeishuClient.normalize(raw[:limit])
    return RecordList(table=table_key, total=len(records), records=records)


@app.get("/quality/check", tags=["质量门禁"])
async def quality_check():
    """
    运行数据质量门禁检查 (PIT-TZ-002/003/004)。
    返回各项检查结果和总体PASS/FAIL。
    """
    from .gates.data_quality import (
        check_amount_logic,
        check_config_contamination,
        check_null_rate,
    )

    table_id = TABLES["contracts"][0]
    raw = feishu.fetch_records(table_id)
    records = FeishuClient.normalize(raw)

    config_violations = check_config_contamination(records)
    amount_errors = check_amount_logic(records)

    null_checks = {}
    for field in ["合同编号", "对方公司", "合同金额"]:
        ok, rate = check_null_rate(records, field)
        null_checks[field] = {"pass": ok, "null_rate": f"{rate:.1%}"}

    all_pass = not config_violations and not amount_errors and all(v["pass"] for v in null_checks.values())

    return {
        "overall": "PASS" if all_pass else "FAIL",
        "checks": {
            "PIT-TZ-002_config_contamination": {"pass": not config_violations, "violations": config_violations[:5]},
            "PIT-TZ-004_amount_logic": {"pass": not amount_errors, "errors": amount_errors[:5]},
            "PIT-TZ-003_null_rates": null_checks,
        },
    }
