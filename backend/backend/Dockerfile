FROM python:3.11.14-slim AS production

WORKDIR /app

# 环境变量（pip 源已配置，无需修改）
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TZ=Asia/Shanghai \
    PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 配置时区（无需 apt，纯命令实现）
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 复制依赖文件 + 安装 Python 依赖（仅 pip，无系统命令）
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 复制应用代码 + 创建日志目录
COPY . .
RUN mkdir -p logs


# 暴露端口 + 启动命令
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000"]
