# DTLE 双轨排版引擎 —— 开发/当前环境镜像
# 后端：Flask HTTP 服务 + Playwright(Chromium) B 轨 PNG/视觉回归
# 构建：docker build -t dtle-dev -f wechat_design/dtle/Dockerfile .
# 运行：docker run -p 8787:8787 dtle-dev
FROM python:3.13-slim

WORKDIR /app

# 仅复制引擎与既有校验脚本（校验门复用 wechat_design/scripts/validate_gzh_html.py）
COPY wechat_design/ /app/wechat_design/

# 安装 Flask + Playwright + Chromium（--with-deps 拉取系统库；无 apt 时去掉）
RUN pip install --no-cache-dir pyyaml flask playwright \
 && (playwright install --with-deps chromium || playwright install chromium)

EXPOSE 8787

# cli.py 会自动把 /app 加入 sys.path，故可解析 wechat_design.dtle 包
# DTLE_BTRACK_BACKEND 缺省为 dev（B 轨 PNG 走 Playwright）
CMD ["python", "wechat_design/dtle/cli.py", "serve", "--host", "0.0.0.0", "--port", "8787", "--server", "flask"]
