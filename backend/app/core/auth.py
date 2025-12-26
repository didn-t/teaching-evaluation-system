# 用于验证token，角色权限验证
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
import bcrypt
from jose import jwt, JWTError

from app.schemas import Token,TokenData


def hash_password(password: str) -> str:
    # 密码需要编码为 bytes，且不能超过 72 字节
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(token_data: TokenData, expires_delta: timedelta | None = None) -> Token:
    """
    创建访问令牌
    :param token_data:
    :param expires_delta:
    :return:Token(pydantic)
    """
    to_encode = token_data.model_dump().copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES) or 30))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    print("SECRET_KEY", SECRET_KEY)
    print("ALGORITHM", ALGORITHM)

    return Token(
        access_token=encoded_jwt,
        expire_time=expire,
    )

def verify_token(token: Token) -> Optional[TokenData]:
    """
    验证token
    :param token:
    :return:成功返回payload，失败返回None
    """
    try:
        payload = jwt.decode(token.access_token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)
        return token_data
    except JWTError :
        print("token验证失败")
        return None
