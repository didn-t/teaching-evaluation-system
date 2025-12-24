from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn
from fastapi import Depends
from sqlalchemy.orm import Session



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
    return {"message": "Welcome to Teaching Evaluation System API", "version": os.getenv('APP_VERSION', '1.0.0')}


# 导入路由
from app.api.v1.teaching_eval import user as teaching_eval_user
from app.api.v1.teaching_eval import eval as teaching_eval_api

app.include_router(teaching_eval_user.router, prefix="/api/v1/teaching-eval/user", tags=["用户认证"])
app.include_router(teaching_eval_api.router, prefix="/api/v1/teaching-eval/eval", tags=["教学评价"])


# 健康检查接口
@app.get("/health")
def health_check():
    return {"status": "healthy"}


from app.database import get_db
@app.get("/health/db")
def database_health_check(db: Session = Depends(get_db)):
    """
    简单的数据库连接检查
    """
    try:
        # 执行简单查询测试连接
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception:
        return {"status": "unhealthy", "database": "disconnected"}, 503


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=os.getenv('DEBUG', 'True').lower() == 'true')
