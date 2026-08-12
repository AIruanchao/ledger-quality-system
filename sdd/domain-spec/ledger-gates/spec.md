---
spec_id: "SPEC-LE-002"
title: "ledger-gates 模块规格"
module: "ledger-gates"
level: "A"
status: "confirmed"
owner: "@dachui80"
version: "0.2.0"
generated_by: "SpecGuard ReverseEngine"
confirmed_at: "2026-08-12"
---

# ledger-gates 模块规格（confirmed）

## Confirmed Facts

### 目录
- `src/gates/__init__.py`：包入口
- `src/gates/data_quality.py`：数据质量门禁实现

### 与 api 联动
- `src/api.py` 暴露 `GET /quality/check` 路由，调用 `src/gates/data_quality.py` 内的检查逻辑
- tags 标记为 `["质量门禁"]`

### 与飞书联动
- 门禁触发后通过 `src/feishu_client.py` 发送告警（消费 `FeishuClient`）

### 监控链路
- `src/monitors/`：持续监控模块，定期调用门禁
- `src/sentry_health.py`：Sentry 健康上报

## Inferred Rules
- 门禁检查是只读操作，不修改台账数据
- 失败门禁应触发飞书告警而非直接阻塞（除非被 CLI 显式调用）
- `data_quality.py` 是单文件实现，便于审计

## To Clarify
- `data_quality.py` 的具体检查项（空值/重复/范围/外键）
- 门禁严重等级（warn/error/critical）与告警通道映射
- 是否支持自定义规则注入
- 与 `src/validators/` 的职责边界
