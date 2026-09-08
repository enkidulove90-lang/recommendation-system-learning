# novelty 创新性分析引擎 — 服务镜像
# 基于 design docs §7 运维设计：SPECTER2 经 transformers 本地推理；GROBID 另起容器常驻。
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 系统依赖（sentence-transformers / faiss 需要基础编译与网络库）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && rm -rf /var/lib/apt/lists/*

# 先装依赖（利用层缓存）
COPY requirements.txt requirements-novelty.txt ./
RUN pip install -r requirements.txt && pip install -r requirements-novelty.txt

# 复制代码（data/ 通过 volume 挂载，不进镜像）
COPY . .

# 服务端口
EXPOSE 8000

HEALTHCHECK --interval=60s --timeout=10s --retries=3 \
    CMD curl -fsS http://localhost:8000/health || exit 1

CMD ["sh", "-c", "uvicorn novelty.serve:app --host 0.0.0.0 --port 8000"]
