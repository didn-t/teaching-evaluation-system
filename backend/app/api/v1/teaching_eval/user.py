from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import false
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

from app.models import User
from app.schemas import Token, TokenData, UserNewCreate as UserCreate, UserNewResponse as UserResponse

# 加载环境变量
load_dotenv()

router = APIRouter()


# 用户登录
@router.post("/login", response_model=Token)
async def login():
    return {
        "code": 200,
        "msg": "登录成功",
        "data": {},
        "timestamp": datetime.now().timestamp(),
    }


@router.get("/login")
async def login():
    return {"status": "ok"}
