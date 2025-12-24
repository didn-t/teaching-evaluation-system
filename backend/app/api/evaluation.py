from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

from app.models import College, PermissionDict, User, UserPermission, Timetable, TeachingEvaluation, TeacherEvaluationStat, CollegeEvaluationStat, SystemConfig
from app.schemas import CollegeResponse, CollegeCreate, PermissionDictResponse, PermissionDictCreate, UserNewResponse, UserNewCreate, UserPermissionResponse, UserPermissionCreate, TimetableResponse, TimetableCreate, TeachingEvaluationResponse, TeachingEvaluationCreate, TeacherEvaluationStatResponse, TeacherEvaluationStatCreate, CollegeEvaluationStatResponse, CollegeEvaluationStatCreate, SystemConfigResponse, SystemConfigCreate
from app.database import get_db

# 加载环境变量
load_dotenv()

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码Bearer模式
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# 1. 学院信息相关API
@router.get("/colleges/{college_id}", response_model=CollegeResponse)
async def get_college(college_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(College).where(College.id == college_id, College.is_delete == False))
    try:
        college = result.scalar_one()
        return college
    except NoResultFound:
        raise HTTPException(status_code=404, detail="College not found")

@router.post("/colleges", response_model=CollegeResponse)
async def create_college(college: CollegeCreate, db: AsyncSession = Depends(get_db)):
    # 检查学院编码是否已存在
    result = await db.execute(select(College).where(College.college_code == college.college_code))
    existing_college = result.scalar()
    if existing_college:
        raise HTTPException(status_code=400, detail="College code already exists")
    
    db_college = College(
        college_code=college.college_code,
        college_name=college.college_name
    )
    db.add(db_college)
    await db.commit()
    await db.refresh(db_college)
    return db_college

# 2. 权限字典相关API
@router.get("/permissions/{permission_id}", response_model=PermissionDictResponse)
async def get_permission(permission_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PermissionDict).where(PermissionDict.id == permission_id, PermissionDict.is_delete == False))
    try:
        permission = result.scalar_one()
        return permission
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Permission not found")

@router.post("/permissions", response_model=PermissionDictResponse)
async def create_permission(permission: PermissionDictCreate, db: AsyncSession = Depends(get_db)):
    # 检查权限编码是否已存在
    result = await db.execute(select(PermissionDict).where(PermissionDict.permission_code == permission.permission_code))
    existing_permission = result.scalar()
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission code already exists")
    
    db_permission = PermissionDict(
        permission_code=permission.permission_code,
        permission_name=permission.permission_name,
        permission_type=permission.permission_type,
        parent_id=permission.parent_id,
        sort=permission.sort
    )
    db.add(db_permission)
    await db.commit()
    await db.refresh(db_permission)
    return db_permission

# 3. 用户相关API
@router.get("/users/{user_id}", response_model=UserNewResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id, User.is_delete == False))
    try:
        user = result.scalar_one()
        return user
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/users", response_model=UserNewResponse)
async def create_user(user: UserNewCreate, db: AsyncSession = Depends(get_db)):
    # 检查用户工号是否已存在
    result = await db.execute(select(User).where(User.user_no == user.user_no))
    existing_user = result.scalar()
    if existing_user:
        raise HTTPException(status_code=400, detail="User number already exists")
    
    # 加密密码
    hashed_password = pwd_context.hash(user.password)
    
    db_user = User(
        user_no=user.user_no,
        user_name=user.user_name,
        role_type=user.role_type,
        college_id=user.college_id,
        password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# 4. 用户权限关联相关API
@router.get("/user-permissions/{id}", response_model=UserPermissionResponse)
async def get_user_permission(id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(UserPermission).where(UserPermission.id == id, UserPermission.is_delete == False))
    try:
        user_permission = result.scalar_one()
        return user_permission
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User permission association not found")

@router.post("/user-permissions", response_model=UserPermissionResponse)
async def create_user_permission(user_permission: UserPermissionCreate, db: AsyncSession = Depends(get_db)):
    # 检查用户权限关联是否已存在
    result = await db.execute(
        select(UserPermission).where(
            UserPermission.user_id == user_permission.user_id,
            UserPermission.permission_id == user_permission.permission_id
        )
    )
    existing_association = result.scalar()
    if existing_association:
        raise HTTPException(status_code=400, detail="User permission association already exists")
    
    db_user_permission = UserPermission(
        user_id=user_permission.user_id,
        permission_id=user_permission.permission_id,
        scope_college_ids=user_permission.scope_college_ids,
        operator_id=user_permission.operator_id
    )
    db.add(db_user_permission)
    await db.commit()
    await db.refresh(db_user_permission)
    return db_user_permission

# 5. 课表相关API
@router.get("/timetables/{timetable_id}", response_model=TimetableResponse)
async def get_timetable(timetable_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Timetable).where(Timetable.id == timetable_id, Timetable.is_delete == False))
    try:
        timetable = result.scalar_one()
        return timetable
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Timetable not found")

