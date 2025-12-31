# app/api/v1/teaching_eval/auth.py
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence

from app.database import get_db
from app.schemas import (
    BaseResponse,
    TokenData,
)
from app.core.deps import get_current_user, require_access
from app.crud.role import role_crud
from app.crud.permission import permission_crud
from app.crud.user import user_crud
from app.models import Role, Permission, User, UserRole

router = APIRouter(prefix="/auth", tags=["角色权限管理"])


# -----------------------------
# 角色相关接口
# -----------------------------
@router.post("/role", summary="创建角色")
async def create_role(
    name: str,
    code: str,
    description: Optional[str] = None,
    status: int = 1,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:role:create",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """创建角色"""
    try:
        # 检查角色代码是否已存在
        existing = await role_crud.get_by_code(db, role_code=code)
        if existing:
            raise HTTPException(status_code=400, detail="角色代码已存在")
        
        role_data = {
            "role_name": name,
            "role_code": code,
            "description": description,
            "status": status,
            "is_delete": False,
        }
        role = await role_crud.create(db, obj_in=role_data)
        return BaseResponse(code=200, msg="success", data={
            "id": role.id,
            "name": role.role_name,
            "code": role.role_code,
            "description": role.description,
            "status": role.status,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建角色失败: {e}")


@router.get("/role/{role_id}", summary="获取角色详情")
async def get_role(
    role_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:role:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取角色详情"""
    role = await role_crud.get(db, id=role_id)
    if not role or role.is_delete:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 获取角色的权限
    stmt = select(Permission).join(Role.permissions).where(Role.id == role_id)
    result = await db.execute(stmt)
    permissions = result.scalars().all()
    
    return BaseResponse(code=200, msg="success", data={
        "id": role.id,
        "name": role.role_name,
        "code": role.role_code,
        "description": role.description,
        "status": role.status,
        "permissions": [{
            "id": perm.id,
            "code": perm.permission_code,
            "name": perm.permission_name,
        } for perm in permissions],
    })


@router.put("/role/{role_id}", summary="更新角色")
async def update_role(
    role_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[int] = None,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:role:update",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """更新角色"""
    role = await role_crud.get(db, id=role_id)
    if not role or role.is_delete:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    try:
        update_data = {}
        if name is not None:
            update_data["role_name"] = name
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        
        updated_role = await role_crud.update(db, db_obj=role, obj_in=update_data)
        return BaseResponse(code=200, msg="success", data={
            "id": updated_role.id,
            "name": updated_role.role_name,
            "code": updated_role.role_code,
            "description": updated_role.description,
            "status": updated_role.status,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新角色失败: {e}")


@router.delete("/role/{role_id}", summary="删除角色")
async def delete_role(
    role_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:role:delete",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """删除角色（软删除）"""
    role = await role_crud.get(db, id=role_id)
    if not role or role.is_delete:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    try:
        deleted_role = await role_crud.soft_remove(db, id=role_id)
        return BaseResponse(code=200, msg="success", data={
            "id": deleted_role.id,
            "name": deleted_role.role_name,
            "code": deleted_role.role_code,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除角色失败: {e}")


@router.get("/roles", summary="获取角色列表")
async def list_roles(
    skip: int = 0,
    limit: int = 50,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:role:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取角色列表"""
    roles, total = await role_crud.get_multi(db, skip=skip, limit=limit)
    
    role_responses = []
    for role in roles:
        if not role.is_delete:
            role_responses.append({
                "id": role.id,
                "name": role.role_name,
                "code": role.role_code,
                "description": role.description,
                "status": role.status,
            })
    
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": role_responses,
            "total": total,
            "skip": skip,
            "limit": limit,
        },
    )


