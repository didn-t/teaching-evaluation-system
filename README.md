# 南宁理工学院听课评教系统

## 一、项目需求

### （一）项目概述

本项目为南宁理工学院定制开发听课评教一体化系统，支持微信小程序与 Web 端双端访问，覆盖普通老师、督导老师、学院管理员、学校管理员四类用户角色，实现课表同步、在线评教、反馈查看、数据统计及权限管控全流程管理。

### （二）核心功能模块

#### 1. 基础功能模块

| 功能项           | 详细说明                                                     |
| ---------------- | ------------------------------------------------------------ |
| 课表同步功能     | 1. 对接学校教务系统，自动同步所有教师个人课表；2. 按角色权限展示对应课表（普通老师看个人、督导看负责范围、管理员看全院 / 全校）； |
| 听课评教提交功能 | 1. 评分标准：采用百分制（贴合南宁理工学院听课记录表评分项）；2. 评分操作：支持听课中 / 课后在线实时提交；3. 文字建议：填写优点、问题及改进方向（如课程导入、互动方式），提交后不可修改；4. 匿名设置：由学校管理员配置（二选一：统一匿名 / 实名；或用户自主选择）；5. 记录要求：自动留存各学院每位教师的听课评教记录； |
| 反馈查看功能     | 1. 授课教师：查看自身总分、各维度得分、文字建议，支持历史记录查询及个人得分趋势图展示；2. 听课用户：仅查看自身提交的评教记录，不可查看他人原始评教数据； |

#### 2. 数据统计与分析功能

| 统计维度     | 详细说明                                                     |
| ------------ | ------------------------------------------------------------ |
| 学院层面统计 | 1. 教师评教详情：本院每位教师总分、平均分、各维度得分；2. 排名统计：教师校内排名、院内排名；3. 整体分析：学院总平均分计算、高频问题教学环节识别（如重难点讲解、互动性）、文字反馈汇总；4. 数据导出：支持听课记录报表、评教统计数据导出； |
| 学校层面统计 | 1. 学院排名：各学院评教总平均分排名（对比教学质量差异）；2. 教师排名：全校教师总分 / 平均分排名，支持按学院、课程类型筛选；3. 全局分析：汇总全校 / 指定学院评教整体情况，形成数据看板； |

#### 3. 权限管理功能

##### （1）角色权限明细

| 角色       | 核心权限                                                     |
| ---------- | ------------------------------------------------------------ |
| 普通老师   | 1. 查看个人课表；2. 参与听课并提交评分、文字建议；3. 查看个人评教结果（历史记录、得分趋势图）；4. 查看本院公开统计数据（如学院总平均分，不可查看他人详细评教数据）； |
| 督导老师   | 1. 查看所负责学院 / 教研组教师课表；2. 参与听课并提交评分、文字建议；3. 查看负责范围内教师评教汇总数据（总分、平均分、排名、问题统计）；4. 导出负责范围内听课记录报表； |
| 学院管理员 | 1. 维护本院用户账号基础信息；2. 查看本院所有教师评教详情、排名、总平均分、问题统计；3. 导出本院评教相关报表；4. 查看学校下发的评教通知； |
| 学校管理员 | 1. 系统最高权限：管理所有用户账号、角色分配及权限配置；2. 配置评教匿名 / 实名模式；3. 查看全校各学院、教师评教统计数据及排名；4. 导出全校评教汇总报表；5. 系统参数配置、数据备份与维护； |

##### （2）权限配置灵活性

1. 匿名 / 实名模式：由学校管理员统一配置，二选一（系统默认模式 / 用户自主选择模式）；
2. 督导权限：支持按学院、教研组等维度灵活分配管理范围；
3. 数据可见性：可按需调整各角色数据查看详细程度（如是否允许普通老师查看院内教师排名）；

## 二、技术方案

| 技术层面 | 选型说明                                         |
| -------- | ------------------------------------------------ |
| 前端技术 | 小程序：UniApp                                   |
| 后端技术 | Python 3.10.11；FastAPI 0.112.4；SQLAlchemy 2.0.45； |
| 数据库   | MySQL 8.0.36                                     |
| 其他依赖 | 详细查看requirements.txt                         |

