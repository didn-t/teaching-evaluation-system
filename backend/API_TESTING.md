# 教学评价系统 API 测试指南

## 测试脚本说明

本项目包含以下测试脚本：

- `test_api.py` - 基础API接口测试
- `create_test_data.py` - 创建测试数据
- `test_api_complete.py` - 完整API功能测试
- `API_TESTING.md` - 本说明文档

## 使用步骤

### 1. 启动应用

首先确保数据库已创建，然后启动FastAPI应用：

```bash
cd D:\teaching-evaluation-system\backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. 创建测试数据

在另一个终端中运行以下命令创建测试数据：

```bash
cd D:\teaching-evaluation-system\backend
python create_test_data.py
```

这将创建以下测试账号：

- 管理员: `admin` / 密码: `admin123`
- 教师: `teacher001` / 密码: `teacher123`
- 督导: `supervisor001` / 密码: `supervisor123`

### 3. 运行测试

在应用运行状态下，运行测试脚本：

```bash
# 运行基础测试
python test_api.py

# 运行完整测试
python test_api_complete.py
```

## API 端点

### 健康检查端点

- `GET /health` - 应用健康检查
- `GET /health/db` - 数据库健康检查

### 用户认证端点

- `POST /api/v1/teaching-eval/user/login` - 用户登录
- `GET /api/v1/teaching-eval/user/info` - 获取用户信息

### 评价相关端点

- `GET/POST /api/v1/teaching-eval/colleges` - 学院信息
- `GET/POST /api/v1/teaching-eval/users` - 用户信息
- `GET/POST /api/v1/teaching-eval/evaluations` - 评教信息
- 其他评价相关端点...

## 测试内容

### 基础测试 (test_api.py)

- 应用健康检查
- 数据库连接检查
- 用户登录功能
- 认证保护端点

### 完整测试 (test_api_complete.py)

- 所有基础测试内容
- 多用户登录测试
- API文档端点测试
- 详细的错误处理测试

## 注意事项

1. 确保在运行测试前应用已启动
2. 确保数据库连接配置正确
3. 测试数据仅在首次运行时创建
4. 测试过程中不会修改或删除现有数据

## 预期输出

成功运行测试后，您应该看到类似以下的输出：

```
======================================================================
开始运行完整API测试
目标URL: http://localhost:8000
开始时间: 2025-12-24 19:00:00
======================================================================
1. 测试健康检查端点
   健康检查状态: 200
   响应: {'status': 'healthy'}
   数据库健康检查状态: 200
   响应: {'status': 'healthy', 'database': 'connected'}

2. 测试用户登录 - 账号: admin
   登录响应状态: 200
   登录成功！获取到token: abcdef123456...
```