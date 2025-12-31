#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限初始化脚本：创建预定义角色和权限
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.base import Base
from app.models import Permission, Role, RolePermission, User, UserRole
from app.database import DATABASE_URL
from app.core.auth import get_password_hash


async def init_permissions():
    """初始化权限和角色"""
    # 创建异步引擎
    engine = create_async_engine(
        DATABASE_URL, 
        echo=True, 
        future=True
    )
    
    # 创建会话工厂
    AsyncSessionLocal = sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # ==========================
            # 1. 获取或创建权限
            # ==========================
            permissions = [
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
                
                # 统计数据
                {"permission_code": "statistics:view:college_public", "permission_name": "查看本院公开统计数据", "permission_type": 1, "parent_id": None, "sort_order": 20},
                {"permission_code": "statistics:view:college_detail", "permission_name": "查看学院详细统计数据", "permission_type": 1, "parent_id": None, "sort_order": 21},
                {"permission_code": "statistics:view:all", "permission_name": "查看全校统计数据", "permission_type": 1, "parent_id": None, "sort_order": 22},
                
                # 用户管理
                {"permission_code": "user:manage:college", "permission_name": "维护本院用户账号", "permission_type": 2, "parent_id": None, "sort_order": 30},
                {"permission_code": "user:manage:all", "permission_name": "管理所有用户账号", "permission_type": 2, "parent_id": None, "sort_order": 31},
                
                # 角色权限管理
                {"permission_code": "role:manage", "permission_name": "管理角色", "permission_type": 2, "parent_id": None, "sort_order": 40},
                {"permission_code": "permission:manage", "permission_name": "管理权限", "permission_type": 2, "parent_id": None, "sort_order": 41},
                
                # 系统配置
                {"permission_code": "system:config", "permission_name": "系统参数配置", "permission_type": 4, "parent_id": None, "sort_order": 50},
                {"permission_code": "system:backup", "permission_name": "数据备份与维护", "permission_type": 4, "parent_id": None, "sort_order": 51},
                {"permission_code": "system:mode", "permission_name": "配置评教模式", "permission_type": 4, "parent_id": None, "sort_order": 52},
            ]
            
            # 获取或创建权限
            permission_objects = {}
            for perm_data in permissions:
                # 检查权限是否已存在
                stmt = select(Permission).where(Permission.permission_code == perm_data["permission_code"])
                result = await session.execute(stmt)
                existing_perm = result.scalar_one_or_none()
                
                if existing_perm:
                    permission_objects[perm_data["permission_code"]] = existing_perm
                else:
                    permission = Permission(**perm_data)
                    session.add(permission)
                    permission_objects[perm_data["permission_code"]] = permission
            
            # 刷新会话以获取权限ID
            await session.flush()
            
            # ==========================
            # 2. 获取或创建角色
            # ==========================
            roles = [
                {"role_code": "teacher", "role_name": "老师", "role_level": 1, "description": "普通教师角色", "status": 1},
                {"role_code": "supervisor", "role_name": "督导老师", "role_level": 2, "description": "督导教师角色", "status": 1},
                {"role_code": "college_admin", "role_name": "学院管理员", "role_level": 3, "description": "学院管理员角色", "status": 1},
                {"role_code": "school_admin", "role_name": "学校管理员", "role_level": 4, "description": "学校管理员角色", "status": 1},
            ]
            
            # 获取或创建角色
            role_objects = {}
            for role_data in roles:
                # 检查角色是否已存在
                stmt = select(Role).where(Role.role_code == role_data["role_code"])
                result = await session.execute(stmt)
                existing_role = result.scalar_one_or_none()
                
                if existing_role:
                    # 更新已存在角色的名称
                    existing_role.role_name = role_data["role_name"]
                    role_objects[role_data["role_code"]] = existing_role
                else:
                    role = Role(**role_data)
                    session.add(role)
                    role_objects[role_data["role_code"]] = role
            
            # 刷新会话以获取角色ID
            await session.flush()
            
            # ==========================
            # 3. 分配权限给角色
            # ==========================
            role_permissions = {
                "teacher": [
                    "timetable:view:self",
                    "evaluation:submit",
                    "evaluation:view:self",
                    "statistics:view:college_public",
                ],
                "supervisor": [
                    "timetable:view:college",
                    "evaluation:submit",
                    "evaluation:view:college",
                    "statistics:view:college_detail",
                    "evaluation:export:college",
                ],
                "college_admin": [
                    "user:manage:college",
                    "evaluation:view:college",
                    "statistics:view:college_detail",
                    "evaluation:export:college",
                ],
                "school_admin": [
                    # 学校管理员拥有所有权限，这里不一一列出，因为已经在deps.py中设置了绕过权限检查
                ],
            }
            
            # 创建角色-权限关联
            for role_code, perm_codes in role_permissions.items():
                role = role_objects[role_code]
                for perm_code in perm_codes:
                    perm = permission_objects[perm_code]
                    
                    # 检查关联是否已存在
                    stmt = select(RolePermission).where(
                        RolePermission.role_id == role.id,
                        RolePermission.permission_id == perm.id
                    )
                    result = await session.execute(stmt)
                    existing_role_perm = result.scalar_one_or_none()
                    
                    if not existing_role_perm:
                        role_perm = RolePermission(role_id=role.id, permission_id=perm.id)
                        session.add(role_perm)
            
            # ==========================
            # 4. 获取或创建用户
            # ==========================
            users = [
                {"user_on": "teacher001", "user_name": "老师", "password": "123456", "role_code": "teacher"},
                {"user_on": "supervisor001", "user_name": "督导老师", "password": "123456", "role_code": "supervisor"},
                {"user_on": "college001", "user_name": "学院管理员", "password": "123456", "role_code": "college_admin"},
                {"user_on": "school001", "user_name": "学校管理员", "password": "123456", "role_code": "school_admin"},
            ]
            
            # 获取或创建用户
            for user_data in users:
                # 检查用户是否已存在
                stmt = select(User).where(User.user_on == user_data["user_on"])
                result = await session.execute(stmt)
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    continue
                
                # 创建新用户
                user = User(
                    user_on=user_data["user_on"],
                    user_name=user_data["user_name"],
                    password=get_password_hash(user_data["password"]),
                    status=1
                )
                session.add(user)
                await session.flush()
                
                # 分配角色
                role = role_objects[user_data["role_code"]]
                
                # 检查用户-角色关联是否已存在
                stmt = select(UserRole).where(
                    UserRole.user_id == user.id,
                    UserRole.role_id == role.id
                )
                result = await session.execute(stmt)
                existing_user_role = result.scalar_one_or_none()
                
                if not existing_user_role:
                    user_role = UserRole(user_id=user.id, role_id=role.id)
                    session.add(user_role)
            
            # ==========================
            # 4. 提交事务
            # ==========================
            await session.commit()
    
    print("权限初始化完成！")
    print(f"创建/获取了 {len(permissions)} 个权限")
    print(f"创建/获取了 {len(roles)} 个角色")
    print(f"创建/获取了 {len(users)} 个用户")
    print("角色权限分配完成")
    print("\n初始账号信息：")
    for user_data in users:
        print(f"  {user_data['user_name']}：账号={user_data['user_on']}，密码={user_data['password']}，角色={user_data['role_code']}")


if __name__ == "__main__":
    asyncio.run(init_permissions())
