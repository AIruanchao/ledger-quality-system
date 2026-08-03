.PHONY: help install dev lint test test-unit test-e2e test-all coverage docker-build docker-run docker-test backup health clean

help: ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	pip install pydantic httpx pytest pytest-cov ruff

dev: install ## 开发环境一键安装
	@echo "✅ 开发环境就绪"

lint: ## Lint检查
	ruff check src/ tests/

lint-fix: ## 自动修复lint问题
	ruff check --fix src/ tests/

test: test-unit ## 运行测试（默认unit）

test-unit: ## 单元测试
	pytest tests/unit/ -v --tb=short

test-e2e: ## E2E测试（需要网络+飞书密钥）
	pytest tests/e2e/ -v -m "not slow" --tb=short

test-all: ## 全量测试+覆盖率
	pytest tests/unit/ tests/e2e/ -v -m "not slow" --tb=short --cov=src --cov-report=term-missing --cov-fail-under=80

coverage: ## 生成覆盖率报告
	pytest tests/unit/ --cov=src --cov-report=html --cov-fail-under=80
	@echo "📊 覆盖率报告: htmlcov/index.html"

docker-build: ## 构建Docker镜像
	docker build -t ledger-quality-system:latest .

docker-run: ## 运行Docker容器
	docker run --rm --env-file .env ledger-quality-system:latest

docker-test: ## Docker内运行测试
	docker compose --profile test up --abort-on-container-exit

backup: ## 执行备份
	bash scripts/backup_daily.sh

health: ## 健康检查
	python3 -c "from src.monitors import HealthChecker; import json; print(json.dumps(HealthChecker().check_all(), indent=2, ensure_ascii=False))"

clean: ## 清理缓存
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
	@echo "✅ 清理完成"
