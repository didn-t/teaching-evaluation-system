from __future__ import annotations

import argparse
import asyncio
import json
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import (
    College, ResearchRoom, Major, Clazz,
    TeacherProfile, Timetable, User
)


# -----------------------------
# 工具：拿 AsyncSession
# -----------------------------
async def acquire_session() -> Tuple[AsyncSession, Any]:
    gen = get_db()
    db = await gen.__anext__()
    return db, gen


# -----------------------------
# 工具：读取 JSON
# -----------------------------
def load_json_list(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"{path} must be a JSON list")
    return data


# -----------------------------
# 星期映射
# -----------------------------
WEEKDAY_MAP = {
    "星期一": 1, "周一": 1,
    "星期二": 2, "周二": 2,
    "星期三": 3, "周三": 3,
    "星期四": 4, "周四": 4,
    "星期五": 5, "周五": 5,
    "星期六": 6, "周六": 6,
    "星期日": 7, "星期天": 7, "周日": 7, "周天": 7,
}


def normalize_weekday_text(s: str) -> str:
    s = (s or "").strip()
    return s


def weekday_to_int(s: str) -> int:
    s = normalize_weekday_text(s)
    if s in WEEKDAY_MAP:
        return WEEKDAY_MAP[s]
    # 兜底：尝试提取数字
    m = re.search(r"([1-7])", s)
    if m:
        return int(m.group(1))
    raise ValueError(f"无法解析星期字段: {s}")


# -----------------------------
# 工具：get_or_create
# -----------------------------
async def get_or_create_college(db: AsyncSession, college_name: str) -> College:
    college_name = (college_name or "").strip()
    if not college_name:
        raise ValueError("college_name empty")
    # 你模型 college_code unique，这里用名称生成一个稳定 code
    code = re.sub(r"\s+", "", college_name)
    code = re.sub(r"[^\w\u4e00-\u9fff]+", "", code)[:32] or "COL"
    stmt = select(College).where(College.college_name == college_name, College.is_delete == False)
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if obj:
        return obj

    obj = College(
        college_code=code,
        college_name=college_name,
        short_name=college_name[:16],
        sort_order=0,
        is_delete=False,
    )
    db.add(obj)
    await db.flush()
    return obj


async def get_or_create_major(db: AsyncSession, college_id: int, major_name: str) -> Major:
    major_name = (major_name or "").strip()
    if not major_name:
        major_name = "未分配专业"

    stmt = select(Major).where(
        Major.college_id == college_id,
        Major.major_name == major_name,
        Major.is_delete == False,
    )
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if obj:
        return obj

    # major_code 可空，这里不强塞
    obj = Major(
        major_code=None,
        major_name=major_name,
        short_name=major_name[:32],
        college_id=college_id,
        is_delete=False,
    )
    db.add(obj)
    await db.flush()
    return obj


async def get_or_create_clazz(db: AsyncSession, major_id: int, class_name: str, grade: Optional[str], class_code: Optional[str]) -> Clazz:
    class_name = (class_name or "").strip()
    if not class_name:
        raise ValueError("class_name empty")

    stmt = select(Clazz).where(
        Clazz.class_name == class_name,
        Clazz.is_delete == False,
    )
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if obj:
        # 补齐信息
        changed = False
        if obj.major_id is None and major_id:
            obj.major_id = major_id
            changed = True
        if grade and not obj.grade:
            obj.grade = grade
            changed = True
        if class_code and not obj.class_code:
            obj.class_code = class_code[:32]
            changed = True
        if changed:
            db.add(obj)
            await db.flush()
        return obj

    obj = Clazz(
        class_code=(class_code[:32] if class_code else None),
        class_name=class_name,
        grade=grade,
        major_id=major_id,
        is_delete=False,
    )
    db.add(obj)
    await db.flush()
    return obj


def gen_teacher_user_on(name: str) -> str:
    # user_on 必须唯一：用名字 + 简单hash尾巴
    base = re.sub(r"\s+", "", name)[:16] or "teacher"
    suffix = abs(hash(name)) % 100000
    return f"T_{base}_{suffix:05d}"[:32]