@router.post("/timetables", response_model=TimetableResponse)
async def create_timetable(timetable: TimetableCreate, db: AsyncSession = Depends(get_db)):
    # 检查课表编号是否已存在
    result = await db.execute(select(Timetable).where(Timetable.timetable_no == timetable.timetable_no))
    existing_timetable = result.scalar()
    if existing_timetable:
        raise HTTPException(status_code=400, detail="Timetable number already exists")
    
    db_timetable = Timetable(
        timetable_no=timetable.timetable_no,
        college_id=timetable.college_id,
        teacher_id=timetable.teacher_id,
        course_name=timetable.course_name,
        course_type=timetable.course_type,
        class_name=timetable.class_name,
        teach_week=timetable.teach_week,
        teach_time=timetable.teach_time,
        teach_place=timetable.teach_place,
        sync_time=timetable.sync_time
    )
    db.add(db_timetable)
    await db.commit()
    await db.refresh(db_timetable)
    return db_timetable

# 6. 评教相关API
@router.get("/evaluations/{evaluation_id}", response_model=TeachingEvaluationResponse)
async def get_evaluation(evaluation_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeachingEvaluation).where(TeachingEvaluation.id == evaluation_id, TeachingEvaluation.is_delete == False))
    try:
        evaluation = result.scalar_one()
        return evaluation
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Evaluation not found")

@router.post("/evaluations", response_model=TeachingEvaluationResponse)
async def create_evaluation(evaluation: TeachingEvaluationCreate, db: AsyncSession = Depends(get_db)):
    # 检查评教编号是否已存在
    result = await db.execute(select(TeachingEvaluation).where(TeachingEvaluation.evaluation_no == evaluation.evaluation_no))
    existing_evaluation = result.scalar()
    if existing_evaluation:
        raise HTTPException(status_code=400, detail="Evaluation number already exists")
    
    db_evaluation = TeachingEvaluation(
        evaluation_no=evaluation.evaluation_no,
        timetable_id=evaluation.timetable_id,
        teach_teacher_id=evaluation.teach_teacher_id,
        listen_teacher_id=evaluation.listen_teacher_id,
        total_score=evaluation.total_score,
        dimension_scores=evaluation.dimension_scores,
        advantage_content=evaluation.advantage_content,
        problem_content=evaluation.problem_content,
        improve_suggestion=evaluation.improve_suggestion,
        is_anonymous=evaluation.is_anonymous,
        submit_time=evaluation.submit_time
    )
    db.add(db_evaluation)
    await db.commit()
    await db.refresh(db_evaluation)
    return db_evaluation

# 7. 教师评教统计相关API
@router.get("/teacher-stats/{stat_id}", response_model=TeacherEvaluationStatResponse)
async def get_teacher_stat(stat_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TeacherEvaluationStat).where(TeacherEvaluationStat.id == stat_id))
    try:
        teacher_stat = result.scalar_one()
        return teacher_stat
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Teacher statistics not found")

