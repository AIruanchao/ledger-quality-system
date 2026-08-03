## PR描述模板

### 变更类型
- [ ] feat: 新功能
- [ ] fix: Bug修复
- [ ] refactor: 重构
- [ ] test: 测试
- [ ] docs: 文档
- [ ] ci: CI/CD
- [ ] chore: 其他

### 变更内容
<!-- 简要描述做了什么 -->

### 关联PIT
<!-- PIT-TZ-XXX 或 "无关联" -->

### 测试
- [ ] `ruff check src/ tests/` 通过
- [ ] `pytest tests/unit/ -q` 通过
- [ ] 覆盖率≥80%

### Checklist
- [ ] 无明文密钥
- [ ] 无console.log/print调试代码
- [ ] 文档已更新（如需要）