async def get_or_create_teacher_user(db: AsyncSession, teacher_name: str, college_id: Optional[int]) -> User:
    teacher_name = (teacher_name or "").strip()
    if not teacher_name:
        raise ValueError("teacher_name empty")

    # 先按 user_name 查（你这批数据里老师 likely 只有姓名）
    stmt = select(User).where(User.user_name == teacher_name, User.is_delete == False)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if user:
        # 补学院
        if college_id and user.college_id is None:
            user.college_id = college_id
            db.add(user)
            await db.flush()
        return user

    # 新建
    user_on = gen_teacher_user_on(teacher_name)

    # 避免 user_on 冲突：如果冲突就加随机尾巴（循环少量次）
    for i in range(10):
        stmt2 = select(User).where(User.user_on == user_on)
        r2 = await db.execute(stmt2)
        if r2.scalar_one_or_none() is None:
            break
        user_on = f"{user_on[:28]}{i:02d}"

    user = User(
        user_on=user_on,
        user_name=teacher_name,
        college_id=college_id,
        password="$2b$12$MIGRATION_DUMMY_HASH_DO_NOT_LOGIN",  # 迁移占位，不可登录
        status=1,
        is_delete=False,
    )
    db.add(user)
    await db.flush()
    return user


async def get_or_create_research_room(db: AsyncSession, college_id: int, room_name: str) -> ResearchRoom:
    room_name = (room_name or "").strip()
    if not room_name:
        room_name = "未分配教研室"

    stmt = select(ResearchRoom).where(
        ResearchRoom.college_id == college_id,
        ResearchRoom.room_name == room_name,
        ResearchRoom.is_delete == False,
    )
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if obj:
        return obj

    obj = ResearchRoom(
        room_name=room_name,
        college_id=college_id,
        is_delete=False,
    )
    db.add(obj)
    await db.flush()
    return obj


async def upsert_teacher_profile(
    db: AsyncSession,
    user_id: int,
    research_room_id: Optional[int],
    raw_payload: Optional[Dict[str, Any]] = None,
) -> TeacherProfile:
    stmt = select(TeacherProfile).where(TeacherProfile.user_id == user_id, TeacherProfile.is_delete == False)
    res = await db.execute(stmt)
    obj = res.scalar_one_or_none()
    if obj:
        changed = False
        if research_room_id and obj.research_room_id is None:
            obj.research_room_id = research_room_id
            changed = True
        if raw_payload:
            # 覆盖/合并都可；这里简单覆盖为最新
            obj.raw_payload = raw_payload
            changed = True
        if changed:
            db.add(obj)
            await db.flush()
        return obj

    obj = TeacherProfile(
        user_id=user_id,
        title=None,
        research_room_id=research_room_id,
        external_id=None,
        raw_payload=raw_payload,
        sync_status=1,
        is_delete=False,
    )
    db.add(obj)
    await db.flush()
    return obj


# -----------------------------
# 迁移：teacher_rooms.json
# -----------------------------
async def migrate_teacher_rooms(
    db: AsyncSession,
    teacher_rooms: List[Dict[str, Any]],
    college_name_hint: Optional[str] = None,
) -> Dict[str, int]:
    """
    返回 teacher_name -> user_id 映射，便于 timetable 复用
    """
    teacher_map: Dict[str, int] = {}

    # 如果你能提供“教师属于哪个学院”的映射更好。
    # 现在数据里没有学院字段，这里用 hint 或默认“未知学院”
    college_name = (college_name_hint or "未知学院").strip()
    college = await get_or_create_college(db, college_name)

    for item in teacher_rooms:
        teacher_name = (item.get("教师姓名") or "").strip()
        rooms = item.get("教研室") or []
        if not teacher_name:
            continue

        user = await get_or_create_teacher_user(db, teacher_name, college.id)

        # teacher_profile 只能挂 1 个教研室：默认取第一个
        chosen_room_id = None
        room_payload_list = []

        if isinstance(rooms, list):
            for rr in rooms:
                code = (rr.get("代码") or "").strip()
                name = (rr.get("名称") or "").strip()
                if not name:
                    continue
                room = await get_or_create_research_room(db, college.id, name)
                if chosen_room_id is None:
                    chosen_room_id = room.id
                room_payload_list.append({"code": code, "name": name})

        await upsert_teacher_profile(
            db,
            user_id=user.id,
            research_room_id=chosen_room_id,
            raw_payload={"rooms": room_payload_list},
        )

        teacher_map[teacher_name] = user.id

    await db.commit()
    return teacher_map


# -----------------------------
# 迁移：timetable.json
# -----------------------------
@dataclass
class TimetableDefaults:
    academic_year: str
    semester: int