后端目录结构
```
backend/
├── alembic/                    # 数据库迁移文件
│   ├── versions/              # 迁移版本文件
├── app/                       # 应用主目录
│   ├── api/                   # API 接口定义
│   │   └── v1/               # API 版本 v1
│   │       └── teaching_eval/ # 教学评教相关接口
│   │           ├── eval.py    # 评教相关接口
│   │           └── user.py    # 用户相关接口
│   ├── core/                  # 核心模块
│   │   ├── auth.py            # 认证相关
│   │   ├── config.py          # 配置管理
│   │   ├── deps.py            # 依赖注入
│   │   └── exceptions.py      # 异常处理
│   ├── crud/                  # 数据库操作
│   │   └── teaching_eval/     # 教学评教相关数据库操作
│   │       └── user.py        # 用户相关数据库操作
│   ├── middleware/            # 中间件
│   │   └── auth_middleware.py # 认证中间件
│   ├── models.py              # 数据库模型
│   ├── schemas.py             # 数据验证模型
│   └── base.py                # 基础配置
├── tests/                     # 测试文件
├── main.py                    # 主应用文件
├── requirements.txt           # 依赖包
└── .env                       # 环境配置
```

后端依赖一键安装命令
```bash
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

#### backend目录下有文件:requirements.txt；.env

**requirements.txt文件存放项目依赖版本**

 **.env文件 存放数据库配置等敏感信息**

.env例如：
```
# MySQL 数据库配置
MYSQL_USER=root
MYSQL_PASSWORD=a
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DB=teaching_evaluation_system

# JWT 配置
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 应用配置
APP_NAME='Teaching Evaluation System'
APP_VERSION=1.0.0
DEBUG=True
```

## 三、API 接口说明

FastAPI自动生成

### （一）接口设计原则

1. 统一前缀：所有接口统一前缀（如 `/api/v1/teaching-eval/`），区分不同业务模块；
2. 请求方式：遵循 RESTful 风格（GET：查询、POST：新增、PUT/PATCH：修改、DELETE：删除）；
3. 数据格式：请求 / 响应均采用 JSON 格式，统一返回状态码与提示信息；
4. 权限校验：所有接口（除登录、注册外）需携带 Token 进行身份验证与权限校验。

### （二）核心接口分类

| 业务模块     | 核心接口示例                                                 |
| ------------ | ------------------------------------------------------------ |
| 用户模块     | 1. `POST /api/v1/teaching-eval/user/login`（用户登录，获取 Token）；2. `POST /api/v1/teaching-eval/user/register`（用户注册）；3. `GET /api/v1/teaching-eval/user/role`（查询当前用户角色信息）；4. `GET /api/v1/teaching-eval/user/role-permissions`（查询角色权限信息）；5. `GET /api/v1/teaching-eval/user/permissions`（查询用户权限信息）；6. `PATCH /api/v1/teaching-eval/user/update`（更新用户基础信息）； |
| 评教模块     | 1. `POST /api/v1/teaching-eval/eval/system-configs`（创建系统配置）； |

### （三）统一响应格式

```json
{
  "code": 200, // 状态码：200成功、400参数错误、401未授权、500服务器错误
  "msg": "操作成功", // 提示信息
  "data": {}, // 业务数据（按需返回，如列表、详情、统计结果）
  "timestamp": 1735689600 // 请求时间戳
}
```

## 四、数据库设计

### （一）核心表结构



### （二）数据库关系图

```
用户(user) ←→ 用户角色(user_role) ←→ 角色(role) ←→ 角色权限(role_permission) ←→ 权限(permission)
   ↓
学院(college) ←→ 课表(timetable) ←→ 教学评价(teaching_evaluation)
   ↓
学院统计(college_evaluation_stat)
   ↓
教师统计(teacher_evaluation_stat)
```

## 五、项目管理

### （一）GitHub Flow 核心流程

GitHub Flow 是轻量级、适用于持续部署的分支管理流程，核心原则：保持 main 分支可部署，一个需求一个临时分支，流程闭环如下：

```plaintext
1.  基准同步：从最新 main 分支拉取代码（保证开发基准一致）
2.  创建分支：基于 main 分支创建语义化临时分支（功能/修复）
3.  本地开发：在临时分支完成开发，规范提交代码
4.  远程推送：将临时分支推送到 GitHub 远程仓库
5.  提交PR：创建 Pull Request（PR），发起代码审核
6.  审核合并：审核通过后，将临时分支合并到 main 分支
7.  分支清理：立即删除本地/远程临时分支
8.  自动/手动部署：同步部署 main 分支代码到生产/测试环境
```

**核心总结**：「建分支 → 开发 → 推送 → PR → 合并 → 删分支 → 部署」的循环迭代，确保 main 分支始终处于可部署状态。

### （二）GitHub Flow 常用 Git 命令清单

#### 前期准备：同步主分支最新代码

```bash
# 1. 切换到 main 主分支（唯一长期分支）
git checkout main

# 2. 拉取远程 main 分支最新更新（同步团队其他成员提交）
git pull origin main

