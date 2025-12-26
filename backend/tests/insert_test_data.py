#!/usr/bin/env python3
"""
一键插入测试数据脚本
用于教学评价系统后端的数据库测试数据初始化
"""
import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models import (
    Base, User, College, Timetable, EvaluationDimension, 
    TeachingEvaluation, Role, Permission, UserRole, RolePermission,
    TeacherEvaluationStat, CollegeEvaluationStat
)
from app.core.config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB
from passlib.context import CryptContext

# 创建数据库引擎
DATABASE_URL = f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

import bcrypt

def get_password_hash(password: str):
    """生成密码哈希，与项目中的auth.py保持一致"""
    # 密码需要编码为 bytes，且不能超过 72 字节
    password_bytes = password.encode('utf-8')[:72]
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码，与项目中的auth.py保持一致"""
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

async def create_colleges(db: AsyncSession):
    """创建学院测试数据"""
    print("正在插入学院数据...")
    
    college_data = [
        {"college_code": "CS", "college_name": "计算机科学与技术学院", "short_name": "计算机学院"},
        {"college_code": "EE", "college_name": "电子信息工程学院", "short_name": "电子学院"},
        {"college_code": "ME", "college_name": "机械工程学院", "short_name": "机械学院"},
        {"college_code": "MATH", "college_name": "数学与应用数学学院", "short_name": "数学院"},
        {"college_code": "ENG", "college_name": "英语学院", "short_name": "外语学院"},
        {"college_code": "PHY", "college_name": "物理学院", "short_name": "物理学院"},
    ]
    
    for college_info in college_data:
        existing = await db.execute(
            select(College).where(College.college_code == college_info["college_code"])
        )
        if not existing.scalar():
            college = College(**college_info)
            db.add(college)
    
    await db.commit()
    print("学院数据插入完成")


async def create_permissions(db: AsyncSession):
    """创建权限测试数据"""
    print("正在插入权限数据...")
    
    permissions_data = [
        {"permission_code": "user:read", "permission_name": "查看用户", "permission_type": 1},
        {"permission_code": "user:create", "permission_name": "创建用户", "permission_type": 2},
        {"permission_code": "user:update", "permission_name": "修改用户", "permission_type": 2},
        {"permission_code": "user:delete", "permission_name": "删除用户", "permission_type": 2},
        {"permission_code": "evaluation:read", "permission_name": "查看评价", "permission_type": 1},
        {"permission_code": "evaluation:create", "permission_name": "创建评价", "permission_type": 2},
        {"permission_code": "evaluation:update", "permission_name": "修改评价", "permission_type": 2},
        {"permission_code": "evaluation:export", "permission_name": "导出评价", "permission_type": 3},
        {"permission_code": "stat:read", "permission_name": "查看统计", "permission_type": 1},
        {"permission_code": "admin:config", "permission_name": "系统配置", "permission_type": 4},
    ]
    
    for perm_info in permissions_data:
        existing = await db.execute(
            select(Permission).where(Permission.permission_code == perm_info["permission_code"])
        )
        if not existing.scalar():
            permission = Permission(**perm_info)
            db.add(permission)
    
    await db.commit()
    print("权限数据插入完成")


async def create_roles(db: AsyncSession):
    """创建角色测试数据"""
    print("正在插入角色数据...")
    
    roles_data = [
        {"role_code": "admin", "role_name": "管理员", "description": "系统管理员角色"},
        {"role_code": "teacher", "role_name": "教师", "description": "普通教师角色"},
        {"role_code": "department_head", "role_name": "系主任", "description": "系主任角色"},
        {"role_code": "college_admin", "role_name": "学院管理员", "description": "学院管理员角色"},
    ]
    
    for role_info in roles_data:
        existing = await db.execute(
            select(Role).where(Role.role_code == role_info["role_code"])
        )
        if not existing.scalar():
            role = Role(**role_info)
            db.add(role)
    
    await db.commit()
    print("角色数据插入完成")


async def create_users(db: AsyncSession):
    """创建用户测试数据"""
    print("正在插入用户数据...")
    
    # 获取学院ID
    colleges = (await db.execute(select(College))).scalars().all()
    if not colleges:
        print("请先插入学院数据")
        return
    
    # 获取角色ID
    roles = (await db.execute(select(Role))).scalars().all()
    if not roles:
        print("请先插入角色数据")
        return
    
    pass  # 使用全局定义的 get_password_hash 函数
    
    users_data = [
        {
            "user_on": "admin001",
            "user_name": "系统管理员",
            "college_id": colleges[0].id if colleges else None,
            "password": get_password_hash("admin123"),
            "status": 1
        },
        {
            "user_on": "teacher001",
            "user_name": "张教授",
            "college_id": colleges[0].id if colleges else None,
            "password": get_password_hash("teacher123"),
            "status": 1
        },
        {
            "user_on": "teacher002",
            "user_name": "李副教授",
            "college_id": colleges[1].id if len(colleges) > 1 else None,
            "password": get_password_hash("teacher123"),
            "status": 1
        },
        {
            "user_on": "teacher003",
            "user_name": "王讲师",
            "college_id": colleges[2].id if len(colleges) > 2 else None,
            "password": get_password_hash("teacher123"),
            "status": 1
        },
        {
            "user_on": "teacher004",
            "user_name": "赵主任",
            "college_id": colleges[0].id if colleges else None,
            "password": get_password_hash("teacher123"),
            "status": 1
        },
        {
            "user_on": "teacher005",
            "user_name": "孙老师",
            "college_id": colleges[3].id if len(colleges) > 3 else None,
            "password": get_password_hash("teacher123"),
            "status": 1
        },
    ]
    
    for user_info in users_data:
        existing = await db.execute(
            select(User).where(User.user_on == user_info["user_on"])
        )
        if not existing.scalar():
            user = User(**user_info)
            db.add(user)
    
    await db.commit()
    print("用户数据插入完成")


async def create_user_roles(db: AsyncSession):
    """创建用户角色关联数据"""
    print("正在插入用户角色关联数据...")
    
    # 获取用户和角色
    users = (await db.execute(select(User))).scalars().all()
    roles = (await db.execute(select(Role))).scalars().all()
    
    if not users or not roles:
        print("请先插入用户和角色数据")
        return
    
    # 管理员用户分配管理员角色
    admin_user = next((u for u in users if u.user_on == "admin001"), None)
    admin_role = next((r for r in roles if r.role_code == "admin"), None)
    if admin_user and admin_role:
        user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
        existing = await db.execute(
            select(UserRole).where(
                UserRole.user_id == admin_user.id,
                UserRole.role_id == admin_role.id
            )
        )
        if not existing.scalar():
            db.add(user_role)
    
    # 其他用户分配教师角色
    teacher_role = next((r for r in roles if r.role_code == "teacher"), None)
    if teacher_role:
        for user in users[1:]:  # 除了admin用户
            existing = await db.execute(
                select(UserRole).where(
                    UserRole.user_id == user.id,
                    UserRole.role_id == teacher_role.id
                )
            )
            if not existing.scalar():
                user_role = UserRole(user_id=user.id, role_id=teacher_role.id)
                db.add(user_role)
    
    await db.commit()
    print("用户角色关联数据插入完成")


async def create_evaluation_dimensions(db: AsyncSession):
    """创建评价维度数据"""
    print("正在插入评价维度数据...")
    
    dimensions_data = [
        {
            "dimension_code": "teaching_content",
            "dimension_name": "教学内容",
            "max_score": 20,
            "weight": 0.25,
            "sort_order": 1,
            "description": "教学内容的完整性和准确性",
            "is_required": True,
            "status": 1
        },
        {
            "dimension_code": "teaching_method",
            "dimension_name": "教学方法",
            "max_score": 20,
            "weight": 0.25,
            "sort_order": 2,
            "description": "教学方法的适用性和创新性",
            "is_required": True,
            "status": 1
        },
        {
            "dimension_code": "class_management",
            "dimension_name": "课堂管理",
            "max_score": 20,
            "weight": 0.20,
            "sort_order": 3,
            "description": "课堂秩序和氛围管理",
            "is_required": True,
            "status": 1
        },
        {
            "dimension_code": "student_engagement",
            "dimension_name": "学生参与度",
            "max_score": 20,
            "weight": 0.20,
            "sort_order": 4,
            "description": "学生学习积极性和参与度",
            "is_required": True,
            "status": 1
        },
        {
            "dimension_code": "teaching_effect",
            "dimension_name": "教学效果",
            "max_score": 20,
            "weight": 0.10,
            "sort_order": 5,
            "description": "教学目标达成情况",
            "is_required": True,
            "status": 1
        }
    ]
    
    for dim_info in dimensions_data:
        existing = await db.execute(
            select(EvaluationDimension).where(
                EvaluationDimension.dimension_code == dim_info["dimension_code"]
            )
        )
        if not existing.scalar():
            dimension = EvaluationDimension(**dim_info)
            db.add(dimension)
    
    await db.commit()
    print("评价维度数据插入完成")


async def create_timetables(db: AsyncSession):
    """创建课表数据"""
    print("正在插入课表数据...")
    
    # 获取用户和学院
    users = (await db.execute(select(User))).scalars().all()
    colleges = (await db.execute(select(College))).scalars().all()
    
    if not users or not colleges:
        print("请先插入用户和学院数据")
        return
    
    # 找到教师用户
    teacher_users = [u for u in users if u.user_on.startswith("teacher")]
    
    timetables_data = []
    for i, teacher in enumerate(teacher_users[:4]):  # 选择前4个教师
        for j in range(2):  # 每个教师2门课
            timetable_info = {
                "timetable_no": f"TT{i+1:02d}{j+1}",
                "college_id": teacher.college_id,
                "teacher_id": teacher.id,
                "course_code": f"COURSE{i+1:02d}{j+1}",
                "course_name": f"课程{i+1:02d}{j+1}名称",
                "course_type": "必修课" if j % 2 == 0 else "选修课",
                "class_name": f"班级{i+1:02d}{j+1}",
                "student_count": 30 + i * 5,
                "credit": 3.0,
                "academic_year": "2024-2025",
                "semester": 1,  # 春季
                "teach_week_start": 1,
                "teach_week_end": 16,
                "weekday": (i + j) % 5 + 1,  # 1-5 星期一到星期五
                "period_start": 1 + (j * 2) % 4,  # 1, 3 节开始
                "period_end": 2 + (j * 2) % 4,   # 2, 4 节结束
                "teach_week": "1-16周",
                "teach_time": f"周{(i + j) % 5 + 1}第{1 + (j * 2) % 4}-{2 + (j * 2) % 4}节",
                "teach_place": f"教学楼{(i + j) % 3 + 1}-{(i + j) * 2 + 1:03d}",
                "sync_time": datetime.now() - timedelta(days=30),
                "sync_status": 1
            }
            timetables_data.append(timetable_info)
    
    for timetable_info in timetables_data:
        existing = await db.execute(
            select(Timetable).where(Timetable.timetable_no == timetable_info["timetable_no"])
        )
        if not existing.scalar():
            timetable = Timetable(**timetable_info)
            db.add(timetable)
    
    await db.commit()
    print("课表数据插入完成")


async def create_teaching_evaluations(db: AsyncSession):
    """创建教学评价数据"""
    print("正在插入教学评价数据...")
    
    # 获取数据
    users = (await db.execute(select(User))).scalars().all()
    timetables = (await db.execute(select(Timetable))).scalars().all()
    dimensions = (await db.execute(select(EvaluationDimension))).scalars().all()
    
    if not users or not timetables or not dimensions:
        print("请先插入用户、课表和评价维度数据")
        return
    
    # 选择评价教师和被评价教师
    eval_users = [u for u in users if u.user_on.startswith("teacher")]
    
    evaluations_data = []
    for i, timetable in enumerate(timetables[:8]):  # 选择前8个课表
        # 选择评价教师（不与授课教师重复）
        listen_teacher = next(
            (u for u in eval_users if u.id != timetable.teacher_id), 
            eval_users[0]  # 如果没有其他教师，则使用第一个
        )
        
        # 生成维度评分
        dimension_scores = {}
        total_score = 0
        for dim in dimensions:
            score = 16 + (i % 4) * 2  # 16-22分
            dimension_scores[dim.dimension_code] = score
            total_score += score * float(dim.weight)
        
        # 计算等级
        if total_score >= 90:
            score_level = "优秀"
        elif total_score >= 80:
            score_level = "良好"
        elif total_score >= 60:
            score_level = "合格"
        else:
            score_level = "不合格"
        
        eval_info = {
            "evaluation_no": f"EVAL{i+1:04d}",
            "timetable_id": timetable.id,
            "teach_teacher_id": timetable.teacher_id,
            "listen_teacher_id": listen_teacher.id,
            "total_score": int(total_score),
            "dimension_scores": dimension_scores,
            "score_level": score_level,
            "advantage_content": f"这堂课的优点是教学内容丰富，教学方法得当，学生参与度高。",
            "problem_content": f"课堂管理方面还有提升空间，部分内容讲解可以更加详细。",
            "improve_suggestion": f"建议增加更多互动环节，进一步提升教学效果。",
            "listen_date": datetime.now() - timedelta(days=i),
            "listen_duration": 45 + (i % 3) * 15,  # 45, 60, 75分钟
            "listen_location": timetable.teach_place,
            "status": 1,
            "submit_time": datetime.now() - timedelta(days=i, hours=2)
        }
        evaluations_data.append(eval_info)
    
    for eval_info in evaluations_data:
        existing = await db.execute(
            select(TeachingEvaluation).where(
                TeachingEvaluation.evaluation_no == eval_info["evaluation_no"]
            )
        )
        if not existing.scalar():
            evaluation = TeachingEvaluation(**eval_info)
            db.add(evaluation)
    
    await db.commit()
    print("教学评价数据插入完成")


async def create_statistics(db: AsyncSession):
    """创建统计数据"""
    print("正在插入统计数据...")
    
    # 获取数据
    users = (await db.execute(select(User))).scalars().all()
    colleges = (await db.execute(select(College))).scalars().all()
    
    if not users or not colleges:
        print("请先插入用户和学院数据")
        return
    
    # 教师统计
    teacher_users = [u for u in users if u.user_on.startswith("teacher")]
    for i, teacher in enumerate(teacher_users[:3]):
        stat_info = {
            "teacher_id": teacher.id,
            "college_id": teacher.college_id,
            "stat_year": "2024-2025",
            "stat_semester": 1,
            "total_evaluation_num": 5 + i,
            "avg_total_score": 85.0 + i * 2.5,
            "max_score": 95 - i * 2,
            "min_score": 75 + i * 2,
            "dimension_avg_scores": {
                "teaching_content": 17.5 + i * 0.5,
                "teaching_method": 17.0 + i * 0.5,
                "class_management": 16.5 + i * 0.5,
                "student_engagement": 17.0 + i * 0.5,
                "teaching_effect": 16.0 + i * 0.5
            },
            "school_rank": i + 1,
            "school_total": len(teacher_users),
            "college_rank": i + 1,
            "college_total": sum(1 for t in teacher_users if t.college_id == teacher.college_id),
            "high_freq_problems": ["课堂互动不够", "教学节奏偏快"] if i % 2 == 0 else ["内容深度不够"],
            "high_freq_suggestions": ["增加案例分析", "加强课堂互动"] if i % 2 == 0 else ["增加实践环节"],
            "score_distribution": {"优秀": 2, "良好": 2, "合格": 1, "不合格": 0} if i % 2 == 0 else {"优秀": 1, "良好": 3, "合格": 1, "不合格": 0}
        }
        
        existing = await db.execute(
            select(TeacherEvaluationStat).where(
                TeacherEvaluationStat.teacher_id == teacher.id,
                TeacherEvaluationStat.stat_year == "2024-2025",
                TeacherEvaluationStat.stat_semester == 1
            )
        )
        if not existing.scalar():
            stat = TeacherEvaluationStat(**stat_info)
            db.add(stat)
    
    # 学院统计
    for i, college in enumerate(colleges[:3]):
        stat_info = {
            "college_id": college.id,
            "stat_year": "2024-2025",
            "stat_semester": 1,
            "total_teacher_num": 10 + i * 2,
            "total_evaluation_num": 50 + i * 10,
            "avg_total_score": 83.0 + i * 1.5,
            "dimension_avg_scores": {
                "teaching_content": 16.5 + i * 0.5,
                "teaching_method": 16.0 + i * 0.5,
                "class_management": 15.5 + i * 0.5,
                "student_engagement": 16.0 + i * 0.5,
                "teaching_effect": 15.0 + i * 0.5
            },
            "school_rank": i + 1,
            "school_total": len(colleges),
            "high_freq_problems": ["教学方法创新不足", "课堂管理待提升"] if i % 2 == 0 else ["理论与实践结合不够"],
            "score_distribution": {"优秀": 15, "良好": 20, "合格": 10, "不合格": 5} if i % 2 == 0 else {"优秀": 10, "良好": 25, "合格": 12, "不合格": 3},
            "excellent_rate": 0.30 + i * 0.05
        }
        
        existing = await db.execute(
            select(CollegeEvaluationStat).where(
                CollegeEvaluationStat.college_id == college.id,
                CollegeEvaluationStat.stat_year == "2024-2025",
                CollegeEvaluationStat.stat_semester == 1
            )
        )
        if not existing.scalar():
            stat = CollegeEvaluationStat(**stat_info)
            db.add(stat)
    
    await db.commit()
    print("统计数据插入完成")


async def main():
    """主函数，按顺序插入所有测试数据"""
    print("开始插入测试数据...")
    
    async with AsyncSessionLocal() as db:
        # 按依赖关系顺序插入数据
        await create_colleges(db)
        await create_permissions(db)
        await create_roles(db)
        await create_users(db)
        await create_user_roles(db)
        await create_evaluation_dimensions(db)
        await create_timetables(db)
        await create_teaching_evaluations(db)
        await create_statistics(db)
    
    print("所有测试数据插入完成！")


if __name__ == "__main__":
    asyncio.run(main())