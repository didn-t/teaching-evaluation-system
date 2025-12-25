from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from typing import Optional

from app.models import User


async def get_user_by_user_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """根据用户编号获取用户"""
    result = await db.execute(select(User).where(User.user_id == user_id))
    try:
        return result.scalar_one_or_none()
    except NoResultFound:
        return None


async def create_user(db: AsyncSession, user_data: dict) -> User:
    """创建新用户"""
    user = User(**user_data)
    db.add(user)
    await db.commit()
    await db.refresh(user)  # 刷新以获取数据库生成的ID
    return user


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = await db.execute(select(User).where(User.user_id == username))
    try:
        return result.scalar_one()
    except NoResultFound:
        return None


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """验证用户"""
    user = await get_user_by_username(db, username)
    if not user:
        return None
    # 这里需要实现密码验证逻辑，但需要引入密码验证函数
    # 由于SQLAlchemy模型中没有密码验证方法，这里需要外部提供验证函数
    return user