@router.post("/teacher-stats", response_model=TeacherEvaluationStatResponse)
async def create_teacher_stat(teacher_stat: TeacherEvaluationStatCreate, db: AsyncSession = Depends(get_db)):
    # 检查是否已存在该教师在该年份学期的统计
    result = await db.execute(
        select(TeacherEvaluationStat).where(
            TeacherEvaluationStat.teacher_id == teacher_stat.teacher_id,
            TeacherEvaluationStat.stat_year == teacher_stat.stat_year,
            TeacherEvaluationStat.stat_semester == teacher_stat.stat_semester
        )
    )
    existing_stat = result.scalar()
    if existing_stat:
        raise HTTPException(status_code=400, detail="Teacher statistics for this year and semester already exist")
    
    db_teacher_stat = TeacherEvaluationStat(
        teacher_id=teacher_stat.teacher_id,
        college_id=teacher_stat.college_id,
        stat_year=teacher_stat.stat_year,
        stat_semester=teacher_stat.stat_semester,
        total_evaluation_num=teacher_stat.total_evaluation_num,
        avg_total_score=teacher_stat.avg_total_score,
        dimension_avg_scores=teacher_stat.dimension_avg_scores,
        school_rank=teacher_stat.school_rank,
        college_rank=teacher_stat.college_rank,
        high_freq_problems=teacher_stat.high_freq_problems,
        high_freq_suggestions=teacher_stat.high_freq_suggestions
    )
    db.add(db_teacher_stat)
    await db.commit()
    await db.refresh(db_teacher_stat)
    return db_teacher_stat

# 8. 学院评教统计相关API
@router.get("/college-stats/{stat_id}", response_model=CollegeEvaluationStatResponse)
async def get_college_stat(stat_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CollegeEvaluationStat).where(CollegeEvaluationStat.id == stat_id))
    try:
        college_stat = result.scalar_one()
        return college_stat
    except NoResultFound:
        raise HTTPException(status_code=404, detail="College statistics not found")

@router.post("/college-stats", response_model=CollegeEvaluationStatResponse)
async def create_college_stat(college_stat: CollegeEvaluationStatCreate, db: AsyncSession = Depends(get_db)):
    # 检查是否已存在该学院在该年份学期的统计
    result = await db.execute(
        select(CollegeEvaluationStat).where(
            CollegeEvaluationStat.college_id == college_stat.college_id,
            CollegeEvaluationStat.stat_year == college_stat.stat_year,
            CollegeEvaluationStat.stat_semester == college_stat.stat_semester
        )
    )
    existing_stat = result.scalar()
    if existing_stat:
        raise HTTPException(status_code=400, detail="College statistics for this year and semester already exist")
    
    db_college_stat = CollegeEvaluationStat(
        college_id=college_stat.college_id,
        stat_year=college_stat.stat_year,
        stat_semester=college_stat.stat_semester,
        total_teacher_num=college_stat.total_teacher_num,
        avg_total_score=college_stat.avg_total_score,
        dimension_avg_scores=college_stat.dimension_avg_scores,
        school_rank=college_stat.school_rank,
        high_freq_problems=college_stat.high_freq_problems,
        report_export_num=college_stat.report_export_num
    )
    db.add(db_college_stat)
    await db.commit()
    await db.refresh(db_college_stat)
    return db_college_stat

# 9. 系统配置相关API
@router.get("/system-configs/{config_id}", response_model=SystemConfigResponse)
async def get_system_config(config_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemConfig).where(SystemConfig.id == config_id))
    try:
        system_config = result.scalar_one()
        return system_config
    except NoResultFound:
        raise HTTPException(status_code=404, detail="System configuration not found")

@router.post("/system-configs", response_model=SystemConfigResponse)
async def create_system_config(config: SystemConfigCreate, db: AsyncSession = Depends(get_db)):
    # 检查配置键是否已存在
    result = await db.execute(select(SystemConfig).where(SystemConfig.config_key == config.config_key))
    existing_config = result.scalar()
    if existing_config:
        raise HTTPException(status_code=400, detail="Configuration key already exists")
    
    db_system_config = SystemConfig(
        config_key=config.config_key,
        config_value=config.config_value,
        config_desc=config.config_desc,
        operator_id=config.operator_id
    )
    db.add(db_system_config)
    await db.commit()
    await db.refresh(db_system_config)
    return db_system_config