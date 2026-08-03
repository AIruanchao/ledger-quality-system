# 变更日志

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范。

## [Unreleased]

### Added
- 7个Gap全部补齐（E2E/CD/监控/备份/类型检查/依赖安全/覆盖率消水）

## [1.0.0] — 2026-08-03

### Added
- Git仓库 + 标准Python包结构 (src/tests/.github)
- pytest 69/69 PASSED + 覆盖率93.98%
- ruff lint 0 errors
- GitHub Actions CI (lint+test+cov+pyright+pip-audit)
- 10个PIT-TZ坑点 → pytest unit tests
- Pydantic数据契约 (ContractRecord/PaymentRecord)
- 密钥外置 (fail-closed, 消除明文APP_SECRET)
- E2E测试 (飞书+HT+ERP真实数据验证)
- CD deploy.yml (staging→prod→rollback)
- 监控告警 (health.py + alert.py)
- 备份恢复 (backup_daily.sh NDJSON+gzip+30天保留)
- 分支保护 (main protected + PR≥1 + CI必绿)
- 需求追溯矩阵 (10 PIT-TZ → test映射 + RACI)
- Dependabot 自动依赖更新
- CODEOWNERS + PR模板
