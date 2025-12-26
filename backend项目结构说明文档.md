# 教学评教系统项目结构说明文档

## 1. 项目概述

教学评教系统是一个基于 FastAPI 框架开发的 Web 应用，主要用于南宁理工学院的听课评教工作。系统采用现代化的后端架构，使用 MySQL 数据库存储数据，并通过 Alembic 进行数据库迁移管理。

## 2. 目录结构

```
teaching-evaluation-system/
├── alembic/                    # 数据库迁移文件
│   ├── versions/              # 迁移版本文件
│   ├── README                 # 迁移说明
│   └── env.py                 # 迁移环境配置
├── app/                       # 应用主目录
│   ├── api/                   # API 接口定义
│   │   └── v1/               # API 版本 v1
│   │       └── teaching_eval/ # 教学评教相关接口
│   │           ├── eval.py    # 评教相关接口
│   │           └── user.py    # 用户相关接口 (比如对用户进行操作的接口就放在user.py文件里)
│   ├── core/                  # 核心功能模块
│   │   ├── auth.py            # 认证相关功能
│   │   └── config.py          # 配置管理（读取.env文件）
│   ├── crud/                  # 数据库操作
│   │   └── teaching_eval/     # 教学评教相关数据库操作
│   │       └── user.py        # 用户相关数据库操作
│   ├── utils/                 # 工具函数(后续添加)
│   ├── spiders/               # 爬虫模块(后续添加)
│   │   └── nnlg_spider/        # 南宁理工教务系统爬虫(后续添加)
│   ├── base.py                # 数据库基础模型
│   ├── database.py            # 数据库连接配置
│   ├── models.py              # 数据库模型定义
│   └── schemas.py             # Pydantic 数据模型
├── tests/                     # 测试文件目录
├── .env                       # 环境变量配置
├── alembic.ini                # Alembic 配置文件
├── main.py                    # 应用入口文件
├── requirements.txt           # 项目依赖
└── 数据库迁移说明.md           # 数据库迁移说明文档
```

## 3. 核心模块说明

### 3.1 主应用入口 (main.py)

- 使用 FastAPI 框架构建 Web 应用
- 配置 CORS 跨域资源共享
- 定义根路由和健康检查接口
- 包含数据库连接健康检查
- 集成 API 路由

### 3.2 配置模块 (app/core/config.py)

- 加载环境变量配置
- 定义数据库连接参数
- JWT 认证配置
- 应用基本信息配置

### 3.3 数据库模块 (app/database.py)

- 配置异步数据库连接
- 使用 asyncmy 驱动连接 MySQL
- 创建数据库会话工厂
- 提供数据库依赖注入

### 3.4 数据模型 (app/models.py)

系统包含以下主要数据模型：

#### 用户权限相关
- **User**: 用户表 - 存储系统用户信息，包括工号、姓名、学院、密码等
- **UserWechatBind**: 用户微信绑定表 - 管理用户与微信的绑定关系
- **Permission**: 权限表 - 定义系统中的各种权限
- **Role**: 角色表 - 定义系统中的角色
- **UserRole**: 用户-角色关联表 - 管理用户与角色的关联关系
- **RolePermission**: 角色-权限关联表 - 管理角色与权限的关联关系

#### 学院与课表相关
- **College**: 学院表 - 存储学院信息
- **Timetable**: 课表 - 存储课程安排信息

#### 评价相关
- **EvaluationDimension**: 评价维度配置表 - 定义评教维度和评分标准
- **TeachingEvaluation**: 教学评价表 - 存储具体的评教记录

#### 统计相关
- **TeacherEvaluationStat**: 教师评价统计表 - 存储教师评教统计数据
- **CollegeEvaluationStat**: 学院评价统计表 - 存储学院评教统计数据

#### 系统配置与日志
- **SystemConfig**: 系统配置表 - 存储系统配置项
- **OperationLog**: 操作日志表 - 记录系统操作日志
- **LoginLog**: 登录日志表 - 记录用户登录日志
- **OperationLogArchive**: 操作日志归档表 - 归档历史操作日志
- **LoginLogArchive**: 登录日志归档表 - 归档历史登录日志

### 3.5 API 接口 (app/api/v1/teaching_eval/)

#### 用户接口 (user.py)
- `/register`: 用户注册
- `/login`: 用户登录
- `/role`: 获取用户角色信息
- `/update`: 更新用户信息
- `/logout`: 用户登出
- `/role-permissions`: 获取用户角色权限信息
- `/permissions`: 获取用户权限信息

#### 评教接口 (eval.py)
- `/system-configs`: 系统配置管理

### 3.6 数据库操作 (app/crud/teaching_eval/)

#### 用户相关操作 (user.py)
- `get_user`: 根据用户ID获取用户信息
- `create_user`: 创建新用户
- `get_user_by_username`: 根据用户名获取用户
- `update_user`: 更新用户信息
- `get_roles_name`: 获取用户角色名称列表
- `get_role_permissions`: 获取角色权限列表
- `get_user_permissions`: 获取用户权限列表

