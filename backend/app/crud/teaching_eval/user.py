from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from typing import Optional, Any, Coroutine

from sqlalchemy.orm import selectinload

from app.models import User, Role, UserRole, Permission
from app.schemas import UserUpdate, TokenData


async def get_user(db: AsyncSession, user_id: str) -> Optional[User]:
    """
    根据用户编号获取用户
    :param db: 异步会话对象
    :param user_id: 用户ID
    :return: User对象（无返回None）
    """
    result = await db.execute(select(User).where(User.user_id == user_id))
    try:
        return result.scalar_one_or_none()
    except NoResultFound:
        return None


async def create_user(db: AsyncSession, user_data: dict) -> Optional[User]:
    """
    创建新用户
    :return: User对象（失败返回None）
    """
    user = User(**user_data)
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)  # 刷新以获取数据库生成的ID
        return user
    except Exception as e:
        print(e)
        return None


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    result = await db.execute(select(User).where(User.user_id == username))
    try:
        return result.scalar_one()
    except NoResultFound:
        return None


async def update_user(db: AsyncSession, token_data, user_data: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    user = await get_user(db, token_data.user_id)
    if not user:
        return None

    # 将模型转换为字典并过滤None值
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(user, key):
            setattr(user, key, value)

    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        print(e)
        await db.rollback()
        return None


async def get_roles_name(db: AsyncSession, token_data: Optional[TokenData]) -> list[str]:
    """
    根据用户user_id获取用户角色列表（返回角色名称列表）
    :param db: 异步会话对象
    :param token_data:
    :return: 角色名称列表（无角色返回空列表）
    """
    # 构建关联查询：UserRole关联Role，筛选指定user_id，查询角色名称
    stmt = (
        select(Role.role_name)
        .where(UserRole.user_id == token_data.user_id)  # 筛选用户ID
    )

    # 执行异步查询，提取标量结果列表
    result = await db.execute(stmt)
    try:
        role_list = result.scalars().all()  # 直接获取[str, str, ...] 或 []
        return list(role_list)
    except NoResultFound:
        return []


async def get_role_permissions(db: AsyncSession, token_data: Optional[TokenData]) -> list[str]:
    """
    根据角色role_id获取角色权限
    :param db: 异步会话对象
    :param token_data:

    :return: 返回角色权限列表（无角色返回空列表）
    """

    result = await db.execute(
        select(Role.permissions)
        .options(selectinload(Role.permissions))
    )
    return result.scalar_one_or_none()


async def get_user_permissions(db: AsyncSession, token_data: Optional[TokenData]) -> list[str]:
    """
    根据用户user_id获取用户全部权限
    :param db: 异步会话对象
    :param token_data:
    :return list[str]
    """
    try:
        # 查询用户及其关联的角色和权限
        result = await db.execute(
            select(Permission.permission_code)
            .where(UserRole.user_id == token_data.user_id)
        )

        data = result.all()

        return list(dict.fromkeys(item[0] for item in data))
    except NoResultFound:
        return []
