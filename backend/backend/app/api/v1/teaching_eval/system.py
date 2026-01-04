from __future__ import annotations

import os
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.auth import get_password_hash
from app.models import Permission, Role, RolePermission, User, UserRole

router = APIRouter(prefix="", tags=["系统初始化"])


def _require_local_or_token(request: Request) -> None:
    """22300417陈俫坤开发：限制 bootstrap 仅本机调用，或携带约定 token（避免误暴露）"""

    expected = os.getenv("BOOTSTRAP_TOKEN")
    if expected:
        got = request.headers.get("x-bootstrap-token")
        if got != expected:
            raise HTTPException(status_code=403, detail="bootstrap token invalid")
        return

    host = getattr(request.client, "host", "") if request.client else ""
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise HTTPException(status_code=403, detail="bootstrap only allowed from localhost")


async def bootstrap_seed(db: AsyncSession) -> Dict[str, Any]:
    """22300417陈俫坤开发：幂等初始化（权限/角色/角色权限/初始账号/用户角色）"""

    permissions: List[Dict[str, Any]] = [
        # 课表管理
        {"permission_code": "timetable:view:self", "permission_name": "查看个人课表", "permission_type": 1, "parent_id": None, "sort_order": 1},
        {"permission_code": "timetable:view:college", "permission_name": "查看学院课表", "permission_type": 1, "parent_id": None, "sort_order": 2},
        {"permission_code": "timetable:view:all", "permission_name": "查看全校课表", "permission_type": 1, "parent_id": None, "sort_order": 3},

        # 评教管理
        {"permission_code": "evaluation:submit", "permission_name": "提交评分和建议", "permission_type": 2, "parent_id": None, "sort_order": 10},
        {"permission_code": "evaluation:view:self", "permission_name": "查看个人评教结果", "permission_type": 1, "parent_id": None, "sort_order": 11},
        {"permission_code": "evaluation:view:college", "permission_name": "查看学院评教详情", "permission_type": 1, "parent_id": None, "sort_order": 12},
        {"permission_code": "evaluation:view:all", "permission_name": "查看全校评教数据", "permission_type": 1, "parent_id": None, "sort_order": 13},
        {"permission_code": "evaluation:export:college", "permission_name": "导出学院评教报表", "permission_type": 3, "parent_id": None, "sort_order": 14},
        {"permission_code": "evaluation:export:all", "permission_name": "导出全校评教报表", "permission_type": 3, "parent_id": None, "sort_order": 15},
        {"permission_code": "evaluation:read:self", "permission_name": "查看本人提交的评教详情", "permission_type": 1, "parent_id": None, "sort_order": 16},
        {"permission_code": "evaluation:delete:self", "permission_name": "删除本人提交的评教记录", "permission_type": 2, "parent_id": None, "sort_order": 17},
        {"permission_code": "evaluation:read:received", "permission_name": "查看收到的评教", "permission_type": 1, "parent_id": None, "sort_order": 18},
        {"permission_code": "evaluation:dimension:read", "permission_name": "查看评教维度配置", "permission_type": 1, "parent_id": None, "sort_order": 19},
        {"permission_code": "evaluation:review", "permission_name": "审核评教记录", "permission_type": 2, "parent_id": None, "sort_order": 20},
        {"permission_code": "evaluation:stats:teacher", "permission_name": "查看教师评教统计", "permission_type": 1, "parent_id": None, "sort_order": 21},
        {"permission_code": "evaluation:stats:college", "permission_name": "查看学院评教统计", "permission_type": 1, "parent_id": None, "sort_order": 22},
        {"permission_code": "evaluation:stats:school", "permission_name": "查看全校评教统计", "permission_type": 1, "parent_id": None, "sort_order": 23},

        # 统计数据
        {"permission_code": "statistics:view:college_public", "permission_name": "查看本院公开统计数据", "permission_type": 1, "parent_id": None, "sort_order": 30},
        {"permission_code": "statistics:view:college_detail", "permission_name": "查看学院详细统计数据", "permission_type": 1, "parent_id": None, "sort_order": 31},
        {"permission_code": "statistics:view:all", "permission_name": "查看全校统计数据", "permission_type": 1, "parent_id": None, "sort_order": 32},

        # 用户管理
        {"permission_code": "user:manage:college", "permission_name": "维护本院用户账号", "permission_type": 2, "parent_id": None, "sort_order": 40},
        {"permission_code": "user:manage:all", "permission_name": "管理所有用户账号", "permission_type": 2, "parent_id": None, "sort_order": 41},

        # 角色权限管理（细分）
        {"permission_code": "auth:role:create", "permission_name": "创建角色", "permission_type": 2, "parent_id": None, "sort_order": 52},
        {"permission_code": "auth:role:read", "permission_name": "查看角色", "permission_type": 1, "parent_id": None, "sort_order": 53},
        {"permission_code": "auth:role:update", "permission_name": "更新角色", "permission_type": 2, "parent_id": None, "sort_order": 54},
        {"permission_code": "auth:role:delete", "permission_name": "删除角色", "permission_type": 2, "parent_id": None, "sort_order": 55},
        {"permission_code": "auth:permission:create", "permission_name": "创建权限", "permission_type": 2, "parent_id": None, "sort_order": 56},
        {"permission_code": "auth:permission:read", "permission_name": "查看权限", "permission_type": 1, "parent_id": None, "sort_order": 57},
        {"permission_code": "auth:permission:update", "permission_name": "更新权限", "permission_type": 2, "parent_id": None, "sort_order": 58},
        {"permission_code": "auth:permission:delete", "permission_name": "删除权限", "permission_type": 2, "parent_id": None, "sort_order": 59},
        {"permission_code": "auth:role:assign_permission", "permission_name": "给角色分配权限", "permission_type": 2, "parent_id": None, "sort_order": 60},
        {"permission_code": "auth:role:read_permissions", "permission_name": "查看角色权限", "permission_type": 1, "parent_id": None, "sort_order": 61},
        {"permission_code": "auth:user:assign_role", "permission_name": "给用户分配角色", "permission_type": 2, "parent_id": None, "sort_order": 62},

        # 组织结构管理
        {"permission_code": "org:college:create", "permission_name": "创建学院", "permission_type": 2, "parent_id": None, "sort_order": 70},
        {"permission_code": "org:college:read", "permission_name": "查看学院", "permission_type": 1, "parent_id": None, "sort_order": 71},
        {"permission_code": "org:college:update", "permission_name": "更新学院", "permission_type": 2, "parent_id": None, "sort_order": 72},
        {"permission_code": "org:college:delete", "permission_name": "删除学院", "permission_type": 2, "parent_id": None, "sort_order": 73},
        {"permission_code": "org:timetable:create", "permission_name": "创建课表", "permission_type": 2, "parent_id": None, "sort_order": 86},
        {"permission_code": "org:timetable:read", "permission_name": "查看课表", "permission_type": 1, "parent_id": None, "sort_order": 87},
        {"permission_code": "org:timetable:update", "permission_name": "更新课表", "permission_type": 2, "parent_id": None, "sort_order": 88},
        {"permission_code": "org:timetable:delete", "permission_name": "删除课表", "permission_type": 2, "parent_id": None, "sort_order": 89},

        # 系统配置
        {"permission_code": "system:config", "permission_name": "系统参数配置", "permission_type": 4, "parent_id": None, "sort_order": 90},
    ]

    roles: List[Dict[str, Any]] = [
        {"role_code": "teacher", "role_name": "老师", "role_level": 1, "description": "普通教师角色", "status": 1},
        {"role_code": "supervisor", "role_name": "督导老师", "role_level": 2, "description": "督导教师角色", "status": 1},
        {"role_code": "college_admin", "role_name": "学院管理员", "role_level": 3, "description": "学院管理员角色", "status": 1},
        {"role_code": "school_admin", "role_name": "学校管理员", "role_level": 4, "description": "学校管理员角色", "status": 1},
    ]

    role_permissions: Dict[str, List[str]] = {
        "teacher": [
            "timetable:view:self",
            "evaluation:submit",
            "evaluation:view:self",
            "evaluation:read:self",
            "evaluation:delete:self",
            "evaluation:read:received",
            "evaluation:dimension:read",
            "evaluation:stats:teacher",
            "statistics:view:college_public",
        ],
        "supervisor": [
            "timetable:view:college",
            "evaluation:submit",
            "evaluation:view:college",
            "evaluation:read:received",
            "evaluation:dimension:read",
            "evaluation:stats:teacher",
            "statistics:view:college_detail",
            "evaluation:export:college",
            # 22300417陈俫坤开发：督导老师需要读取学院列表/信息用于负责范围筛选
            "org:college:read",
            # 22300417陈俫坤开发：督导范围配置需要读取教研室列表
            "org:research_room:read",
        ],
        "college_admin": [
            "user:manage:college",
            "evaluation:view:college",
            "evaluation:review",
            "evaluation:stats:teacher",
            "evaluation:stats:college",
            "evaluation:export:college",
            "org:college:read",
            "org:timetable:create",
            "org:timetable:read",
            "org:timetable:update",
            "org:timetable:delete",
            "statistics:view:college_detail",
        ],
        "school_admin": [
            "user:manage:all",
            "evaluation:review",
            "evaluation:stats:school",
            "evaluation:stats:college",
            "evaluation:stats:teacher",
            "evaluation:export:all",
            "system:config",
            "auth:role:create",
            "auth:role:read",
            "auth:role:update",
            "auth:role:delete",
            "auth:permission:create",
            "auth:permission:read",
            "auth:permission:update",
            "auth:permission:delete",
            "auth:role:assign_permission",
            "auth:role:read_permissions",
            "auth:user:assign_role",
            "org:college:create",
            "org:college:read",
            "org:college:update",
            "org:college:delete",
        ],
    }

    seed_users: List[Dict[str, str]] = [
        {"user_on": "teacher001", "user_name": "老师", "password": "123456", "role_code": "teacher"},
        {"user_on": "supervisor001", "user_name": "督导老师", "password": "123456", "role_code": "supervisor"},
        {"user_on": "college001", "user_name": "学院管理员", "password": "123456", "role_code": "college_admin"},
        {"user_on": "school001", "user_name": "学校管理员", "password": "123456", "role_code": "school_admin"},
    ]

    created_permissions = 0
    created_roles = 0
    created_role_permissions = 0
    created_users = 0
    created_user_roles = 0

    # 1) permissions
    permission_objects: Dict[str, Permission] = {}
    for perm_data in permissions:
        stmt = select(Permission).where(Permission.permission_code == perm_data["permission_code"])
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            permission_objects[perm_data["permission_code"]] = existing
            continue
        p = Permission(**perm_data)
        db.add(p)
        permission_objects[perm_data["permission_code"]] = p
        created_permissions += 1

    await db.flush()

    # 2) roles
    role_objects: Dict[str, Role] = {}
    for role_data in roles:
        stmt = select(Role).where(Role.role_code == role_data["role_code"])
        res = await db.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            role_objects[role_data["role_code"]] = existing
            continue
        r = Role(**role_data)
        db.add(r)
        role_objects[role_data["role_code"]] = r
        created_roles += 1

    await db.flush()

    # 3) role_permission
    for role_code, perm_codes in role_permissions.items():
        role = role_objects.get(role_code)
        if not role:
            continue
        for perm_code in perm_codes:
            perm = permission_objects.get(perm_code)
            if not perm:
                continue
            stmt = select(RolePermission).where(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm.id,
            )
            res = await db.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                continue
            db.add(RolePermission(role_id=role.id, permission_id=perm.id))
            created_role_permissions += 1

    await db.flush()

    # 4) users + user_role
    for u in seed_users:
        stmt = select(User).where(User.user_on == u["user_on"], User.is_delete == False)  # noqa: E712
        res = await db.execute(stmt)
        existing_user = res.scalar_one_or_none()
        if not existing_user:
            user = User(
                user_on=u["user_on"],
                user_name=u["user_name"],
                password=get_password_hash(u["password"]),
                status=1,
                is_delete=False,
            )
            db.add(user)
            await db.flush()
            created_users += 1
        else:
            user = existing_user

        role = role_objects.get(u["role_code"])
        if role:
            stmt = select(UserRole).where(UserRole.user_id == user.id, UserRole.role_id == role.id)
            res = await db.execute(stmt)
            existing_ur = res.scalar_one_or_none()
            if not existing_ur:
                db.add(UserRole(user_id=user.id, role_id=role.id))
                created_user_roles += 1

    await db.commit()

    return {
        "created_permissions": created_permissions,
        "created_roles": created_roles,
        "created_role_permissions": created_role_permissions,
        "created_users": created_users,
        "created_user_roles": created_user_roles,
    }


