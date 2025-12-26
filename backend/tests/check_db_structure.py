#!/usr/bin/env python3
"""
检查数据库表结构的脚本
用于确认字段长度是否正确
"""
import asyncio
from sqlalchemy import create_engine, text
from app.core.config import MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, MYSQL_DB

# 创建同步引擎
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
engine = create_engine(DATABASE_URL)

def check_column_info():
    """检查相关表的字段信息"""
    with engine.connect() as conn:
        print("检查 teacher_evaluation_stat 表...")
        try:
            result = conn.execute(text("""
                SELECT COLUMN_NAME, COLUMN_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :db_name AND TABLE_NAME = 'teacher_evaluation_stat' AND COLUMN_NAME = 'stat_year'
            """), {"db_name": MYSQL_DB})
            row = result.fetchone()
            if row:
                print(f"  teacher_evaluation_stat.stat_year: {dict(row)}")
            else:
                print("  teacher_evaluation_stat.stat_year 不存在")
        except Exception as e:
            print(f"  检查 teacher_evaluation_stat 失败: {e}")
        
        print("\n检查 college_evaluation_stat 表...")
        try:
            result = conn.execute(text("""
                SELECT COLUMN_NAME, COLUMN_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :db_name AND TABLE_NAME = 'college_evaluation_stat' AND COLUMN_NAME = 'stat_year'
            """), {"db_name": MYSQL_DB})
            row = result.fetchone()
            if row:
                print(f"  college_evaluation_stat.stat_year: {dict(row)}")
            else:
                print("  college_evaluation_stat.stat_year 不存在")
        except Exception as e:
            print(f"  检查 college_evaluation_stat 失败: {e}")
        
        print("\n检查 timetable 表...")
        try:
            result = conn.execute(text("""
                SELECT COLUMN_NAME, COLUMN_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = :db_name AND TABLE_NAME = 'timetable' AND COLUMN_NAME = 'academic_year'
            """), {"db_name": MYSQL_DB})
            row = result.fetchone()
            if row:
                print(f"  timetable.academic_year: {dict(row)}")
            else:
                print("  timetable.academic_year 不存在")
        except Exception as e:
            print(f"  检查 timetable 失败: {e}")

if __name__ == "__main__":
    print("正在检查数据库表结构...")
    check_column_info()
    print("检查完成")