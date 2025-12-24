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
from app.schemas import CollegeResponse, CollegeCreate, PermissionDictResponse, PermissionDictCreate, UserNewResponse as UserResponse, UserNewCreate as UserCreate, UserPermissionResponse, UserPermissionCreate, TimetableResponse, TimetableCreate, TeachingEvaluationResponse, TeachingEvaluationCreate, TeacherEvaluationStatResponse, TeacherEvaluationStatCreate, CollegeEvaluationStatResponse, CollegeEvaluationStatCreate, SystemConfigResponse, SystemConfigCreate
from app.database import get_db

# 加载环境变量
load_dotenv()

router = APIRouter()



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