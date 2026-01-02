# app/crud/user.py
from __future__ import annotations

from typing import Optional, List

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_async import CRUDBaseAsync
from app.models import User, Role, UserRole, Permission, RolePermission, SupervisorScope  # 按你的实际路径改
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

    async def get_users_with_roles(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 20,
        college_id: Optional[int] = None,
        max_role_level: Optional[int] = None,
    ) -> tuple[List[User], int]:
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
            # 22300417陈俫坤开发：使用 outerjoin，避免“没有任何角色的新用户”被过滤掉
            stmt = stmt.outerjoin(
                user_role_level_subq,
                User.id == user_role_level_subq.c.user_id
            )
            stmt = stmt.where(or_(user_role_level_subq.c.min_role_level <= max_role_level,
                                 user_role_level_subq.c.min_role_level.is_(None)))

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

            # 22300417陈俫坤开发：outerjoin + 允许空角色用户计入列表统计
            count_stmt = count_stmt.outerjoin(
                user_role_level_subq,
                User.id == user_role_level_subq.c.user_id
            )
            count_stmt = count_stmt.where(or_(user_role_level_subq.c.min_role_level <= max_role_level,
                                             user_role_level_subq.c.min_role_level.is_(None)))

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
        role_ids_subq = select(UserRole.role_id).where(UserRole.user_id == user_id)

        stmt = (
            select(Permission.permission_code)
            .join(RolePermission, Permission.id == RolePermission.permission_id)
            .where(RolePermission.role_id.in_(role_ids_subq))
        )
        res = await db.execute(stmt)
        return list(res.scalars().all())


# ---------------------------
# 22300417陈俫坤开发：督导负责范围（多学院/多教研组）
# ---------------------------
async def get_supervisor_scope_ids(db: AsyncSession, *, supervisor_user_id: int) -> tuple[list[int], list[int]]:
    """返回 (college_ids, research_room_ids)"""
    stmt = select(SupervisorScope.scope_type, SupervisorScope.scope_id).where(
        SupervisorScope.supervisor_user_id == supervisor_user_id,
        SupervisorScope.is_delete == False,  # noqa: E712
    )
    rows = (await db.execute(stmt)).all()
    college_ids: list[int] = []
    research_room_ids: list[int] = []
    for t, sid in rows:
        if t == "college":
            college_ids.append(int(sid))
        elif t == "research_room":
            research_room_ids.append(int(sid))
    # 去重
    college_ids = sorted(list({*college_ids}))
    research_room_ids = sorted(list({*research_room_ids}))
    return college_ids, research_room_ids


async def set_supervisor_scope_ids(
    db: AsyncSession,
    *,
    supervisor_user_id: int,
    college_ids: list[int],
    research_room_ids: list[int],
) -> None:
    """幂等设置范围：先软删旧记录，再插入新记录"""
    # 软删旧记录
    await db.execute(
        SupervisorScope.__table__.update()
        .where(SupervisorScope.supervisor_user_id == supervisor_user_id, SupervisorScope.is_delete == False)  # noqa: E712
        .values(is_delete=True)
    )

    # 插入新记录
    for cid in sorted(list({int(x) for x in (college_ids or [])})):
        db.add(SupervisorScope(supervisor_user_id=supervisor_user_id, scope_type="college", scope_id=cid, is_delete=False))
    for rid in sorted(list({int(x) for x in (research_room_ids or [])})):
        db.add(SupervisorScope(supervisor_user_id=supervisor_user_id, scope_type="research_room", scope_id=rid, is_delete=False))

    await db.commit()


async def get_effective_supervisor_scope(
    db: AsyncSession,
    *,
    current_user: TokenData,
) -> tuple[list[int], list[int]]:
    """22300417陈俫坤开发：获取督导有效范围（有配置优先，否则回退到 current_user.college_id）"""
    college_ids, research_room_ids = await get_supervisor_scope_ids(db, supervisor_user_id=current_user.id)
    if college_ids or research_room_ids:
        return college_ids, research_room_ids
    # fallback：兼容旧行为
    if getattr(current_user, "college_id", None):
        return [int(current_user.college_id)], []
    return [], []


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
