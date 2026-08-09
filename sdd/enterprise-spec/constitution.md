# 台账质量系统 SDD宪法 v1.0

> 状态: Active
> 适用范围: /Users/maccc/Projects/ledger-quality-system

## 治理原则
| 原则 | 说明 |
|------|------|
| 存量渐进补规范 | 按A/B/C分级逐步补Spec |
| 增量强制SDD | 新增功能必须按SDD流程执行 |
| Agent只读Spec | AI Agent仅读取sdd/目录规范文件编码 |
## 特别约束
- 飞书token不入库
- 台账数据只读(禁止反写ERP)

## 分级
| 级别 | 模块 |
|------|------|
| A级 | ledger-api, ledger-gates, ledger-feishu |
| B级 | ledger-validators, ledger-monitors |
| C级 | ledger-cli |
