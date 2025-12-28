# app/crud/logs.py
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models import OperationLog, LoginLog  # 按你的实际路径改


def create_operation_log(
    db: Session,
    *,
    user_id: Optional[int],
    user_name: Optional[str],
    operation_type: str,
    module: str,
    target_id: Optional[int] = None,
    target_type: Optional[str] = None,
    content: Optional[Dict[str, Any]] = None,
    before_data: Optional[Dict[str, Any]] = None,
    after_data: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_url: Optional[str] = None,
    request_method: Optional[str] = None,
    response_code: Optional[int] = None,
    execute_time: Optional[int] = None,
) -> OperationLog:
    now = datetime.utcnow()
    obj = OperationLog(
        user_id=user_id,
        user_name=user_name,
        operation_type=operation_type,
        module=module,
        target_id=target_id,
        target_type=target_type,
        content=content,
        before_data=before_data,
        after_data=after_data,
        ip_address=ip_address,
        user_agent=user_agent,
        request_url=request_url,
        request_method=request_method,
        response_code=response_code,
        execute_time=execute_time,
        create_time=now,
        create_date=now.strftime("%Y-%m-%d"),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def create_login_log(
    db: Session,
    *,
    user_id: Optional[int],
    user_name: Optional[str],
    login_type: str,
    login_status: int,
    fail_reason: Optional[str] = None,
    ip_address: Optional[str] = None,
    location: Optional[str] = None,
    device_type: Optional[str] = None,
    browser: Optional[str] = None,
    os: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> LoginLog:
    now = datetime.utcnow()
    obj = LoginLog(
        user_id=user_id,
        user_name=user_name,
        login_type=login_type,
        login_status=login_status,
        fail_reason=fail_reason,
        ip_address=ip_address,
        location=location,
        device_type=device_type,
        browser=browser,
        os=os,
        user_agent=user_agent,
        create_time=now,
        create_date=now.strftime("%Y-%m-%d"),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
