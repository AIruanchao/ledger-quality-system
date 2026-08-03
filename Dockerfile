FROM python:3.11-slim

LABEL maintainer="大锤80"
LABEL description="台账系统质量保障工程"

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc && \
    rm -rf /var/lib/apt/lists/*

# Python依赖（先装依赖利用Docker缓存）
COPY pyproject.toml .
RUN pip install --no-cache-dir pydantic httpx pytest pytest-cov ruff

# 源代码
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# 环境变量默认值
ENV TZ_FEISHU_BASE=changeme \
    TZ_FEISHU_APP_ID=changeme \
    TZ_FEISHU_SECRET=changeme

# 健康检查
HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD python3 -c "from src.monitors import HealthChecker; h=HealthChecker(); exit(0 if all(v['status']=='ok' for v in h.check_all().values()) else 1)"

# 默认运行测试
CMD ["pytest", "tests/unit/", "-q", "--cov=src", "--cov-fail-under=80"]
