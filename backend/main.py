from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.config import APP_NAME, APP_VERSION, DEBUG
import uvicorn
from fastapi import HTTPException

from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)

# 初始化 FastAPI 应用
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="南宁理工学院听课评教系统 API",
)


# 导入认证中间件
from app.middleware.auth_middleware import AuthMiddleware

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加认证中间件
app.add_middleware(AuthMiddleware)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# 根路由
@app.get("/")
async def read_root():
    return {"message": "Welcome to Teaching Evaluation System API", "version": APP_VERSION}


# 导入路由
from app.api.v1.teaching_eval import user as teaching_eval_user
from app.api.v1.teaching_eval import eval as teaching_eval_api
from app.api.v1.teaching_eval import org as teaching_eval_org
from app.api.v1.teaching_eval import auth as teaching_eval_auth
from app.api.v1.teaching_eval import config as teaching_eval_config

app.include_router(teaching_eval_user.router, prefix="/api/v1/teaching-eval/user")
app.include_router(teaching_eval_api.router, prefix="/api/v1/teaching-eval/eval")
app.include_router(teaching_eval_org.router, prefix="/api/v1/teaching-eval/org")
app.include_router(teaching_eval_auth.router, prefix="/api/v1/teaching-eval/auth")
app.include_router(teaching_eval_config.router, prefix="/api/v1/teaching-eval")


# 健康检查接口
@app.get("/health")
def health_check():
    return {"status": "healthy"}



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=DEBUG.lower() == 'true')