from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
import uvicorn

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = f"mysql+asyncmy://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"

# 创建异步引擎
engine = create_async_engine(DATABASE_URL)

# 创建异步会话工厂
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 创建基础模型类
Base = declarative_base()

# 初始化 FastAPI 应用
app = FastAPI(
    title=os.getenv('APP_NAME', 'Teaching Evaluation System'),
    version=os.getenv('APP_VERSION', '1.0.0'),
    description="南宁理工学院听课评教系统 API",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖项：获取数据库会话
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 根路由
@app.get("/")
def read_root():
    return {"message": "Welcome to Teaching Evaluation System API", "version": os.getenv('APP_VERSION', '1.0.0')}

# 健康检查路由
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 导入路由
from app.api import  auth

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=os.getenv('DEBUG', 'True').lower() == 'true')