# app/core/exceptions.py - 全局异常处理器
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas import BaseResponse


async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 异常统一返回 BaseResponse 格式"""
    return JSONResponse(
        status_code=exc.status_code,
        content=BaseResponse(
            code=exc.status_code,
            msg=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            data=None
        ).model_dump()
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """请求验证异常统一返回 BaseResponse 格式"""
    return JSONResponse(
        status_code=422,
        content=BaseResponse(
            code=422,
            msg="请求参数验证失败",
            data=exc.errors()
        ).model_dump()
    )


async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    return JSONResponse(
        status_code=500,
        content=BaseResponse(
            code=500,
            msg="服务器内部错误",
            data=None
        ).model_dump()
    )
