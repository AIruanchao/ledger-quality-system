---
spec_id: "SPEC-LE-001"
title: "ledger-api 模块规格"
module: "ledger-api"
level: "A"
status: "confirmed"
owner: "@dachui80"
version: "0.2.0"
generated_by: "SpecGuard ReverseEngine"
confirmed_at: "2026-08-12"
---

# ledger-api 模块规格（confirmed）

## Confirmed Facts

### 入口
- 入口文件：`src/api.py`（FastAPI 应用）

### 路由清单（实际 grep 命中）
- `GET /` — meta 标签
- `GET /health` — `response_model=HealthResponse`，tags=`["监控"]`
- `GET /tables` — `response_model=list[TableSummary]`，tags=`["台账"]`
- `GET /tables/{table_key}` — `response_model=RecordList`，tags=`["台账"]`
  - 处理器函数：`async def get_records(...)`
- `GET /quality/check` — tags=`["质量门禁"]`

### 响应模型
- `HealthResponse`：健康检查响应
- `TableSummary`：表摘要
- `RecordList`：记录列表
- 质量门禁响应模型未在 grep 中显式声明（推断为 dict/自定义模型）

### 模块结构
- `src/api.py`：FastAPI 入口
- `src/config.py`：配置加载
- `src/logger.py`：日志
- `src/sentry.py` / `src/sentry_health.py`：Sentry 集成与健康探针
- `src/feishu_client.py`：飞书客户端（被 quality/check 消费）
- `src/tz_cli.py`：CLI 工具
- `src/gates/data_quality.py`：质量门禁逻辑
- `src/monitors/`：监控
- `src/validators/`：校验器

## Inferred Rules
- `GET /tables/{table_key}` 通过路径参数动态分发到不同台账
- 质量门禁 `/quality/check` 与 `src/gates/data_quality.py` 强绑定
- 所有路由使用中文 tags 分组（meta/监控/台账/质量门禁）
- `async def` 处理器用于 IO 密集型查询

## To Clarify
- `/quality/check` 的请求参数与返回结构
- `/tables` 是否支持分页/筛选
- 鉴权策略（当前 grep 未发现 `Depends(...)` 鉴权依赖）
- `RecordList` 字段契约（columns/rows/metadata）
