from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime
from typing import Any, Dict, Optional, Tuple, Type

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import (
    Base,  # noqa: F401 (确保模型元数据已加载)
    College, Role, Permission, User,
    UserRole, RolePermission,
    EvaluationDimension, Timetable,
)


# -----------------------------
# 配置
# -----------------------------
DEFAULT_BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")

# 你的接口前缀（从 main.py 中的路由配置看出来的）
API_PREFIX_USER = "/api/v1/teaching-eval/user"
API_PREFIX_EVAL = "/api/v1/teaching-eval/eval"

# 你项目里 token 可能被中间件塞进 response header/cookie/json，脚本会自动尝试提取并测试
TOKEN_CANDIDATE_HEADERS = ["authorization", "Authorization", "token", "Token", "x-token", "X-Token"]


# -----------------------------
# DB 小工具：拿 AsyncSession
# -----------------------------
async def acquire_session() -> Tuple[AsyncSession, Any]:
    gen = get_db()
    db = await gen.__anext__()
    return db, gen


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
    await db.flush()
    return obj, True


def safe_hash_password(raw: str) -> str:
    try:
        from app.core import hash_password  # 你项目里常用这种导入
        return hash_password(raw)
    except Exception:
        try:
            from app.core.auth import hash_password  # 如果你放在这里
            return hash_password(raw)
        except Exception:
            return raw


# -----------------------------
# 关键：避免 MissingGreenlet
# 不直接 role.permissions.append / user.roles.append
# 而是直接插 RolePermission / UserRole
# -----------------------------
async def seed_db_data() -> Dict[str, Any]:
    db, gen = await acquire_session()
    try:
        # 1) 学院
        college, _ = await get_or_create(
            db,
            College,
            college_code="C01",
            defaults={"college_name": "计算机学院", "short_name": "计科", "sort_order": 1, "is_delete": False},
        )

        # 2) 权限
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
                    "permission_type": 2,
                    "sort_order": 1,
                    "is_delete": False,
                },
            )
            perm_by_code[code] = p

        # 3) 角色
        teacher_role, _ = await get_or_create(
            db,
            Role,
            role_code="teacher",
            defaults={"role_name": "教师", "role_level": 1, "status": 1, "is_delete": False},
        )
        school_admin_role, _ = await get_or_create(
            db,
            Role,
            role_code="school_admin",
            defaults={"role_name": "学校管理员", "role_level": 9, "status": 1, "is_delete": False},
        )

        # 4) 角色-权限（直插中间表）
        async def bind_role_perms(role: Role, perm_codes: list[str]):
            for c in perm_codes:
                await get_or_create(
                    db,
                    RolePermission,
                    role_id=role.id,
                    permission_id=perm_by_code[c].id,
                )

        await bind_role_perms(teacher_role, [
            "evaluation:submit",
            "evaluation:read:self",
            "evaluation:delete:self",
            "evaluation:read:received",
            "evaluation:dimension:read",
            "evaluation:stats:teacher",
        ])
        await bind_role_perms(school_admin_role, [
            "evaluation:read:received",
            "evaluation:review",
            "evaluation:dimension:read",
            "evaluation:stats:teacher",
            "evaluation:stats:college",
            "evaluation:stats:school",
        ])

        # 5) 用户（授课老师 / 听课老师 / 管理员）
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

        # 6) 用户-角色（直插中间表）
        async def bind_user_role(user: User, role: Role):
            await get_or_create(db, UserRole, user_id=user.id, role_id=role.id)

        await bind_user_role(teach_user, teacher_role)
        await bind_user_role(listen_user, teacher_role)
        await bind_user_role(admin_user, school_admin_role)

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
                "course_code": "CS2001",
                "weekday_text": "星期四",
                "student_count": 45,
                "credit": 3.0,
                "course_type": "必修",
                "sync_source": 0,
                "is_delete": False,
            },
        )

        await db.commit()

        return {
            "college_id": college.id,
            "teach_user_on": teach_user.user_on,
            "listen_user_on": listen_user.user_on,
            "admin_user_on": admin_user.user_on,
            "timetable_id": timetable.id,
        }
    finally:
        await gen.aclose()


