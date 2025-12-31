import json
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, insert, update, delete
from app.database import DATABASE_URL
from app.models import (
    College, ResearchRoom, Major, Clazz, User, TeacherProfile,
    Timetable, Role, UserRole
)
from app.core.auth import get_password_hash
from datetime import datetime

# 创建异步引擎和会话工厂
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# 星期映射
day_of_week_mapping = {
    "星期一": 1,
    "星期二": 2,
    "星期三": 3,
    "星期四": 4,
    "星期五": 5,
    "星期六": 6,
    "星期日": 7
}

async def init_db():
    """初始化数据库连接"""
    async with engine.begin() as conn:
        # 这里不需要创建表，因为FastAPI应用启动时会自动创建
        pass

async def import_college_research_room():
    """导入学院和教研室数据"""
    async with AsyncSessionLocal() as db:
        try:
            # 读取学院-教研室数据
            with open('data/College-ResearchRoom.json', 'r', encoding='utf-8') as f:
                college_data = json.load(f)
            
            for college_item in college_data['学院列表']:
                # 检查学院是否已存在
                stmt = select(College).where(College.college_code == college_item['学院编码'])
                result = await db.execute(stmt)
                college = result.scalar_one_or_none()
                
                if not college:
                    # 创建学院
                    college = College(
                        college_code=college_item['学院编码'],
                        college_name=college_item['学院名称']
                    )
                    db.add(college)
                    await db.flush()
                
                # 处理教研室
                for room_item in college_item['教研室列表']:
                    # 检查教研室是否已存在
                    stmt = select(ResearchRoom).where(
                        ResearchRoom.room_name == room_item['教研室名称'],
                        ResearchRoom.college_id == college.id
                    )
                    result = await db.execute(stmt)
                    existing_room = result.scalar_one_or_none()
                    
                    if not existing_room:
                        # 创建教研室
                        research_room = ResearchRoom(
                            room_name=room_item['教研室名称'],
                            college_id=college.id
                        )
                        db.add(research_room)
            
            await db.commit()
            print("学院和教研室数据导入完成")
        except Exception as e:
            await db.rollback()
            print(f"导入学院和教研室数据时出错: {e}")

async def import_teachers():
    """导入教师数据"""
    async with AsyncSessionLocal() as db:
        try:
            # 读取教师信息数据，创建姓名到教工号的映射以及教工号到所属单位的映射
            with open('data/teacher_info.json', 'r', encoding='utf-8') as f:
                teacher_info_data = json.load(f)
            
            # 创建映射
            name_to_employee_id = {}
            employee_id_to_college = {}
            name_to_college = {}
            for info in teacher_info_data:
                name_to_employee_id[info['姓名']] = info['教工号']
                employee_id_to_college[info['教工号']] = info['教师所属单位']
                name_to_college[info['姓名']] = info['教师所属单位']
            
            # 读取教师数据
            with open('data/teachers.json', 'r', encoding='utf-8') as f:
                teachers_data = json.load(f)
            
            for teacher_item in teachers_data:
                teacher_name = teacher_item['教师姓名']
                
                # 查找教工号
                employee_id = name_to_employee_id.get(teacher_name)
                if not employee_id:
                    print(f"警告: 未找到教师 {teacher_name} 的教工号，跳过导入")
                    continue
                
                # 查找所属学院
                college_name = name_to_college.get(teacher_name)
                college_id = None
                if college_name:
                    stmt = select(College).where(College.college_name == college_name)
                    result = await db.execute(stmt)
                    college = result.scalar_one_or_none()
                    if college:
                        college_id = college.id
                    else:
                        print(f"警告: 未找到学院 {college_name}，跳过设置学院id")
                
                # 检查教师是否已存在
                stmt = select(User).where(User.user_on == employee_id)
                result = await db.execute(stmt)
                existing_user = result.scalar_one_or_none()
                
                if not existing_user:
                    # 创建教师用户，包含学院id
                    hashed_password = get_password_hash("123456")
                    user = User(
                        user_on=employee_id,
                        user_name=teacher_name,
                        college_id=college_id,
                        password=hashed_password,
                        status=1
                    )
                    db.add(user)
                    await db.flush()
                    
                    # 分配teacher角色
                    # 获取teacher角色
                    stmt = select(Role).where(Role.role_code == "teacher")
                    result = await db.execute(stmt)
                    teacher_role = result.scalar_one_or_none()
                    
                    if teacher_role:
                        # 检查用户是否已经有这个角色
                        stmt = select(UserRole).where(
                            UserRole.user_id == user.id,
                            UserRole.role_id == teacher_role.id
                        )
                        result = await db.execute(stmt)
                        existing_user_role = result.scalar_one_or_none()
                        
                        if not existing_user_role:
                            # 分配角色
                            user_role = UserRole(user_id=user.id, role_id=teacher_role.id)
                            db.add(user_role)
                    
                    # 创建教师档案
                    for room_item in teacher_item['教研室']:
                        # 查找教研室
                        stmt = select(ResearchRoom).where(
                            ResearchRoom.room_name == room_item['名称']
                        )
                        result = await db.execute(stmt)
                        research_room = result.scalar_one_or_none()
                        
                        if research_room:
                            # 检查教师档案是否已存在
                            stmt = select(TeacherProfile).where(
                                TeacherProfile.user_id == user.id
                            )
                            result = await db.execute(stmt)
                            existing_profile = result.scalar_one_or_none()
                            
                            if not existing_profile:
                                # 创建教师档案
                                teacher_profile = TeacherProfile(
                                    user_id=user.id,
                                    research_room_id=research_room.id
                                )
                                db.add(teacher_profile)
                else:
                    # 如果教师已存在，更新学院id
                    if college_id and existing_user.college_id != college_id:
                        existing_user.college_id = college_id
                        print(f"更新教师 {teacher_name} 的学院id为 {college_id}")
                    
                    # 为已存在的用户也分配teacher角色
                    # 获取teacher角色
                    stmt = select(Role).where(Role.role_code == "teacher")
                    result = await db.execute(stmt)
                    teacher_role = result.scalar_one_or_none()
                    
                    if teacher_role:
                        # 检查用户是否已经有这个角色
                        stmt = select(UserRole).where(
                            UserRole.user_id == existing_user.id,
                            UserRole.role_id == teacher_role.id
                        )
                        result = await db.execute(stmt)
                        existing_user_role = result.scalar_one_or_none()
                        
                        if not existing_user_role:
                            # 分配角色
                            user_role = UserRole(user_id=existing_user.id, role_id=teacher_role.id)
                            db.add(user_role)
            
            await db.commit()
            print("教师数据导入完成")
        except Exception as e:
            await db.rollback()
            print(f"导入教师数据时出错: {e}")