### 3.7 数据传输模型 (app/schemas.py)

定义了各种 Pydantic 模型用于数据验证和序列化：

- **用户相关模型**: UserBase, UserCreate, UserUpdate, UserResponse
- **认证相关模型**: Token, TokenData
- **学院相关模型**: CollegeBase, CollegeCreate, CollegeResponse
- **权限相关模型**: PermissionDictBase, PermissionDictCreate, PermissionDictResponse
- **课表相关模型**: TimetableBase, TimetableCreate, TimetableResponse
- **评教相关模型**: TeachingEvaluationBase, TeachingEvaluationCreate, TeachingEvaluationResponse
- **统计相关模型**: TeacherEvaluationStatBase, CollegeEvaluationStatBase
- **系统配置模型**: SystemConfigBase, SystemConfigCreate, SystemConfigResponse

### 3.8 工具函数 (app/utils/)

- 通用工具函数，如日期处理、数据格式化等

### 3.9 爬虫模块 (app/spiders/)

#### 南宁理工教务系统爬虫 (app/spiders/nnlg_spider/)
- 用于从南宁理工学院教务系统抓取课表信息
- 用户认证和会话管理
- 课程数据提取和处理
- 数据同步到本地数据库
- 定时任务调度功能

### 3.10 核心功能 (app/core/)

#### 认证功能 (auth.py)
- 密码哈希处理
- JWT Token 创建和验证
- 密码验证

#### 配置管理 (config.py)
- 环境变量加载
- 数据库连接配置
- 应用配置项管理

## 4. 技术栈

- **框架**: FastAPI 
- **数据库**: MySQL - 关系型数据库
- **ORM**: SQLAlchemy - 数据库对象关系映射
- **异步数据库驱动**: asyncmy - MySQL 异步驱动
- **数据验证**: Pydantic - 数据验证和序列化
- **认证**: JWT - JSON Web Token 认证
- **密码哈希**: bcrypt - 密码加密
- **数据库迁移**: Alembic - 数据库迁移工具
- **环境变量**: python-dotenv - 环境变量管理

## 5. 依赖管理

项目依赖定义在 [requirements.txt](file:///D:/teaching-evaluation-system/backend/requirements.txt) 文件中，主要包括：

- fastapi~=0.112.4
- SQLAlchemy~=2.0.45
- python-jose~=3.5.0
- passlib~=1.7.4
- python-dotenv~=1.2.1
- pydantic~=2.12.5
- uvicorn~=0.40.0
- pymysql~=1.1.2
- alembic~=1.11.1
- bcrypt~=5.0.0
- asyncmy~=0.2.10

## 6. 数据库迁移

项目使用 Alembic 进行数据库迁移管理，所有迁移文件存储在 [alembic/versions/](file:///D:/teaching-evaluation-system/backend/alembic/versions) 目录中，包括：

- `02e0b63ca617_adddefault.py` - 添加默认数据
- `2f89cbe0b126_recrbac.py` - RBAC 权限系统重构
- `568ac3ea726d_fix_foreign_keys.py` - 修复外键约束
- `8630f7cd6150_fixuser_id.py` - 修复用户ID字段
- `8d2e59e4334d_fix_college_id.py` - 修复学院ID字段
- `9f9aaa16cd09_recallmodels.py` - 模型重构
- `c7d2deca3812_fixuser_id.py` - 修复用户ID字段
- `dad04216851f_fixmodels.py` - 模型修复

## 7. 部署说明

1. 安装依赖：`pip install -r requirements.txt`
2. 配置环境变量：在 [.env](file:///D:/teaching-evaluation-system/backend/.env) 文件中设置数据库连接信息
3. 创建数据库`teaching_evaluation_system`
4. 运行数据库迁移：`alembic upgrade head`
5. 启动应用：`python main.py`

## 8. 未来可扩展模块

系统架构设计考虑了未来的扩展需求，以下是一些可能新增的模块建议：

### 8.1 爬虫模块 (app/spiders/)
- **nnlg_spider/**: 南宁理工教务系统爬虫 - 用于自动同步课表、学生信息等
- **evaluation_spider/**: 评教数据爬虫 - 从其他系统抓取历史评教数据

### 8.2 消息通知模块 (app/notification/)
- **sms/**: 短信通知功能
- **email/**: 邮件通知功能
- **wechat/**: 微信消息推送功能

### 8.3 报表模块 (app/reports/)
- **excel/**: Excel 报表生成
- **pdf/**: PDF 报告生成
- **charts/**: 数据可视化图表

### 8.4 文件处理模块 (app/files/)
- **upload/**: 文件上传处理
- **storage/**: 文件存储管理
- **export/**: 数据导出功能

### 8.5 第三方集成 (app/integration/)
- **wechat/**: 微信集成接口
- **ldap/**: LDAP 认证集成
- **sso/**: 单点登录集成

### 8.6 数据分析模块 (app/analytics/)
- **evaluation_analysis/**: 评教数据分析
- **trend_analysis/**: 趋势分析
- **predictive/**: 预测模型