# -----------------------------
# 权限相关接口
# -----------------------------
@router.post("/permission", summary="创建权限")
async def create_permission(
    code: str,
    name: str,
    type: int,
    parent_id: Optional[int] = None,
    sort: int = 0,
    description: Optional[str] = None,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:permission:create",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """创建权限"""
    try:
        # 检查权限代码是否已存在
        existing = await permission_crud.get_by_code(db, permission_code=code)
        if existing:
            raise HTTPException(status_code=400, detail="权限代码已存在")
        
        permission_data = {
            "permission_code": code,
            "permission_name": name,
            "permission_type": type,
            "parent_id": parent_id,
            "sort_order": sort,
            "permission_description": description,
            "is_delete": False,
        }
        permission = await permission_crud.create(db, obj_in=permission_data)
        return BaseResponse(code=200, msg="success", data={
            "id": permission.id,
            "code": permission.permission_code,
            "name": permission.permission_name,
            "type": permission.permission_type,
            "parent_id": permission.parent_id,
            "sort": permission.sort_order,
            "description": permission.permission_description,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建权限失败: {e}")


@router.get("/permission/{permission_id}", summary="获取权限详情")
async def get_permission(
    permission_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:permission:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取权限详情"""
    permission = await permission_crud.get(db, id=permission_id)
    if not permission or permission.is_delete:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    return BaseResponse(code=200, msg="success", data={
        "id": permission.id,
        "code": permission.permission_code,
        "name": permission.permission_name,
        "type": permission.permission_type,
        "parent_id": permission.parent_id,
        "sort": permission.sort_order,
        "description": permission.permission_description,
    })


@router.put("/permission/{permission_id}", summary="更新权限")
async def update_permission(
    permission_id: int,
    name: Optional[str] = None,
    type: Optional[int] = None,
    parent_id: Optional[int] = None,
    sort: Optional[int] = None,
    description: Optional[str] = None,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:permission:update",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """更新权限"""
    permission = await permission_crud.get(db, id=permission_id)
    if not permission or permission.is_delete:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    try:
        update_data = {}
        if name is not None:
            update_data["permission_name"] = name
        if type is not None:
            update_data["permission_type"] = type
        if parent_id is not None:
            update_data["parent_id"] = parent_id
        if sort is not None:
            update_data["sort_order"] = sort
        if description is not None:
            update_data["permission_description"] = description
        
        updated_permission = await permission_crud.update(db, db_obj=permission, obj_in=update_data)
        return BaseResponse(code=200, msg="success", data={
            "id": updated_permission.id,
            "code": updated_permission.permission_code,
            "name": updated_permission.permission_name,
            "type": updated_permission.permission_type,
            "parent_id": updated_permission.parent_id,
            "sort": updated_permission.sort_order,
            "description": updated_permission.permission_description,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新权限失败: {e}")


@router.delete("/permission/{permission_id}", summary="删除权限")
async def delete_permission(
    permission_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:permission:delete",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """删除权限（软删除）"""
    permission = await permission_crud.get(db, id=permission_id)
    if not permission or permission.is_delete:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    try:
        deleted_permission = await permission_crud.soft_remove(db, id=permission_id)
        return BaseResponse(code=200, msg="success", data={
            "id": deleted_permission.id,
            "code": deleted_permission.permission_code,
            "name": deleted_permission.permission_name,
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除权限失败: {e}")


@router.get("/permissions", summary="获取权限列表")
async def list_permissions(
    skip: int = 0,
    limit: int = 100,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:permission:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取权限列表"""
    permissions, total = await permission_crud.get_multi(db, skip=skip, limit=limit)
    
    permission_responses = []
    for perm in permissions:
        if not perm.is_delete:
            permission_responses.append({
                "id": perm.id,
                "code": perm.permission_code,
                "name": perm.permission_name,
                "type": perm.permission_type,
                "parent_id": perm.parent_id,
                "sort": perm.sort_order,
                "description": perm.permission_description,
            })
    
    return BaseResponse(
        code=200,
        msg="success",
        data={
            "list": permission_responses,
            "total": total,
            "skip": skip,
            "limit": limit,
        },
    )


@router.get("/permissions/tree", summary="获取权限树")
async def get_permission_tree(
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:permission:read",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取权限树，适合前端展示"""
    try:
        # 使用权限CRUD中的list_tree方法获取树形结构
        permission_tree = await permission_crud.list_tree(db)
        return BaseResponse(code=200, msg="success", data=permission_tree)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取权限树失败: {e}")


# -----------------------------
# 角色权限关联接口
# -----------------------------
@router.post("/role/{role_id}/permissions", summary="给角色分配权限")
async def assign_permissions_to_role(
    role_id: int,
    permission_ids: List[int],
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:role:assign_permission",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """给角色分配权限"""
    try:
        # 获取角色
        role = await role_crud.get(db, id=role_id)
        if not role or role.is_delete:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        # 获取要分配的权限
        stmt = select(Permission).where(Permission.id.in_(permission_ids), Permission.is_delete == False)
        result = await db.execute(stmt)
        permissions = list(result.scalars().all())
        
        # 检查是否所有权限都存在
        if len(permissions) != len(permission_ids):
            raise HTTPException(status_code=400, detail="部分权限不存在或已删除")
        
        # 分配权限
        await role_crud.set_permissions(db, role=role, permissions=permissions)
        
        return BaseResponse(code=200, msg="权限分配成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分配权限失败: {e}")


@router.get("/role/{role_id}/permissions", summary="获取角色的权限")
async def get_role_permissions(
    role_id: int,
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:role:read_permissions",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """获取角色的权限"""
    try:
        # 获取角色
        role = await role_crud.get(db, id=role_id)
        if not role or role.is_delete:
            raise HTTPException(status_code=404, detail="角色不存在")
        
        # 获取角色的权限
        stmt = select(Permission).join(Role.permissions).where(
            Role.id == role_id,
            Permission.is_delete == False
        )
        result = await db.execute(stmt)
        permissions = result.scalars().all()
        
        permission_responses = [{
            "id": perm.id,
            "code": perm.permission_code,
            "name": perm.permission_name,
            "type": perm.permission_type,
            "parent_id": perm.parent_id,
        } for perm in permissions]
        
        return BaseResponse(code=200, msg="success", data=permission_responses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色权限失败: {e}")


# -----------------------------
# 哥用户分配角色接口
# -----------------------------
@router.post("/user/{user_id}/roles", summary="给用户分配角色")
async def assign_roles_to_user(
    user_id: int,
    role_ids: List[int],
    current_user: TokenData = Depends(
        require_access(roles_any=("school_admin",), perms_all=("auth:user:assign_role",))
    ),
    db: AsyncSession = Depends(get_db),
):
    """给用户分配角色"""
    try:
        # 参数验证
        if not role_ids:
            raise HTTPException(status_code=400, detail="角色ID列表不能为空")
        
        if len(role_ids) != len(set(role_ids)):
            raise HTTPException(status_code=400, detail="角色ID列表中存在重复项")
        
        # 获取用户
        user = await user_crud.get(db, id=user_id)
        if not user or user.is_delete:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        # 获取要分配的角色
        stmt = select(Role).where(Role.id.in_(role_ids), Role.is_delete == False)
        result = await db.execute(stmt)
        roles = list(result.scalars().all())
        
        # 检查是否所有角色都存在
        if len(roles) != len(role_ids):
            found_role_ids = {role.id for role in roles}
            missing_role_ids = [rid for rid in role_ids if rid not in found_role_ids]
            raise HTTPException(status_code=400, detail=f"以下角色不存在或已删除: {missing_role_ids}")
        
        # 分配角色给用户
        await set_user_roles(db, user=user, roles=roles)
        
        return BaseResponse(code=200, msg="角色分配成功")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分配角色失败: {e}")


# 辅助函数
async def set_user_roles(db: AsyncSession, *, user: User, roles: Sequence[Role]) -> User:
    """设置用户的角色"""
    try:
        # 先删除用户现有的所有角色关联
        stmt = select(UserRole).where(UserRole.user_id == user.id)
        result = await db.execute(stmt)
        existing_user_roles = result.scalars().all()
        
        # 删除现有角色关联
        for user_role in existing_user_roles:
            await db.delete(user_role)
        
        # 添加新的角色关联
        for role in roles:
            user_role = UserRole(user_id=user.id, role_id=role.id)
            db.add(user_role)
        
        # 一次性提交所有更改
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        await db.rollback()
        raise e