async def import_timetable():
    """导入课表数据"""
    async with AsyncSessionLocal() as db:
        try:
            # 读取教师信息数据，创建姓名到教工号的映射
            with open('data/teacher_info.json', 'r', encoding='utf-8') as f:
                teacher_info_data = json.load(f)
            
            # 创建姓名到教工号的映射
            name_to_employee_id = {}
            for info in teacher_info_data:
                name_to_employee_id[info['姓名']] = info['教工号']
            
            # 读取课表数据
            with open('data/2025-2026-1.json', 'r', encoding='utf-8') as f:
                timetable_data = json.load(f)
            
            # 学期信息：2025-2026学年秋季学期
            academic_year = "2025-2026"
            semester = 2
            
            for course_item in timetable_data:
                # 查找学院
                stmt = select(College).where(College.college_name == course_item['学院'])
                result = await db.execute(stmt)
                college = result.scalar_one_or_none()
                
                if not college:
                    continue
                
                # 查找教师
                teacher_name = course_item['teacher']
                teacher = None
                
                # 首先通过姓名获取教工号，然后使用教工号精确查找
                employee_id = name_to_employee_id.get(teacher_name)
                if employee_id:
                    stmt = select(User).where(User.user_on == employee_id)
                    result = await db.execute(stmt)
                    teacher = result.scalar_one_or_none()
                
                # 如果教工号查找失败，才尝试通过姓名查找，处理可能的重名情况
                if not teacher:
                    stmt = select(User).where(User.user_name == teacher_name)
                    result = await db.execute(stmt)
                    users = result.scalars().all()
                    if len(users) == 1:
                        teacher = users[0]
                    elif len(users) > 1:
                        print(f"警告: 发现多个重名教师 {teacher_name}，请使用教工号查询，跳过导入此课表")
                        continue
                
                if not teacher:
                    print(f"警告: 未找到教师 {teacher_name}，跳过导入此课表")
                    continue
                
                # 查找或创建专业
                stmt = select(Major).where(
                    Major.major_name == course_item['专业'],
                    Major.college_id == college.id
                )
                result = await db.execute(stmt)
                major = result.scalar_one_or_none()
                
                if not major:
                    major = Major(
                        major_name=course_item['专业'],
                        college_id=college.id
                    )
                    db.add(major)
                    await db.flush()
                
                # 查找或创建班级
                stmt = select(Clazz).where(
                    Clazz.class_name == course_item['班级'],
                    Clazz.major_id == major.id
                )
                result = await db.execute(stmt)
                clazz = result.scalar_one_or_none()
                
                if not clazz:
                    clazz = Clazz(
                        class_name=course_item['班级'],
                        grade=course_item['年级'],
                        major_id=major.id
                    )
                    db.add(clazz)
                    await db.flush()
                
                # 检查课表是否已存在
                stmt = select(Timetable).where(
                    Timetable.academic_year == academic_year,
                    Timetable.semester == semester,
                    Timetable.teacher_id == teacher.id,
                    Timetable.class_name == course_item['班级'],
                    Timetable.course_name == course_item['course'],
                    Timetable.weekday == day_of_week_mapping[course_item['星期']],
                    Timetable.period == course_item['节次'],
                    Timetable.section_time == course_item['section_time'],
                    Timetable.week_info == course_item['week_info'],
                    Timetable.classroom == course_item['classroom']
                )
                result = await db.execute(stmt)
                existing_timetable = result.scalar_one_or_none()
                
                if not existing_timetable:
                    # 创建课表
                    timetable = Timetable(
                        college_id=college.id,
                        teacher_id=teacher.id,
                        class_id=clazz.id,
                        class_name=course_item['班级'],
                        course_code=course_item['class_code'],
                        course_name=course_item['course'],
                        academic_year=academic_year,
                        semester=semester,
                        weekday=day_of_week_mapping[course_item['星期']],
                        weekday_text=course_item['星期'],
                        period=course_item['节次'],
                        section_time=course_item['section_time'],
                        week_info=course_item['week_info'],
                        classroom=course_item['classroom']
                    )
                    db.add(timetable)
            
            await db.commit()
            print("课表数据导入完成")
        except Exception as e:
            await db.rollback()
            print(f"导入课表数据时出错: {e}")

async def main():
    """主函数"""
    print("开始导入数据...")
    await init_db()
    await import_college_research_room()
    await import_teachers()
    await import_timetable()
    print("所有数据导入完成")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
