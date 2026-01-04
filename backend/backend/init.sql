-- MySQL 初始化脚本
-- 用于在容器首次启动时初始化数据库

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS teaching_evaluation_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 选择数据库
USE teaching_evaluation_system;

-- 确保数据库字符集设置正确
ALTER DATABASE teaching_evaluation_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