async def migrate_timetables(
    db: AsyncSession,
    timetable_rows: List[Dict[str, Any]],
    defaults: TimetableDefaults,
    teacher_name_to_user_id: Optional[Dict[str, int]] = None,
) -> None:
    teacher_name_to_user_id = teacher_name_to_user_id or {}

    for row in timetable_rows:
        class_name = (row.get("班级") or "").strip()
        college_name = (row.get("学院") or "").strip() or "未知学院"
        major_name = (row.get("专业") or "").strip() or "未分配专业"
        grade = (row.get("年级") or "").strip() or None

        weekday_text = (row.get("星期") or "").strip()
        period = (row.get("节次") or "").strip()
        course_name = (row.get("course") or "").strip()
        teacher_name = (row.get("teacher") or "").strip()

        class_code = (row.get("class_code") or "").strip() or None
        week_info = (row.get("week_info") or "").strip()
        section_time = (row.get("section_time") or "").strip()
        classroom = (row.get("classroom") or "")
        classroom = classroom if classroom is not None else ""
        classroom = str(classroom).strip()

        if not (class_name and weekday_text and period and course_name and teacher_name and week_info and section_time):
            # 必要字段缺失直接跳过
            continue

        college = await get_or_create_college(db, college_name)
        major = await get_or_create_major(db, college.id, major_name)
        clazz = await get_or_create_clazz(db, major.id, class_name, grade, class_code)

        # teacher -> user
        teacher_user_id = teacher_name_to_user_id.get(teacher_name)
        if not teacher_user_id:
            teacher_user = await get_or_create_teacher_user(db, teacher_name, college.id)
            teacher_user_id = teacher_user.id
            teacher_name_to_user_id[teacher_name] = teacher_user_id

        weekday_int = weekday_to_int(weekday_text)

        # 查重：优先按 uk_timetable_slot（你模型里已定义）
        stmt = select(Timetable).where(
            Timetable.academic_year == defaults.academic_year,
            Timetable.semester == defaults.semester,
            Timetable.teacher_id == teacher_user_id,
            Timetable.class_name == class_name,
            Timetable.course_name == course_name,
            Timetable.weekday == weekday_int,
            Timetable.period == period,
            Timetable.section_time == section_time,
            Timetable.week_info == week_info,
            Timetable.classroom == classroom,
            Timetable.is_delete == False,
        )
        res = await db.execute(stmt)
        exist = res.scalar_one_or_none()
        if exist:
            # 补齐可选字段
            changed = False
            if exist.college_id is None:
                exist.college_id = college.id
                changed = True
            if exist.class_id is None:
                exist.class_id = clazz.id
                changed = True
            if exist.weekday_text is None:
                exist.weekday_text = weekday_text
                changed = True
            if changed:
                db.add(exist)
                await db.flush()
            continue

        obj = Timetable(
            college_id=college.id,
            teacher_id=teacher_user_id,
            class_id=clazz.id,
            class_name=class_name,
            course_code=None,
            course_name=course_name,
            academic_year=defaults.academic_year,
            semester=defaults.semester,
            weekday=weekday_int,
            weekday_text=weekday_text,
            period=period,
            section_time=section_time,
            week_info=week_info,
            classroom=classroom,
            student_count=None,
            credit=None,
            course_type=None,
            sync_source=0,
            external_id=None,
            raw_payload=row,  # 直接保留源数据，便于回溯
            sync_status=1,
            is_delete=False,
        )
        db.add(obj)

    await db.commit()


# -----------------------------
# 主函数
# -----------------------------
async def main():
    # 配置参数 - 请在下方设置迁移参数
    timetable_json_path = "2025-2026-1.json"  # 课表json文件路径
    teacher_rooms_json_path = "teachers.json"  # 教师教研室json文件路径
    academic_year = "2024-2025"  # 学年，如 2024-2025
    semester = 2  # 学期：1春季 2秋季
    teacher_college_hint = "未知学院"  # teacher_rooms.json 不带学院时，用这个学院名兜底

    # 加载JSON数据
    timetable_rows = load_json_list(timetable_json_path)
    teacher_rooms_rows = load_json_list(teacher_rooms_json_path)

    db, gen = await acquire_session()
    try:
        # 先迁移 teacher_rooms，拿到 teacher_name -> user_id 映射
        teacher_map = await migrate_teacher_rooms(db, teacher_rooms_rows, college_name_hint=teacher_college_hint)

        # 再迁移 timetable
        defaults = TimetableDefaults(academic_year=academic_year, semester=semester)
        await migrate_timetables(db, timetable_rows, defaults, teacher_name_to_user_id=teacher_map)

        print("✅ Migration done.")
        print(f"teachers mapped: {len(teacher_map)}")
        print(f"timetable rows input: {len(timetable_rows)}")
    finally:
        await gen.aclose()


if __name__ == "__main__":
    asyncio.run(main())
