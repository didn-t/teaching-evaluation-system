from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.base import Base
from app.models import (
    User, College, Role, Permission, Timetable,
    EvaluationDimension, UserRole, RolePermission,
)
from app.database import get_db  # 你项目里已有的依赖


# 如果你数据库还没建表，改 True
CREATE_TABLES = False


async def acquire_session() -> Tuple[AsyncSession, Any]:
    """
    兼容 FastAPI 里的 get_db() 依赖（async generator）。
    返回 (session, generator)，最后需要 aclose generator
    """
    gen = get_db()
    db = await gen.__anext__()
    return db, gen


async def create_tables_if_needed():
    if not CREATE_TABLES:
        return

    import app.database as dbmod
    engine = getattr(dbmod, "async_engine", None) or getattr(dbmod, "engine", None)
    if engine is None:
        raise RuntimeError("找不到 async_engine/engine，请检查 app.database 里引擎变量名")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_or_create(
    db: AsyncSession,
    model: Type[Any],
    defaults: Optional[Dict[str, Any]] = None,
    **kwargs,
):
    defaults = defaults or {}
    res = await db.execute(select(model).filter_by(**kwargs))
    obj = res.scalar_one_or_none()
    if obj:
        return obj, False
    obj = model(**kwargs, **defaults)
    db.add(obj)
    await db.flush()  # 立刻拿到 id
    return obj, True


def safe_hash_password(raw: str) -> str:
    """
    测试数据用。优先用你项目里的 hash_password，否则直接存明文（仅测试）。
    """
    try:
        from app.core import hash_password  # 你的项目里很多地方这么导
        return hash_password(raw)
    except Exception:
        try:
            from app.core.auth import hash_password  # 如果你放在这里
            return hash_password(raw)
        except Exception:
            return raw


async def seed_basic_data(db: AsyncSession) -> Dict[str, Any]:
    # 1) 学院
    college, _ = await get_or_create(
        db,
        College,
        college_code="C01",
        defaults={"college_name": "计算机学院", "short_name": "计科", "sort_order": 1, "is_delete": False},
    )

    # 2) 权限（permission_code）
    perm_specs = [
        ("evaluation:submit", "提交评教"),
        ("evaluation:read:self", "查看自己提交的评教"),
        ("evaluation:delete:self", "删除自己提交的评教"),
        ("evaluation:read:received", "查看收到的评教"),
        ("evaluation:review", "审核评教"),
        ("evaluation:dimension:read", "查看评教维度"),
        ("evaluation:stats:teacher", "教师评教统计"),
        ("evaluation:stats:college", "学院评教统计"),
        ("evaluation:stats:school", "全校评教统计"),
    ]

    perm_by_code: Dict[str, Permission] = {}
    for code, name in perm_specs:
        p, _ = await get_or_create(
            db,
            Permission,
            permission_code=code,
            defaults={
                "permission_name": name,
                "permission_type": 2,  # 操作
                "sort_order": 1,
                "is_delete": False,
            },
        )
        perm_by_code[code] = p

    # 3) 角色（role_code）
    teacher_role, _ = await get_or_create(
        db,
        Role,
        role_code="teacher",
        defaults={"role_name": "教师", "role_level": 1, "status": 1, "is_delete": False},
    )
    college_admin_role, _ = await get_or_create(
        db,
        Role,
        role_code="college_admin",
        defaults={"role_name": "学院管理员", "role_level": 5, "status": 1, "is_delete": False},
    )
    school_admin_role, _ = await get_or_create(
        db,
        Role,
        role_code="school_admin",
        defaults={"role_name": "学校管理员", "role_level": 9, "status": 1, "is_delete": False},
    )

    # 4) 角色-权限：直接插 RolePermission（避免 role.permissions lazy load -> MissingGreenlet）
    async def bind_role_perms(role: Role, perm_codes: list[str]):
        for c in perm_codes:
            perm = perm_by_code[c]
            await get_or_create(
                db,
                RolePermission,
                role_id=role.id,
                permission_id=perm.id,
                defaults={},
            )

    await bind_role_perms(teacher_role, [
        "evaluation:submit",
        "evaluation:read:self",
        "evaluation:delete:self",
        "evaluation:read:received",
        "evaluation:dimension:read",
        "evaluation:stats:teacher",
    ])
    await bind_role_perms(college_admin_role, [
        "evaluation:read:received",
        "evaluation:review",
        "evaluation:dimension:read",
        "evaluation:stats:teacher",
        "evaluation:stats:college",
    ])
    await bind_role_perms(school_admin_role, [
        "evaluation:read:received",
        "evaluation:review",
        "evaluation:dimension:read",
        "evaluation:stats:teacher",
        "evaluation:stats:college",
        "evaluation:stats:school",
    ])

    # 5) 用户
    teach_user, _ = await get_or_create(
        db,
        User,
        user_on="T1001",
        defaults={
            "user_name": "授课老师A",
            "password": safe_hash_password("123456"),
            "college_id": college.id,
            "status": 1,
            "is_delete": False,
        },
    )
    listen_user, _ = await get_or_create(
        db,
        User,
        user_on="T2001",
        defaults={
            "user_name": "听课老师B",
            "password": safe_hash_password("123456"),
            "college_id": college.id,
            "status": 1,
            "is_delete": False,
        },
    )
    admin_user, _ = await get_or_create(
        db,
        User,
        user_on="A0001",
        defaults={
            "user_name": "学校管理员",
            "password": safe_hash_password("123456"),
            "college_id": college.id,
            "status": 1,
            "is_delete": False,
        },
    )

    # 6) 用户-角色：直接插 UserRole（避免 user.roles lazy load）
    async def bind_user_roles(user: User, role_codes: list[str]):
        code_to_role = {
            "teacher": teacher_role,
            "college_admin": college_admin_role,
            "school_admin": school_admin_role,
        }
        for rc in role_codes:
            r = code_to_role[rc]
            await get_or_create(
                db,
                UserRole,
                user_id=user.id,
                role_id=r.id,
                defaults={},
            )

    await bind_user_roles(teach_user, ["teacher"])
    await bind_user_roles(listen_user, ["teacher"])
    await bind_user_roles(admin_user, ["school_admin"])

    # 7) 评教维度
    await get_or_create(
        db,
        EvaluationDimension,
        dimension_code="teach",
        defaults={
            "dimension_name": "教学准备",
            "max_score": 20,
            "weight": 1.00,
            "sort_order": 1,
            "is_required": True,
            "status": 1,
            "is_delete": False,
        },
    )
    await get_or_create(
        db,
        EvaluationDimension,
        dimension_code="process",
        defaults={
            "dimension_name": "课堂实施",
            "max_score": 20,
            "weight": 1.00,
            "sort_order": 2,
            "is_required": True,
            "status": 1,
            "is_delete": False,
        },
    )

    # 8) 课表
    timetable, _ = await get_or_create(
        db,
        Timetable,
        teacher_id=teach_user.id,
        class_name="软件工程2022-1班",
        course_name="数据结构",
        academic_year="2024-2025",
        semester=2,
        weekday=4,
        period="第一大节",
        section_time="01-02",
        week_info="1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16",
        classroom="A101",
        defaults={
            "college_id": college.id,
            "class_id": None,
            "course_code": "CS2001",
            "weekday_text": "星期四",
            "student_count": 45,
            "credit": 3.0,
            "course_type": "必修",
            "sync_source": 0,
            "external_id": None,
            "raw_payload": None,
            "sync_status": 1,
            "is_delete": False,
        },
    )

    await db.commit()

    return {
        "college": college,
        "teach_user": teach_user,
        "listen_user": listen_user,
        "admin_user": admin_user,
        "timetable": timetable,
    }


