# 教学评价系统测试数据插入脚本使用说明

## 脚本概述
`insert_test_data.py` 脚本用于一键插入教学评价系统的完整测试数据，包括：
- 学院数据（6个学院）
- 权限数据（10个权限）
- 角色数据（4个角色）
- 用户数据（1个管理员 + 5个教师）
- 评价维度数据（5个维度）
- 课表数据（每个教师最多4门课）
- 教学评价数据（8个评价记录）
- 统计数据（教师统计和学院统计）

## 脚本文件
- 主脚本: `insert_test_data.py`
- 测试连接脚本: `test_db_connection.py`

## 如何运行脚本

### 方法1：命令行运行（推荐）
打开命令提示符或PowerShell，进入项目目录并运行：
```bash
cd D:\teaching-evaluation-system\backend
python insert_test_data.py
```

### 方法2：在PyCharm中运行
1. 在PyCharm中打开 `insert_test_data.py` 文件
2. 右键点击编辑器中的任意位置
3. 选择 "Run 'insert_test_data'" 或按快捷键 Shift+F10

### 方法3：在终端中运行
在PyCharm底部的终端中，切换到经典终端模式：
1. 在PyCharm底部找到 "Terminal" 标签
2. 点击终端设置图标（齿轮图标）
3. 确保 "Classic terminal" 选项被勾选
4. 在终端中输入以下命令：
```bash
python insert_test_data.py
```

## 脚本特性
1. **去重插入**：脚本会检查数据是否已存在，避免重复插入
2. **依赖关系**：按正确的依赖顺序插入数据（如先插入学院再插入用户）
3. **错误处理**：包含基本的错误处理和提示
4. **进度提示**：显示插入进度和完成状态

## 注意事项
1. 确保数据库配置正确（.env文件中的数据库连接信息）
2. 确保数据库服务正在运行
3. 确保所需的Python依赖包已安装（参考requirements.txt）
4. 如果遇到bcrypt相关错误，请参考下方故障排除
5. 如果遇到连接问题，请检查数据库配置和网络连接

## 故障排除

### bcrypt版本兼容性问题
如果遇到以下错误：
```
error reading bcrypt version
AttributeError: module 'bcrypt' has no attribute '__about__'
```
这通常是由于bcrypt版本兼容性问题导致的。脚本已经使用项目auth.py中相同的bcrypt实现来解决此问题。

### 密码长度问题
如果遇到以下错误：
```
password cannot be longer than 72 bytes
```
脚本已自动处理此问题，对超过72字节的密码进行截断。

### 数据长度问题
如果遇到以下错误：
```
Data too long for column 'stat_year' at row 1
```
这通常是由于字符串长度超过数据库字段限制。脚本已经修复此问题，使用更短的年份格式。

## 依赖包
脚本依赖以下Python包（已包含在requirements.txt中）：
- fastapi
- SQLAlchemy
- passlib
- python-dotenv
- pymysql
- asyncmy
- bcrypt

## 数据结构说明
1. **用户**：包含1个管理员用户和5个教师用户
2. **角色**：管理员、教师、系主任、学院管理员
3. **学院**：计算机学院、电子学院、机械学院等
4. **评价维度**：教学内容、教学方法、课堂管理、学生参与度、教学效果
5. **课表**：每个教师2-4门课程
6. **评价记录**：8个完整的教学评价数据

运行脚本后，系统将拥有完整的测试数据，可用于功能测试和演示。