# 3. （可选）查看当前分支状态，确认无未提交修改
git status
```

#### 分支操作：创建与切换临时分支

```bash
# 方式1：先创建分支，再切换（分步操作）
git branch feature/timetable-sync  # 功能分支：课表同步功能
git branch fix/evaluation-submit   # 修复分支：评教提交失败问题
git checkout feature/timetable-sync

# 方式2：创建并直接切换（推荐：一步到位）
git checkout -b feature/feedback-query  # 功能分支：反馈查询功能
git checkout -b fix/ranking-calculation  # 修复分支：排名计算错误问题

# 命名规范(无强制)：
# - 功能分支：feature/xxx（xxx为功能描述，小写+连字符）
# - 修复分支：fix/xxx（xxx为问题描述，小写+连字符）
# - 文档分支：docs/xxx（xxx为文档内容，如接口文档更新）
```

#### 本地开发：代码提交

```bash
# 1. 查看本地修改文件（确认修改范围，避免提交无关文件）
git status

# 2. 将修改文件加入暂存区（两种方式可选）
git add .  # 方式1：添加所有修改文件（推荐本地完整开发后使用）
git add src/pages/evaluation/  # 方式2：指定单个文件/目录（精准提交）

# 3. 提交代码到本地仓库（语义化提交信息，必填）
git commit -m "feat: 实现课表同步功能，对接教务系统接口"  # 功能新增：feat
git commit -m "fix: 修复评教提交时，文字建议为空的报错问题"  # 问题修复：fix
git commit -m "docs: 更新API接口文档，补充评教模块接口"     # 文档更新：docs
git commit -m "style: 调整评教页面样式，优化布局排版"       # 样式修改：style

# 提交信息规范：<类型>: <描述>（描述简洁明了，不超过50字）
```

#### 远程协作：推送分支与创建 PR

```bash
# 1. 将本地临时分支推送到 GitHub 远程仓库（分支名与本地保持一致）
git push origin feature/timetable-sync

# 2. （首次推送可选）关联本地与远程分支（后续推送可直接 git push）
git push -u origin feature/timetable-sync

# 3. 推送后操作：
# - 打开 GitHub 仓库，切换到该临时分支
# - 点击「New pull request」，选择 base: main / compare: 临时分支
# - 填写PR描述（开发内容、测试要点），指定审核人，提交审核
```

#### 冲突解决：合并主分支最新代码

```bash
# 1. 确保当前处于临时分支
git checkout feature/timetable-sync

# 2. 拉取远程 main 分支最新代码，并合并到当前临时分支
git pull origin main

# 3. 冲突出现后：
# - 打开冲突文件（标记 <<<<<<< HEAD / ======= / >>>>>>> main）
# - 手动协商解决冲突（保留有效代码，删除冲突标记）
# - 解决后提交代码
git add .
git commit -m "resolve: 合并main分支最新代码，解决课表数据冲突"
git push origin feature/timetable-sync

# 4. 冲突解决后，重新提交PR审核
```

#### 后续操作：合并后同步与分支清理

```bash
# 1. PR审核通过后，切换回 main 主分支
git checkout main

# 2. 拉取远程 main 分支合并后的最新代码（同步合并结果）
git pull origin main

# 3. 删除本地临时分支（-d：安全删除，未合并会报错，避免误删）
git branch -d feature/timetable-sync

# 4. 删除远程临时分支（保持远程仓库整洁）
git push origin --delete feature/timetable-sync

# 5. （可选）查看所有分支，确认临时分支已删除
git branch  # 查看本地分支
git branch -a  # 查看本地+远程所有分支
```

#### 辅助命令：常用操作

```bash
# 1. 查看分支提交历史（追溯提交记录）
git log  # 详细日志
git log --oneline  # 简洁日志（一行显示一条提交）

# 2. 放弃本地修改（未提交到暂存区时，谨慎使用）
git checkout -- src/pages/evaluation/index.vue  # 放弃单个文件修改
git reset --hard  # 放弃所有本地修改（恢复到最近一次提交）

# 3. 重命名本地分支（如需修改分支名）
git branch -m old-branch-name new-branch-name
```

## 六、部署说明

### （一）环境准备

1. 安装 Python 3.10+
2. 安装 MySQL 8.0+
3. 安装 Git

### （二）后端部署

1. 克隆项目代码
```bash
git clone <repository-url>
cd teaching-evaluation-system/backend
```

2. 创建虚拟环境并安装依赖
```bash
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. 创建数据库
```sql
CREATE DATABASE teaching_evaluation_system 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;
```

4. 配置环境变量
```bash
# 复制配置文件
cp .env.example .env
# 编辑 .env 文件，配置数据库连接信息
```

5. 运行数据库迁移
```bash
alembic upgrade head
```
