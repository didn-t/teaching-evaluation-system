from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any

from app.database import get_db
from app.schemas import BaseResponse, TokenData
from app.core.deps import require_access
from app.models import SystemConfig

router = APIRouter(prefix="/config", tags=["系统配置"])


@router.get("/", summary="获取系统配置")
async def get_system_config(
    config_keys: Optional[str] = Query(None, description="配置键，多个用逗号分隔，为空则获取所有配置"),
    current_user: TokenData = Depends(
        require_access(
            roles_any=("college_admin", "school_admin"),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    获取系统配置
    - config_keys: 配置键，多个用逗号分隔，为空则获取所有配置
    - 学校管理员和学院管理员可查看配置
    """
    from sqlalchemy import select
    
    if config_keys:
        keys = [key.strip() for key in config_keys.split(",") if key.strip()]
        stmt = select(SystemConfig).where(SystemConfig.config_key.in_(keys))
    else:
        stmt = select(SystemConfig)
    
    configs = await db.execute(stmt)
    config_list = configs.scalars().all()
    
    # 格式化输出
    result = {}
    for config in config_list:
        result[config.config_key] = {
            "value": config.config_value,
            "type": config.config_type,
            "desc": config.config_desc,
            "is_public": config.is_public
        }
    
    return BaseResponse(code=200, msg="success", data=result)


@router.post("/", summary="设置系统配置")
async def set_system_config(
    config_key: str,
    config_value: Any = Body(...),
    config_type: str = "string",
    config_desc: str = "",
    is_public: bool = False,
    current_user: TokenData = Depends(
        require_access(
            roles_any=("school_admin"),
            perms_all=("system:config",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    设置系统配置
    - config_key: 配置键
    - config_value: 配置值
    - config_type: 配置类型（string/number/boolean/json）
    - config_desc: 配置描述
    - is_public: 是否前端可见
    - 仅学校管理员可设置配置
    """
    from sqlalchemy import select, and_
    
    # 检查配置是否已存在
    stmt = select(SystemConfig).where(SystemConfig.config_key == config_key)
    existing_config = await db.execute(stmt)
    existing_config = existing_config.scalar_one_or_none()
    
    if existing_config:
        # 更新现有配置
        existing_config.config_value = config_value
        existing_config.config_type = config_type
        existing_config.config_desc = config_desc
        existing_config.is_public = is_public
        existing_config.operator_id = current_user.id
        await db.commit()
        await db.refresh(existing_config)
    else:
        # 创建新配置
        new_config = SystemConfig(
            config_key=config_key,
            config_value=config_value,
            config_type=config_type,
            config_desc=config_desc,
            is_public=is_public,
            operator_id=current_user.id
        )
        db.add(new_config)
        await db.commit()
        await db.refresh(new_config)
    
    return BaseResponse(code=200, msg="success", data=None)


@router.delete("/{config_key}", summary="删除系统配置")
async def delete_system_config(
    config_key: str,
    current_user: TokenData = Depends(
        require_access(
            roles_any=("school_admin"),
            perms_all=("system:config",),
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    删除系统配置
    - config_key: 配置键
    - 仅学校管理员可删除配置
    """
    from sqlalchemy import select
    
    stmt = select(SystemConfig).where(SystemConfig.config_key == config_key)
    config = await db.execute(stmt)
    config = config.scalar_one_or_none()
    
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    await db.delete(config)
    await db.commit()
    
    return BaseResponse(code=200, msg="success", data=None)


@router.get("/current-term", summary="获取当前学年学期")
async def get_current_term(
    db: AsyncSession = Depends(get_db),
):
    """
    获取当前学年学期配置
    - 所有用户均可访问
    """
    from sqlalchemy import select
    
    # 22300417陈俫坤开发：课表周次/日期映射由学校管理员配置学期起始日期；前端通过本接口获取
    # - term_start_date: 学期第1周周一日期（YYYY-MM-DD）
    # - total_weeks: 总周数（可选，默认20）
    keys = [
        "current_academic_year",
        "current_semester",
        "term_start_date",
        "total_weeks",
    ]
    stmt = select(SystemConfig).where(SystemConfig.config_key.in_(keys))
    configs = await db.execute(stmt)
    config_list = configs.scalars().all()
    
    result = {
        "academic_year": None,
        "semester": None,
        "term_start_date": None,
        "total_weeks": None,
    }
    
    for config in config_list:
        if config.config_key == "current_academic_year":
            result["academic_year"] = config.config_value
        elif config.config_key == "current_semester":
            result["semester"] = config.config_value
        elif config.config_key == "term_start_date":
            result["term_start_date"] = config.config_value
        elif config.config_key == "total_weeks":
            result["total_weeks"] = config.config_value
    
    return BaseResponse(code=200, msg="success", data=result)


@router.get("/evaluation-mode", summary="获取评教模式配置")
async def get_evaluation_mode(
    db: AsyncSession = Depends(get_db),
):
    """
    获取评教模式配置
    - 所有用户均可访问
    """
    from sqlalchemy import select
    
    stmt = select(SystemConfig).where(SystemConfig.config_key == "evaluation_anonymous_mode")
    config = await db.execute(stmt)
    config = config.scalar_one_or_none()
    
    # 默认值：1-统一匿名 2-统一实名 3-用户自主选择
    mode = config.config_value if config else 1
    
    return BaseResponse(code=200, msg="success", data={
        "mode": mode,
        "description": {
            1: "统一匿名",
            2: "统一实名",
            3: "用户自主选择"
        }[mode]
    })