@router.get("/bootstrap", summary="开发环境：幂等初始化权限/角色/初始账号")
@router.post("/bootstrap", summary="开发环境：幂等初始化权限/角色/初始账号")
async def bootstrap(request: Request, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """22300417陈俫坤开发：通过接口触发初始化（可重复调用不重复插入）"""

    # 仅允许开发/本机执行
    app_env = os.getenv("APP_ENV")
    if app_env and app_env.lower() in ("prod", "production"):
        raise HTTPException(status_code=403, detail="bootstrap disabled in production")

    _require_local_or_token(request)

    try:
        result = await bootstrap_seed(db)

        # 22300417陈俫坤开发：返回自检信息，方便确认是否已写入到当前连接的 MySQL 库
        seed_users = ["teacher001", "supervisor001", "college001", "school001"]
        res = await db.execute(
            select(User.user_on).where(User.user_on.in_(seed_users), User.is_delete == False)  # noqa: E712
        )
        present = set(res.scalars().all())
        missing = sorted([u for u in seed_users if u not in present])

        role_count_res = await db.execute(select(func.count(Role.id)).where(Role.is_delete == False))  # noqa: E712
        perm_count_res = await db.execute(select(func.count(Permission.id)).where(Permission.is_delete == False))  # noqa: E712

        result.update({
            "app_env": os.getenv("APP_ENV"),
            "mysql_db": os.getenv("MYSQL_DB"),
            "mysql_host": os.getenv("MYSQL_HOST_LOCAL") or os.getenv("MYSQL_HOST"),
            "seed_users_present": sorted(list(present)),
            "seed_users_missing": missing,
            "initialized": len(missing) == 0,
            "role_count": int(role_count_res.scalar_one() or 0),
            "permission_count": int(perm_count_res.scalar_one() or 0),
        })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"bootstrap failed: {e}")