# -----------------------------
# Token 提取与鉴权请求
# -----------------------------
def extract_token(resp: httpx.Response) -> Optional[str]:
    # 1) header
    for k in TOKEN_CANDIDATE_HEADERS:
        if k in resp.headers:
            v = resp.headers.get(k)
            if not v:
                continue
            # 可能是 "Bearer xxx"
            parts = v.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                return parts[1]
            return v.strip()

    # 2) cookie
    for ck in ["access_token", "token", "Authorization", "authorization"]:
        if ck in resp.cookies:
            v = resp.cookies.get(ck)
            if v:
                return v

    # 3) json body
    try:
        j = resp.json()
        # 你们 BaseResponse 里现在没返回 token，但做个兜底
        for path in [
            ("token",),
            ("data", "token"),
            ("data", "access_token"),
            ("data", "token_obj", "token"),
        ]:
            cur = j
            ok = True
            for p in path:
                if isinstance(cur, dict) and p in cur:
                    cur = cur[p]
                else:
                    ok = False
                    break
            if ok and isinstance(cur, str) and cur:
                return cur
    except Exception:
        pass

    return None


def auth_candidates(token: str) -> list[dict]:
    """
    尝试不同 token 传递方式，避免你们中间件/依赖实现差异导致 401。
    """
    return [
        {"headers": {"Authorization": f"Bearer {token}"}},
        {"headers": {"Authorization": token}},
        {"headers": {"token": token}},
        {"headers": {"X-Token": token}},
    ]


async def request_authed(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    token: str,
    **kwargs,
) -> httpx.Response:
    last = None
    for opt in auth_candidates(token):
        merged = dict(kwargs)
        headers = dict(merged.get("headers") or {})
        headers.update(opt["headers"])
        merged["headers"] = headers
        resp = await client.request(method, url, **merged)
        last = resp
        if resp.status_code != 401:
            return resp
    return last  # type: ignore


