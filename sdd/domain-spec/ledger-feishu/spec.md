---
spec_id: "SPEC-LE-003"
title: "ledger-feishu 模块规格"
module: "ledger-feishu"
level: "A"
status: "confirmed"
owner: "@dachui80"
version: "0.2.0"
generated_by: "SpecGuard ReverseEngine"
confirmed_at: "2026-08-12"
---

# ledger-feishu 模块规格（confirmed）

## Confirmed Facts

### 入口
- 主类：`class FeishuClient`（在 `src/feishu_client.py`）
- 辅助函数：`def _extract_text(v: Any) -> str`（提取文本，处理多类型输入）

### 消费者
- `src/api.py` 的 `GET /quality/check` 在门禁失败时调用 `FeishuClient` 推送告警
- `src/monitors/` 监控模块异常通知
- `src/sentry_health.py` 健康探针告警

### 配置
- 通过 `src/config.py` 读取飞书 Webhook/App 凭证
- `.env.dev`/`.env.staging`/`.env.prod` 三套环境配置

## Inferred Rules
- `FeishuClient` 封装了飞书开放平台的消息/卡片发送
- `_extract_text` 统一处理 dict/str/None 输入，避免下游崩溃
- 告警文案与质量门禁结果联动（错误级别+表名+问题摘要）

## To Clarify
- 支持的消息类型（文本/富文本/卡片/交互）
- 重试/退避策略
- 飞书签名/验签实现
- 与飞书机器人（bot）集成的差异