async def run_flow_tests(db: AsyncSession, ctx: Dict[str, Any]):
    """
    跑一遍评教 CRUD 流程：
    - submit
    - duplicate block
    - list_mine
    - list_by_teacher(received)
    - update_status(review)
    - teacher_statistics
    """
    try:
        from app.crud.evaluation import evaluation_crud
    except Exception as e:
        raise RuntimeError(
            "找不到 evaluation_crud。请先确保 app/crud/evaluation.py 里导出了 evaluation_crud 实例。"
        ) from e

    teach_user: User = ctx["teach_user"]
    listen_user: User = ctx["listen_user"]
    timetable: Timetable = ctx["timetable"]

    print("\n=== [1] 提交一次评教（听课老师B -> 授课老师A） ===")
    listen_date = datetime.utcnow().replace(microsecond=0)

    ev = await evaluation_crud.submit(
        db,
        timetable_id=timetable.id,
        listen_teacher_id=listen_user.id,
        total_score=92,
        dimension_scores={"teach": 18, "process": 19},
        listen_date=listen_date,
        advantage_content="课堂节奏把控好，讲解清晰。",
        problem_content="板书稍少。",
        improve_suggestion="建议增加例题板书。",
        listen_duration=90,
        listen_location="A101",
        is_anonymous=False,
        status=1,
    )
    print(f"OK: evaluation_id={ev.id}, evaluation_no={ev.evaluation_no}, score_level={ev.score_level}")

    print("\n=== [2] 重复提交同一天同课表（应被拦截） ===")
    try:
        await evaluation_crud.submit(
            db,
            timetable_id=timetable.id,
            listen_teacher_id=listen_user.id,
            total_score=88,
            dimension_scores={"teach": 17, "process": 18},
            listen_date=listen_date,
            is_anonymous=False,
            status=1,
        )
        raise RuntimeError("ERROR: 重复提交未拦截（不应该发生）")
    except ValueError as e:
        print(f"OK: duplicate blocked -> {e}")

    print("\n=== [3] 我提交的列表（听课老师B） ===")
    mine, total = await evaluation_crud.list_mine(
        db,
        listen_teacher_id=listen_user.id,
        page=1,
        page_size=10,
    )
    print(f"OK: total={total}, first_id={mine[0].id if mine else None}")

    print("\n=== [4] 我收到的列表（授课老师A） ===")
    received, total_r = await evaluation_crud.list_by_teacher(
        db,
        teach_teacher_id=teach_user.id,
        page=1,
        page_size=10,
        academic_year="2024-2025",
        semester=2,
    )
    print(f"OK: total={total_r}, first_id={received[0].id if received else None}")

    print("\n=== [5] 审核/更新状态（仅测试 CRUD） ===")
    ev2 = await evaluation_crud.update_status(
        db,
        evaluation_id=ev.id,
        status=2,  # 你定义的 2=待审核/或其它
        review_comment="通过" if hasattr(ev, "review_comment") else None,
    )
    assert ev2 is not None
    print(f"OK: status={ev2.status}")

    print("\n=== [6] 教师统计（授课老师A） ===")
    stat = await evaluation_crud.teacher_statistics(
        db,
        teacher_id=teach_user.id,
        academic_year="2024-2025",
        semester=2,
    )
    print("OK:", {
        "total_evaluation_num": stat.get("total_evaluation_num"),
        "avg_total_score": stat.get("avg_total_score"),
        "score_distribution": stat.get("score_distribution"),
    })

    print("\n=== ALL TESTS PASSED ===\n")


async def main():
    await create_tables_if_needed()

    db, gen = await acquire_session()
    try:
        ctx = await seed_basic_data(db)
        await run_flow_tests(db, ctx)
    finally:
        await gen.aclose()


if __name__ == "__main__":
    asyncio.run(main())
