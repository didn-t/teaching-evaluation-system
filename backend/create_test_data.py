"""
创建测试数据脚本
用于在数据库中创建测试用户和其他必要数据
"""
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models import User, College
from app.database import Base
from passlib.context import CryptContext

# 加载环境变量
project_root = Path(__file__).parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path, encoding='utf-8')

# 获取数据库URL
DATABASE_URL = f"mysql+asyncmy://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}"

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_data():
    """创建测试数据"""
    # 创建数据库引擎
    engine = create_async_engine(DATABASE_URL)
    
    # 创建会话
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        # 检查是否已存在测试数据
        result = await session.execute(select(User).where(User.user_no == "admin"))
        existing_user = result.scalars().first()
        
        if existing_user:
            print("测试数据已存在，跳过创建")
            return
        
        # 创建一个测试学院
        test_college = College(
            college_code="01",
            college_name="信息工程学院"
        )
        session.add(test_college)
        await session.flush()  # 获取ID
        
        # 创建管理员用户
        admin_user = User(
            user_no="admin",
            user_name="管理员",
            role_type=4,  # 学校管理员
            college_id=test_college.id,
            password=pwd_context.hash("admin123")  # 加密密码
        )
        session.add(admin_user)
        
        # 创建教师用户
        teacher_user = User(
            user_no="teacher001",
            user_name="张老师",
            role_type=1,  # 普通教师
            college_id=test_college.id,
            password=pwd_context.hash("teacher123")  # 加密密码
        )
        session.add(teacher_user)
        
        # 创建督导用户
        supervisor_user = User(
            user_no="supervisor001",
            user_name="李督导",
            role_type=2,  # 督导
            college_id=test_college.id,
            password=pwd_context.hash("supervisor123")  # 加密密码
        )
        session.add(supervisor_user)
        
        # 提交事务
        await session.commit()
        print("测试数据创建成功！")
        print("- 管理员账号: admin / 密码: admin123")
        print("- 教师账号: teacher001 / 密码: teacher123")
        print("- 督导账号: supervisor001 / 密码: supervisor123")


if __name__ == "__main__":
    asyncio.run(create_test_data())