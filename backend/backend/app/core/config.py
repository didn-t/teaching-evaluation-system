import os
from pathlib import Path

from dotenv import load_dotenv

print("正在加载环境变量...")

project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
# 22300417陈俫坤开发：让 .env 覆盖系统环境变量，避免“注册/初始化写入不同库”
load_dotenv(dotenv_path=env_path, encoding='utf-8', override=True)

MYSQL_USER = os.getenv("MYSQL_USER")

MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")
APP_ENV = os.getenv("APP_ENV")

# 如果使用 docker 运行，则使用 docker 中的数据库
if APP_ENV == "docker":
    MYSQL_HOST = os.getenv("MYSQL_HOST_DOCKER", "db")
else:
    MYSQL_HOST = os.getenv("MYSQL_HOST_LOCAL", "127.0.0.1")

print("APP_ENV =", APP_ENV)


# JWT 配置
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

# 应用配置
APP_NAME = os.getenv("APP_NAME") or "Teaching Evaluation System API"
APP_VERSION = os.getenv("APP_VERSION") or "0.1.0"
DEBUG = os.getenv("DEBUG")
