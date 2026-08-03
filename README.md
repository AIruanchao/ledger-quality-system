# 台账系统质量保障工程 (Ledger Quality System)

> 将台账系统的质量保障从"散落的手写脚本"重建为"软件公司标准的工程化体系"。

## 快速开始

```bash
# 1. 安装依赖
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"  # 或 pip install pydantic httpx pytest pytest-cov ruff

# 2. 配置密钥
cp .env.example .env  # 填入真实值

# 3. 运行测试
pytest tests/unit/ -v          # 纯逻辑测试（无需网络）
pytest tests/ -v --cov=src     # 全量测试+覆盖率

# 4. Lint
ruff check src/ tests/
```

## 项目结构

```
src/
├── config.py          # 统一配置（fail-closed，密钥从环境变量读取）
├── feishu_client.py   # 飞书API客户端（分页+token管理）
├── validators/
│   └── schema.py      # Pydantic数据契约（合同/订单/回款）
├── gates/
│   └── data_quality.py # D2-D10数据质量门禁
└── monitors/
    └── health.py      # 分组件健康检查

tests/
├── unit/              # 纯逻辑测试（schema验证、金额计算、空值检测）
├── integration/       # API集成测试（飞书API、tz-cli）
└── e2e/               # 端到端测试（10个PIT-TZ坑点→pytest）
```

## 10个PIT-TZ坑点 → pytest测试映射

| PIT | 根因 | 测试文件 | 类型 |
|-----|------|----------|------|
| TZ-001 | 日期格式化失效 | test_pit_tz_001_dates.py | E2E |
| TZ-002 | 产品型号串入配置 | test_pit_tz_002_config.py | E2E |
| TZ-003 | 草稿空值误报 | test_pit_tz_003_nullcheck.py | E2E |
| TZ-004 | 金额≠单价×台数 | test_pit_tz_004_amount.py | unit+E2E |
| TZ-005 | 回款单不幂等 | test_pit_tz_005_idempotency.py | E2E |
| TZ-006 | 垃圾数据膨胀 | test_pit_tz_006_garbage.py | E2E |
| TZ-007 | date-proxy崩溃 | test_pit_tz_007_systemd.py | E2E |
| TZ-008 | 空表NoneType崩溃 | test_pit_tz_008_nullsafety.py | unit+E2E |
| TZ-009 | 幂等key不可写 | test_pit_tz_009_fieldtype.py | E2E |
| TZ-010 | 状态变更未同步 | test_pit_tz_010_status.py | E2E |

## CI/CD

GitHub Actions自动在PR和push时运行：
- ruff lint
- pytest（unit + integration）
- 覆盖率门禁 ≥80%

## 质量治理

- **需求追溯**: PIT-TZ-XXX → test_pit_tz_XXX → Git tag
- **缺陷管理**: 飞书操作日志表 + P0/P1/P2分级
- **准入标准**: PR CI全绿 + 覆盖率≥80%
- **准出标准**: 0 P0 + 0 P1 + 全量回归PASS
