# app/core/auth.py用于验证token，角色权限验证
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi.security import HTTPBearer

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
import bcrypt
from jose import jwt, JWTError

from app.schemas import Token, TokenData
from fastapi import HTTPException, status, Request

# 创建安全方案实例
security = HTTPBearer()


def hash_password(password: str) -> str:
    # 密码需要编码为 bytes，且不能超过 72 字节
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(token_data: TokenData, expires_delta: timedelta | None = None) -> Optional[Token]:
    """
    创建访问令牌
    :param token_data:
    :param expires_delta:
    :return:Token(pydantic)
    """
    try:
        to_encode = token_data.model_dump().copy()
        expire = datetime.now(timezone.utc) + (
                    expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES) or 30))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        print("创建token失败", e)
        return None
    return Token(
        token=encoded_jwt,
    )


def verify_token(request: Request) -> Optional[TokenData]:
    """
    验证token
    :param request: HTTP请求对象
    :return:成功返回payload，失败抛出异常
    """
    # 从Cookie获取token
    token = request.cookies.get("token")

    if not token:
        # 如果Cookie中没有token，尝试从Authorization头部获取
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)
        return token_data
    except JWTError:
        print("token验证失败")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
