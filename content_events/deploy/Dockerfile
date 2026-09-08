# 内容事件编排 REST 服务镜像
# 仅打包运行 serve.py 所需的 Python 源码与最小依赖；语料(publish_queue/)与落盘(data/)通过卷挂载。
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# 最小依赖（真实发布所需 redbook/wechat_design 依赖为 guarded import，dry_run 不触发）
COPY deploy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 源码包（按 .dockerignore 排除重数据）
COPY content_events/ ./content_events/
COPY redbook/ ./redbook/
COPY wechat_design/ ./wechat_design/
COPY skills/ ./skills/
COPY config/ ./config/

# 运行时入口
EXPOSE 8080
CMD ["sh", "-c", "python -m uvicorn content_events.serve:app --host 0.0.0.0 --port ${PORT}"]
