#!/usr/bin/env python3
"""
测试数据库连接和插入部分测试数据
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models import Base, User, College
from app.core.config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB

# 创建数据库引擎
DATABASE_URL = f"mysql+asyncmy://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def test_connection():
    """测试数据库连接"""
    try:
        async with AsyncSessionLocal() as db:
            # 尝试查询任意表以测试连接
            result = await db.execute(select(College).limit(1))
            print("数据库连接正常")
            return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return False

async def insert_colleges():
    """插入学院测试数据"""
    try:
        async with AsyncSessionLocal() as db:
            college_data = [
                {"college_code": "CS", "college_name": "计算机科学与技术学院", "short_name": "计算机学院"},
                {"college_code": "EE", "college_name": "电子信息工程学院", "short_name": "电子学院"},
                {"college_code": "ME", "college_name": "机械工程学院", "short_name": "机械学院"},
                {"college_code": "MATH", "college_name": "数学与应用数学学院", "short_name": "数学院"},
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
    except Exception as e:
        print(f"插入学院数据失败: {e}")

async def main():
    print("开始测试数据库连接...")
    if await test_connection():
        print("连接成功，开始插入学院数据...")
        await insert_colleges()
        print("测试完成")
    else:
        print("连接失败，无法继续")

if __name__ == "__main__":
    asyncio.run(main())