# -----------------------------
# API 测试流程
# -----------------------------
async def api_flow(base_url: str, timetable_id: int):
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        print(f"\n[1] GET /health")
        r = await client.get("/health")
        print("status:", r.status_code, "body:", r.text[:200])

        # -------- register/login --------
        async def register_or_login(user_on: str, user_name: str, password: str, college_id: Optional[int] = None) -> str:
            reg_payload = {"user_on": user_on, "password": password, "user_name": user_name, "college_id": str(college_id) if college_id else None}
            print(f"\n[2] POST register {user_on}")
            rr = await client.post(f"{API_PREFIX_USER}/register", json=reg_payload)
            if rr.status_code >= 400:
                print("register failed:", rr.status_code, rr.text[:200])
                print(f"[2b] POST login {user_on}")
                rr = await client.post(f"{API_PREFIX_USER}/login", json={"user_on": user_on, "password": password})
            else:
                print("register ok:", rr.status_code)

            token = extract_token(rr)
            if not token:
                print("⚠️ 无法自动提取 token。响应 headers keys=", list(rr.headers.keys()))
                print("响应 body(前200)=", rr.text[:200])
                raise RuntimeError("拿不到 token：请检查你们中间件把 token 放在哪（header/cookie/body）")

            print("token ok (len):", len(token))
            return token

        # 你种子里是 123456
        teacherA_token = await register_or_login("T1001", "授课老师A", "123456")
        teacherB_token = await register_or_login("T2001", "听课老师B", "123456")
        admin_token = await register_or_login("A0001", "学校管理员", "123456")

        # -------- /me --------
        print("\n[3] GET /user/me (teacherB)")
        r = await request_authed(client, "GET", f"{API_PREFIX_USER}/me", teacherB_token)
        print("status:", r.status_code, "body:", r.text[:300])

        # -------- dimensions --------
        print("\n[4] GET /evaluation/dimensions (teacherB)")
        r = await request_authed(client, "GET", f"{API_PREFIX_EVAL}/dimensions", teacherB_token)
        print("status:", r.status_code, "body:", r.text[:300])

        # -------- dimensions 获取可用维度 --------
        print("\n[4b] GET /evaluation/dimensions (for submit)")
        r = await request_authed(client, "GET", f"{API_PREFIX_EVAL}/dimensions", teacherB_token)
        print("status:", r.status_code, "body:", r.text[:300])
        
        dimensions_data = []
        try:
            dimensions_data = r.json().get("data", [])
        except Exception:
            pass
        
        # 使用实际存在的维度代码，如果没有获取到维度，则使用默认的
        if dimensions_data:
            # 使用前两个维度
            if len(dimensions_data) >= 2:
                dim1_code = dimensions_data[0]["dimension_code"]
                dim2_code = dimensions_data[1]["dimension_code"]
            elif len(dimensions_data) == 1:
                dim1_code = dimensions_data[0]["dimension_code"]
                dim2_code = dimensions_data[0]["dimension_code"]  # 重复使用第一个
            else:
                # 默认维度代码
                dim1_code = "teach"
                dim2_code = "process"
        else:
            # 默认维度代码
            dim1_code = "teach"
            dim2_code = "process"
        
        # -------- submit evaluation --------
        print("\n[5] POST /evaluation/submit (teacherB -> timetable)")
        submit_payload = {
            "timetable_id": timetable_id,
            "total_score": 92,
            "dimension_scores": {dim1_code: 18, dim2_code: 19},
            "advantage_content": "课堂节奏把控好，讲解清晰。",
            "problem_content": "板书稍少。",
            "improve_suggestion": "建议增加例题板书。",
            "listen_date": datetime.utcnow().replace(microsecond=0).isoformat(),
            "listen_duration": 90,
            "listen_location": "A101",
            "is_anonymous": False,
        }
        r = await request_authed(client, "POST", f"{API_PREFIX_EVAL}/submit", teacherB_token, json=submit_payload)
        print("status:", r.status_code, "body:", r.text[:500])
        if r.status_code >= 400:
            raise RuntimeError("submit failed")

        j = r.json()
        evaluation_id = None
        try:
            evaluation_id = j.get("data", {}).get("id")
        except Exception:
            pass
        if not evaluation_id:
            raise RuntimeError("提交成功但拿不到 evaluation_id，请检查返回结构")

        # -------- mine --------
        print("\n[6] GET /evaluation/mine (teacherB)")
        r = await request_authed(client, "GET", f"{API_PREFIX_EVAL}/mine?page=1&page_size=10", teacherB_token)
        print("status:", r.status_code, "body:", r.text[:500])

        # -------- received --------
        print("\n[7] GET /evaluation/received (teacherA)")
        r = await request_authed(client, "GET", f"{API_PREFIX_EVAL}/received?page=1&page_size=10", teacherA_token)
        print("status:", r.status_code, "body:", r.text[:500])

        # -------- review --------
        print("\n[8] PUT /evaluation/{id}/review (admin)")
        review_payload = {"status": 1, "review_comment": "审核通过"}
        r = await request_authed(client, "PUT", f"{API_PREFIX_EVAL}/{evaluation_id}/review", admin_token, json=review_payload)
        print("status:", r.status_code, "body:", r.text[:500])

        # -------- stats: teacher me --------
        print("\n[9] GET /evaluation/statistics/teacher/me (teacherA)")
        r = await request_authed(client, "GET", f"{API_PREFIX_EVAL}/statistics/teacher/me?academic_year=2024-2025&semester=2", teacherA_token)
        print("status:", r.status_code, "body:", r.text[:500])

        print("\n✅ API E2E DONE")


async def main():
    # 配置变量
    BASE_URL = "http://127.0.0.1:8000"  # 修改此变量以更改基础URL
    SEED_DB = True  # 是否写入种子数据

    timetable_id = None
    if SEED_DB:
        print("==> Seeding DB ...")
        ctx = await seed_db_data()
        timetable_id = ctx["timetable_id"]
        print("Seed OK. timetable_id =", timetable_id)
    else:
        # 如果不 seed，你必须自己保证库里已经有 timetable + roles/permissions
        timetable_id_env = os.getenv("TIMETABLE_ID")
        if not timetable_id_env:
            raise RuntimeError("未指定 timetable_id：请用 SEED_DB=True 或设置环境变量 TIMETABLE_ID=xxx")
        timetable_id = int(timetable_id_env)

    await api_flow(BASE_URL, timetable_id)


if __name__ == "__main__":
    asyncio.run(main())