@router.get("/db-info", summary="开发环境：查看当前服务连接的数据库信息")
async def db_info(request: Request, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """22300417陈俫坤开发：用于排查“注册/初始化写入不同库”的问题"""

    _require_local_or_token(request)

    try:
        # MySQL 当前 schema
        current_db_res = await db.execute(text("SELECT DATABASE()"))
        current_db = current_db_res.scalar_one_or_none()

        user_count_res = await db.execute(select(func.count(User.id)).where(User.is_delete == False))  # noqa: E712
        user_count = int(user_count_res.scalar_one() or 0)

        seed_users = ["teacher001", "supervisor001", "college001", "school001"]
        seed_res = await db.execute(
            select(User.user_on).where(User.user_on.in_(seed_users), User.is_delete == False)  # noqa: E712
        )
        seed_present = sorted(list(set(seed_res.scalars().all())))

        latest_res = await db.execute(
            select(User.user_on, User.user_name, User.id)
            .where(User.is_delete == False)  # noqa: E712
            .order_by(User.id.desc())
            .limit(10)
        )
        latest = [
            {"id": row.id, "user_on": row.user_on, "user_name": row.user_name}
            for row in latest_res.all()
        ]

        return {
            "app_env": os.getenv("APP_ENV"),
            "mysql_db_env": os.getenv("MYSQL_DB"),
            "mysql_host_env": os.getenv("MYSQL_HOST_LOCAL") or os.getenv("MYSQL_HOST"),
            "mysql_port_env": os.getenv("MYSQL_PORT"),
            "mysql_user_env": os.getenv("MYSQL_USER"),
            "current_db": current_db,
            "user_count": user_count,
            "seed_users_present": seed_present,
            "latest_users": latest,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"db-info failed: {e}")
