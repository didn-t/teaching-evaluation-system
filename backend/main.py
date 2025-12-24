from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
import uvicorn
from app.database import create_tables
import asyncio

# 加载环境变量
load_dotenv()



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


# 根路由
@app.get("/")
async def read_root():
    # 启动时自动创建数据库表
    await create_tables()
    return {"message": "Welcome to Teaching Evaluation System API", "version": os.getenv('APP_VERSION', '1.0.0')}

@app.on_event("startup")
async def startup_event():
    # 应用启动时自动创建数据库表
    await create_tables()

# 健康检查路由
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# 导入路由
from app.api import auth, evaluation

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["评教"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=os.getenv('DEBUG', 'True').lower() == 'true')