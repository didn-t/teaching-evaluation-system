# app/crud/user.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_async import CRUDBaseAsync
from app.models import User, Role, UserRole, Permission, RolePermission  # 按你的实际路径改
from app.schemas import TokenData, UserUpdate  # 按你的实际路径改

# 下面这两行按你 auth.py 真实函数名改一下即可：
from app.core.auth import get_password_hash, verify_password  # noqa: F401


class CRUDUser(CRUDBaseAsync[User]):
    async def get_by_user_on(self, db: AsyncSession, *, user_on: str) -> Optional[User]:
        stmt = select(User).where(User.user_on == user_on, User.is_delete == False)  # noqa: E712
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, *, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id, User.is_delete == False)  # noqa: E712
        res = await db.execute(stmt)
        return res.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, *, user_data: dict) -> User:
        # 如果 user_data 里是明文密码，建议在这里 hash（字段名按你 schema）
        if "password" in user_data and user_data["password"]:
            user_data["password"] = get_password_hash(user_data["password"])

        user = User(**user_data)
        db.add(user)
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise ValueError(f"创建用户失败: {e}") from e

    async def update_user(self, db: AsyncSession, *, token_data: TokenData, user_data: UserUpdate) -> Optional[User]:
        user = await self.get_by_id(db, user_id=token_data.id)
        if not user:
            return None

        update_dict = user_data.model_dump(exclude_unset=True)
        for k, v in update_dict.items():
            if hasattr(user, k):
                setattr(user, k, v)

        try:
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise ValueError(f"更新用户失败: {e}") from e

    async def reset_password(self, db: AsyncSession, *, user_id: int, new_password: str) -> Optional[User]:
        user = await self.get_by_id(db, user_id=user_id)
        if not user:
            return None

        user.password = get_password_hash(new_password)
        try:
            await db.commit()
            await db.refresh(user)
            return user
        except Exception as e:
            await db.rollback()
            raise ValueError(f"重置密码失败: {e}") from e

    async def get_user_role_level(self, db: AsyncSession, *, user_id: int) -> int:
        stmt = (
            select(func.min(Role.role_level))
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        res = await db.execute(stmt)
        return res.scalar_one() or 0

    async def get_users_with_roles(self, db: AsyncSession, *, skip: int = 0, limit: int = 20, 
                                 college_id: Optional[int] = None, max_role_level: Optional[int] = None) -> tuple[List[User], int]:
        from sqlalchemy import and_
        
        # 构建查询语句
        stmt = select(User)
        
        # 添加学院过滤
        if college_id is not None:
            stmt = stmt.where(User.college_id == college_id)
        
        # 构建角色等级过滤条件
        if max_role_level is not None:
            # 使用子查询获取用户的最小角色等级
            user_role_level_subq = select(
                UserRole.user_id,
                func.min(Role.role_level).label('min_role_level')
            ).join(Role, UserRole.role_id == Role.id)
            user_role_level_subq = user_role_level_subq.group_by(UserRole.user_id)
            user_role_level_subq = user_role_level_subq.subquery()
            
            # 添加角色等级过滤
            stmt = stmt.join(
                user_role_level_subq, 
                User.id == user_role_level_subq.c.user_id
            )
            stmt = stmt.where(user_role_level_subq.c.min_role_level <= max_role_level)
        
        # 默认排除软删除
        stmt = stmt.where(User.is_delete == False)  # noqa: E712
        
        # 添加排序
        stmt = stmt.order_by(User.id)
        
        # 添加分页
        stmt = stmt.offset(skip).limit(limit)
        
        # 执行查询
        result = await db.execute(stmt)
        items = list(result.scalars().all())
        
        # 计算总数
        count_stmt = select(func.count()).select_from(User)
        
        # 添加相同的过滤条件
        if college_id is not None:
            count_stmt = count_stmt.where(User.college_id == college_id)
        
        if max_role_level is not None:
            # 与上面相同的子查询
            user_role_level_subq = select(
                UserRole.user_id,
                func.min(Role.role_level).label('min_role_level')
            ).join(Role, UserRole.role_id == Role.id)
            user_role_level_subq = user_role_level_subq.group_by(UserRole.user_id)
            user_role_level_subq = user_role_level_subq.subquery()
            
            count_stmt = count_stmt.join(
                user_role_level_subq, 
                User.id == user_role_level_subq.c.user_id
            )
            count_stmt = count_stmt.where(user_role_level_subq.c.min_role_level <= max_role_level)
        
        count_stmt = count_stmt.where(User.is_delete == False)  # noqa: E712
        
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()
        
        return items, total

    async def authenticate(self, db: AsyncSession, *, user_on: str, plain_password: str) -> Optional[User]:
        user = await self.get_by_user_on(db, user_on=user_on)
        if not user:
            return None
        if user.status != 1 or user.is_delete:
            return None
        if not verify_password(plain_password, user.password):
            return None
        return user

    async def get_roles_name(self, db: AsyncSession, *, user_id: int) -> List[str]:
        stmt = (
            select(Role.role_name)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_roles_code(self, db: AsyncSession, *, user_id: int) -> List[str]:
        stmt = (
            select(Role.role_code)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())

    async def get_user_permissions(self, db: AsyncSession, *, user_id: int) -> List[str]:
        # 用子查询拿 role_id，再查 permission_code（你旧代码思路是对的）
        role_ids_subq = select(UserRole.role_id).where(UserRole.user_id == user_id)

        stmt = (
            select(Permission.permission_code)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(RolePermission.role_id.in_(role_ids_subq))
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


user_crud = CRUDUser(User)


# ---------------------------
# 兼容层：保留你旧函数签名（可选）
# 如果你愿意改上层 import，可以删掉下面这些 wrapper
# ---------------------------

async def get_user(db: AsyncSession, user_on: str) -> Optional[User]:
    return await user_crud.get_by_user_on(db, user_on=user_on)


async def get_user_by_id(db: AsyncSession, token_data: TokenData) -> Optional[User]:
    return await user_crud.get_by_id(db, user_id=token_data.id)


async def create_user(db: AsyncSession, user_data: dict) -> Optional[User]:
    return await user_crud.create_user(db, user_data=user_data)


async def update_user(db: AsyncSession, token_data: TokenData, user_data: UserUpdate) -> Optional[User]:
    return await user_crud.update_user(db, token_data=token_data, user_data=user_data)


async def reset_user_password(db: AsyncSession, user_id: int, new_password: str) -> Optional[User]:
    return await user_crud.reset_password(db, user_id=user_id, new_password=new_password)


async def get_user_role_level(db: AsyncSession, token_data: TokenData) -> int:
    return await user_crud.get_user_role_level(db, user_id=token_data.id)


async def get_users_list(db: AsyncSession, skip: int = 0, limit: int = 20, 
                        college_id: Optional[int] = None, max_role_level: Optional[int] = None) -> tuple[List[User], int]:
    return await user_crud.get_users_with_roles(db, skip=skip, limit=limit, 
                                              college_id=college_id, max_role_level=max_role_level)


async def get_roles_name(db: AsyncSession, token_data: TokenData) -> list[str]:
    return await user_crud.get_roles_name(db, user_id=token_data.id)


async def get_roles_code(db: AsyncSession, token_data: TokenData) -> list[str]:
    return await user_crud.get_roles_code(db, user_id=token_data.id)


async def get_user_permissions(db: AsyncSession, token_data: TokenData) -> list[str]:
    return await user_crud.get_user_permissions(db, user_id=token_data.id)
