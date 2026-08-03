# 需求可追溯矩阵 (Requirements Traceability Matrix)

> PIT-TZ坑点 → pytest测试 → Git版本 三向映射

## 追溯链

| 需求ID | 根因描述 | 测试文件 | 测试类型 | Git Tag |
|--------|----------|----------|----------|---------|
| PIT-TZ-001 | 日期格式化失效（显示毫秒时间戳） | tests/unit/test_pit_tz_001_dates.py | unit | v1.0.0 |
| PIT-TZ-002 | 产品型号字段串入存储配置信息 | tests/unit/test_pit_tz_002_config.py | unit | v1.0.0 |
| PIT-TZ-003 | 草稿合同空值被计入空值率误报 | tests/unit/test_pit_tz_003_nullcheck.py | unit | v1.0.0 |
| PIT-TZ-004 | 金额≠单价×台数（含空产品行） | tests/unit/test_pit_tz_004_amount.py | unit | v1.0.0 |
| PIT-TZ-005 | 回款单scheduler不幂等→数据膨胀 | tests/unit/test_pit_tz_005_idempotency.py | unit | v1.0.0 |
| PIT-TZ-006 | backfill垃圾数据→台账膨胀 | tests/unit/test_pit_tz_006_garbage.py | unit | v1.0.0 |
| PIT-TZ-007 | date-proxy崩溃后日期格式化失效 | tests/e2e/test_ledger_e2e.py | e2e | v1.0.0 |
| PIT-TZ-008 | feishu_client空表NoneType崩溃 | tests/unit/test_pit_tz_008_nullsafety.py | unit | v1.0.0 |
| PIT-TZ-009 | 飞书自动编号字段不可写→幂等key失效 | tests/unit/test_pit_tz_009_fieldtype.py | unit | v1.0.0 |
| PIT-TZ-010 | 合同状态变更后D4排除规则需同步 | tests/unit/test_pit_tz_010_status.py | unit | v1.0.0 |

## 缺陷生命周期

```
发现 → 登记PIT-TZ-XXX → 写pytest测试 → CI门禁拦截 → 修复 → CI全绿 → 关闭
```

| 状态 | 含义 |
|------|------|
| open | 新发现，未修复 |
| tested | 已有pytest测试覆盖 |
| closed | 修复+CI全绿 |

## 质量度量

| 指标 | 当前值 | 目标 |
|------|--------|------|
| 坑点总数 | 10 | — |
| 已覆盖测试 | 10/10 (100%) | 100% |
| pytest结果 | 40/40 PASSED | 0 FAIL |
| 覆盖率 | 96.15% | ≥80% |
| ruff errors | 0 | 0 |

## RACI责任矩阵

| 角色 | 需求 | 测试 | Review | 发布 | 缺陷 |
|------|------|------|--------|------|------|
| 超哥 | A(审批) | A | A | A(审批) | I(知情) |
| 大锤80 | R(执行) | R | R | R | R |
| coder | R | R | C(咨询) | I | R |
