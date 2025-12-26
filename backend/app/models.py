from sqlalchemy import (
    Column, BigInteger, String, DateTime, Text, Boolean,
    JSON, DECIMAL, ForeignKey, UniqueConstraint, Index, SmallInteger
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.base import Base


# ==================== 用户权限相关 ====================

class User(Base):
    """用户表"""
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='用户ID')
    user_on = Column(String(32), unique=True, nullable=False, index=True, comment='工号/账号')
    user_name = Column(String(64), nullable=False, comment='用户名')
    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='SET NULL'), nullable=True, index=True,
                        comment='所属学院ID')
    password = Column(String(255), nullable=False, comment='密码（bcrypt加密）')
    status = Column(TINYINT, default=1, index=True, comment='状态 1-启用 0-禁用')

    # Token 相关（无 Redis 时存数据库）
    token = Column(String(512), comment='用户token')
    refresh_token = Column(String(512), comment='用户refresh_token')
    token_expire_time = Column(DateTime, comment='token过期时间')

    # 登录信息
    last_login_time = Column(DateTime, comment='最近登录时间')
    last_login_ip = Column(String(45), comment='最近登录IP（支持IPv6）')
    login_fail_count = Column(TINYINT, default=0, comment='连续登录失败次数')
    lock_until = Column(DateTime, comment='锁定截止时间')

    # 南宁理工教务系统登录key
    nnlg_key = Column(String(128), comment='用户nnlg_key')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    # 关联
    college = relationship("College", back_populates="users")
    roles = relationship("Role", secondary="user_role", back_populates="users", lazy="selectin")
    wechat_bind = relationship("UserWechatBind", back_populates="user", uselist=False)
    teach_timetables = relationship("Timetable", foreign_keys="Timetable.teacher_id", back_populates="teacher")
    evaluation_records = relationship("TeachingEvaluation", foreign_keys="TeachingEvaluation.teach_teacher_id",
                                      back_populates="teach_teacher")
    listen_evaluations = relationship("TeachingEvaluation", foreign_keys="TeachingEvaluation.listen_teacher_id",
                                      back_populates="listen_teacher")

    __table_args__ = (
        Index('idx_user_status_delete', 'status', 'is_delete'),
        Index('idx_user_token', 'token'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '用户表'}
    )

    def get_permissions(self):
        """获取用户所有权限"""
        permissions = set()
        for role in self.roles:
            if role.status == 1 and not role.is_delete:
                for perm in role.permissions:
                    if not perm.is_delete:
                        permissions.add(perm.permission_code)
        return permissions


class UserWechatBind(Base):
    """用户微信绑定表"""
    __tablename__ = 'user_wechat_bind'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True,
                     comment='用户ID')
    openid = Column(String(64), unique=True, nullable=False, index=True, comment='微信openid')
    unionid = Column(String(64), unique=True, nullable=True, index=True, comment='微信unionid')
    session_key = Column(String(64), comment='session_key')
    nickname = Column(String(64), comment='微信昵称')
    avatar_url = Column(String(512), comment='微信头像')
    bind_time = Column(DateTime, server_default=func.now(), comment='绑定时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联
    user = relationship("User", back_populates="wechat_bind")

    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '用户微信绑定表'}
    )


class Permission(Base):
    """权限表"""
    __tablename__ = 'permission'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='权限ID')
    permission_code = Column(String(64), unique=True, nullable=False, index=True, comment='权限编码')
    permission_name = Column(String(128), nullable=False, comment='权限名称')
    permission_type = Column(TINYINT, nullable=False, index=True, comment='权限类型 1-查看 2-操作 3-导出 4-配置')
    parent_id = Column(BigInteger, ForeignKey('permission.id', ondelete='CASCADE'), nullable=True, index=True,
                       comment='父权限ID')
    sort_order = Column(SmallInteger, default=0, comment='排序')
    permission_description = Column(String(256), comment='权限描述')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    # 关联
    roles = relationship("Role", secondary="role_permission", back_populates="permissions")
    parent = relationship("Permission", remote_side=[id], backref="children")

    __table_args__ = (
        Index('idx_permission_type_order', 'permission_type', 'sort_order'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '权限表'}
    )


class Role(Base):
    """角色表"""
    __tablename__ = 'role'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='角色ID')
    role_code = Column(String(64), unique=True, nullable=False, index=True, comment='角色编码')
    role_name = Column(String(128), nullable=False, comment='角色名称')
    role_level = Column(TINYINT, default=0, comment='角色级别（用于权限继承）')
    description = Column(String(256), comment='角色描述')
    status = Column(TINYINT, default=1, index=True, comment='状态 1-启用 0-禁用')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    # 关联
    users = relationship("User", secondary="user_role", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permission", back_populates="roles", lazy="selectin")

    __table_args__ = (
        Index('idx_role_status_delete', 'status', 'is_delete'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '角色表'}
    )


class UserRole(Base):
    """用户-角色关联表"""
    __tablename__ = 'user_role'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = Column(BigInteger, ForeignKey('role.id', ondelete='CASCADE'), nullable=False, index=True)
    create_time = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uk_user_role'),
        {'mysql_charset': 'utf8mb4', 'comment': '用户角色关联表'}
    )


class RolePermission(Base):
    """角色-权限关联表"""
    __tablename__ = 'role_permission'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_id = Column(BigInteger, ForeignKey('role.id', ondelete='CASCADE'), nullable=False, index=True)
    permission_id = Column(BigInteger, ForeignKey('permission.id', ondelete='CASCADE'), nullable=False, index=True)
    create_time = Column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
        {'mysql_charset': 'utf8mb4', 'comment': '角色权限关联表'}
    )


# ==================== 学院与课表 ====================

class College(Base):
    """学院表"""
    __tablename__ = 'college'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='学院ID')
    college_code = Column(String(32), unique=True, nullable=False, index=True, comment='学院编码')
    college_name = Column(String(64), nullable=False, comment='学院名称')
    short_name = Column(String(16), comment='学院简称')
    sort_order = Column(SmallInteger, default=0, comment='排序')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    # 关联
    users = relationship("User", back_populates="college")
    timetables = relationship("Timetable", back_populates="college")
    college_stats = relationship("CollegeEvaluationStat", back_populates="college")
    teacher_stats = relationship("TeacherEvaluationStat", back_populates="college")

    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '学院表'}
    )


class Timetable(Base):
    """课表"""
    __tablename__ = 'timetable'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='课表记录ID')
    timetable_no = Column(String(64), unique=True, nullable=False, index=True, comment='课表编号')
    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='RESTRICT'), nullable=False, index=True,
                        comment='所属学院ID')
    teacher_id = Column(BigInteger, ForeignKey('user.id', ondelete='RESTRICT'), nullable=False, index=True,
                        comment='授课教师ID')

    # 课程信息
    course_code = Column(String(32), nullable=True, index=True, comment='课程编码')
    course_name = Column(String(128), nullable=False, index=True, comment='课程名称')
    course_type = Column(String(32), nullable=False, index=True, comment='课程类型（必修课/选修课/实训课）')
    class_name = Column(String(128), nullable=False, comment='授课班级')
    student_count = Column(SmallInteger, comment='学生人数')
    credit = Column(DECIMAL(3, 1), comment='学分')

    # 学期信息（结构化）
    academic_year = Column(String(9), nullable=False, index=True, comment='学年（如2024-2025）')
    semester = Column(TINYINT, nullable=False, index=True, comment='学期 1-春季 2-秋季')

    # 时间信息（结构化，便于查询）
    teach_week_start = Column(TINYINT, comment='起始周次')
    teach_week_end = Column(TINYINT, comment='结束周次')
    weekday = Column(TINYINT, comment='星期几 1-7')
    period_start = Column(TINYINT, comment='开始节次')
    period_end = Column(TINYINT, comment='结束节次')

    # 原始格式（保留兼容性）
    teach_week = Column(String(64), nullable=False, comment='授课周次（如1-16周）')
    teach_time = Column(String(64), nullable=False, comment='授课时间（如周一第3-4节）')
    teach_place = Column(String(64), nullable=False, comment='授课地点')

    # 同步信息
    sync_time = Column(DateTime, nullable=False, comment='最后同步时间')
    sync_status = Column(TINYINT, default=1, comment='同步状态 1-成功 0-失败')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    # 关联
    college = relationship("College", back_populates="timetables")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teach_timetables")
    evaluations = relationship("TeachingEvaluation", back_populates="timetable")

    __table_args__ = (
        Index('idx_timetable_college_teacher', 'college_id', 'teacher_id'),
        Index('idx_timetable_year_semester', 'academic_year', 'semester'),
        Index('idx_timetable_schedule', 'weekday', 'period_start'),
        Index('idx_timetable_course', 'course_code', 'course_name'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '课表'}
    )


# ==================== 评价相关 ====================

class EvaluationDimension(Base):
    """评价维度配置表"""
    __tablename__ = 'evaluation_dimension'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    dimension_code = Column(String(32), unique=True, nullable=False, index=True, comment='维度编码')
    dimension_name = Column(String(64), nullable=False, comment='维度名称')
    max_score = Column(TINYINT, nullable=False, default=20, comment='该维度最高分')
    weight = Column(DECIMAL(3, 2), nullable=False, default=1.00, comment='权重')
    sort_order = Column(SmallInteger, default=0, comment='排序')
    description = Column(String(256), comment='维度说明')
    scoring_criteria = Column(JSON, comment='评分标准说明')
    is_required = Column(Boolean, default=True, comment='是否必填')
    status = Column(TINYINT, default=1, comment='状态 1-启用 0-禁用')
    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_delete = Column(Boolean, default=False, index=True)

    __table_args__ = (
        Index('idx_dimension_status_order', 'status', 'sort_order'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '评价维度配置表'}
    )


class TeachingEvaluation(Base):
    """教学评价表"""
    __tablename__ = 'teaching_evaluation'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='评教记录ID')
    evaluation_no = Column(String(64), unique=True, nullable=False, index=True, comment='评教编号')
    timetable_id = Column(BigInteger, ForeignKey('timetable.id', ondelete='RESTRICT'), nullable=False, index=True,
                          comment='关联课表ID')
    teach_teacher_id = Column(BigInteger, ForeignKey('user.id', ondelete='RESTRICT'), nullable=False, index=True,
                              comment='授课教师ID')
    listen_teacher_id = Column(BigInteger, ForeignKey('user.id', ondelete='RESTRICT'), nullable=False, index=True,
                               comment='听课教师ID')

    # 评分信息
    total_score = Column(TINYINT, nullable=False, comment='评教总分（0-100）')
    dimension_scores = Column(JSON, nullable=False, comment='各维度得分')
    score_level = Column(String(8), index=True, comment='等级（优秀/良好/合格/不合格）')

    # 评价内容
    advantage_content = Column(Text, comment='优点描述')
    problem_content = Column(Text, comment='问题描述')
    improve_suggestion = Column(Text, comment='改进建议')

    # 听课信息
    listen_date = Column(DateTime, nullable=False, index=True, comment='实际听课日期')
    listen_duration = Column(SmallInteger, comment='听课时长（分钟）')
    listen_location = Column(String(64), comment='实际听课地点')

    # 状态信息
    is_anonymous = Column(Boolean, default=False, comment='是否匿名')
    status = Column(TINYINT, default=1, index=True, comment='状态 1-有效 0-作废 2-待审核')

    submit_time = Column(DateTime, nullable=False, index=True, comment='提交时间')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    # 关联
    timetable = relationship("Timetable", back_populates="evaluations")
    teach_teacher = relationship("User", foreign_keys=[teach_teacher_id], back_populates="evaluation_records")
    listen_teacher = relationship("User", foreign_keys=[listen_teacher_id], back_populates="listen_evaluations")

    __table_args__ = (
        # 防止同一听课教师对同一课表同一天重复评价
        UniqueConstraint('timetable_id', 'listen_teacher_id', 'listen_date', name='uk_evaluation_unique'),
        Index('idx_evaluation_teachers', 'teach_teacher_id', 'listen_teacher_id'),
        Index('idx_evaluation_submit', 'submit_time', 'is_delete'),
        Index('idx_evaluation_score_level', 'score_level', 'status'),
        Index('idx_evaluation_listen_date', 'listen_date', 'status'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '教学评价表'}
    )


# ==================== 统计相关 ====================

class TeacherEvaluationStat(Base):
    """教师评价统计表"""
    __tablename__ = 'teacher_evaluation_stat'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='统计记录ID')
    teacher_id = Column(BigInteger, ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True,
                        comment='教师ID')
    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='CASCADE'), nullable=False, index=True,
                        comment='所属学院ID')
    stat_year = Column(String(9), nullable=False, index=True, comment='统计学年（如2024-2025）')
    stat_semester = Column(TINYINT, nullable=False, comment='统计学期 1-春季 2-秋季')

    # 统计数据
    total_evaluation_num = Column(SmallInteger, default=0, comment='评教总次数')
    avg_total_score = Column(DECIMAL(5, 2), comment='总分平均分')
    max_score = Column(TINYINT, comment='最高分')
    min_score = Column(TINYINT, comment='最低分')
    dimension_avg_scores = Column(JSON, comment='各维度平均分')

    # 排名
    school_rank = Column(SmallInteger, comment='全校排名')
    school_total = Column(SmallInteger, comment='全校参评教师总数')
    college_rank = Column(SmallInteger, comment='院内排名')
    college_total = Column(SmallInteger, comment='院内参评教师总数')

    # 问题分析
    high_freq_problems = Column(JSON, comment='高频问题')
    high_freq_suggestions = Column(JSON, comment='高频建议')
    score_distribution = Column(JSON, comment='分数分布（优秀/良好/合格/不合格数量）')

    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # 关联
    teacher = relationship("User", foreign_keys=[teacher_id])
    college = relationship("College", back_populates="teacher_stats")

    __table_args__ = (
        UniqueConstraint('teacher_id', 'stat_year', 'stat_semester', name='uk_teacher_stat_period'),
        Index('idx_teacher_stat_year_semester', 'stat_year', 'stat_semester'),
        Index('idx_teacher_stat_college', 'college_id', 'stat_year', 'stat_semester'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '教师评价统计表'}
    )


class CollegeEvaluationStat(Base):
    """学院评价统计表"""
    __tablename__ = 'college_evaluation_stat'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='统计记录ID')
    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='CASCADE'), nullable=False, index=True,
                        comment='学院ID')
    stat_year = Column(String(9), nullable=False, index=True, comment='统计学年')
    stat_semester = Column(TINYINT, nullable=False, comment='统计学期 1-春季 2-秋季')

    # 统计数据
    total_teacher_num = Column(SmallInteger, default=0, comment='参评教师总数')
    total_evaluation_num = Column(SmallInteger, default=0, comment='评价总次数')
    avg_total_score = Column(DECIMAL(5, 2), comment='学院总平均分')
    dimension_avg_scores = Column(JSON, comment='学院各维度平均分')

    # 排名
    school_rank = Column(SmallInteger, comment='学院全校排名')
    school_total = Column(SmallInteger, comment='参评学院总数')

    # 分析数据
    high_freq_problems = Column(JSON, comment='学院高频问题')
    score_distribution = Column(JSON, comment='分数分布')
    excellent_rate = Column(DECIMAL(5, 2), comment='优秀率')

    # 导出记录
    report_export_num = Column(SmallInteger, default=0, comment='报表导出次数')
    last_export_time = Column(DateTime, comment='最后导出时间')

    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # 关联
    college = relationship("College", back_populates="college_stats")

    __table_args__ = (
        UniqueConstraint('college_id', 'stat_year', 'stat_semester', name='uk_college_stat_period'),
        Index('idx_college_stat_year_semester', 'stat_year', 'stat_semester'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '学院评价统计表'}
    )


# ==================== 系统配置与日志 ====================

class SystemConfig(Base):
    """系统配置表"""
    __tablename__ = 'system_config'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='配置ID')
    config_key = Column(String(64), unique=True, nullable=False, index=True, comment='配置键')
    config_value = Column(JSON, nullable=False, comment='配置值')
    config_type = Column(String(32), default='string', comment='配置类型（string/number/boolean/json）')
    config_desc = Column(String(256), nullable=False, comment='配置描述')
    is_public = Column(Boolean, default=False, comment='是否前端可见')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    operator_id = Column(BigInteger, ForeignKey('user.id', ondelete='SET NULL'), nullable=True, index=True,
                         comment='操作人ID')

    # 关联
    operator = relationship("User", foreign_keys=[operator_id])

    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '系统配置表'}
    )


class OperationLog(Base):
    """操作日志表 - 建议保留90天，定期归档"""
    __tablename__ = 'operation_log'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='SET NULL'), nullable=True, index=True,
                     comment='操作用户ID')
    user_name = Column(String(64), comment='操作用户名（冗余，防止用户删除后丢失）')
    operation_type = Column(String(32), nullable=False, index=True, comment='操作类型')
    module = Column(String(32), nullable=False, index=True, comment='模块')
    target_id = Column(BigInteger, comment='操作目标ID')
    target_type = Column(String(32), comment='操作目标类型')
    content = Column(JSON, comment='操作详情')
    before_data = Column(JSON, comment='操作前数据')
    after_data = Column(JSON, comment='操作后数据')
    ip_address = Column(String(45), comment='IP地址')
    user_agent = Column(String(512), comment='User-Agent')
    request_url = Column(String(256), comment='请求URL')
    request_method = Column(String(10), comment='请求方法')
    response_code = Column(SmallInteger, comment='响应状态码')
    execute_time = Column(SmallInteger, comment='执行耗时(ms)')
    create_time = Column(DateTime, server_default=func.now(), index=True, comment='创建时间')
    create_date = Column(String(10), nullable=False, index=True, comment='创建日期(YYYY-MM-DD)，用于分区和归档')

    __table_args__ = (
        Index('idx_log_user_time', 'user_id', 'create_time'),
        Index('idx_log_module_type', 'module', 'operation_type'),
        Index('idx_log_target', 'target_type', 'target_id'),
        Index('idx_log_date', 'create_date'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '操作日志表'}
    )


class LoginLog(Base):
    """登录日志表 - 建议保留180天"""
    __tablename__ = 'login_log'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='SET NULL'), nullable=True, index=True)
    user_name = Column(String(64), comment='用户名/工号')
    login_type = Column(String(16), nullable=False, comment='登录类型（PASSWORD/WECHAT/TOKEN）')
    login_status = Column(TINYINT, nullable=False, comment='登录状态 1-成功 0-失败')
    fail_reason = Column(String(128), comment='失败原因')
    ip_address = Column(String(45), comment='IP地址')
    location = Column(String(64), comment='登录地点')
    device_type = Column(String(32), comment='设备类型（PC/MOBILE/TABLET）')
    browser = Column(String(64), comment='浏览器')
    os = Column(String(64), comment='操作系统')
    user_agent = Column(String(512), comment='User-Agent')
    create_time = Column(DateTime, server_default=func.now(), index=True, comment='登录时间')
    create_date = Column(String(10), nullable=False, index=True, comment='创建日期(YYYY-MM-DD)')

    __table_args__ = (
        Index('idx_login_user_time', 'user_id', 'create_time'),
        Index('idx_login_status_time', 'login_status', 'create_time'),
        Index('idx_login_date', 'create_date'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '登录日志表'}
    )


class OperationLogArchive(Base):
    """操作日志归档表 - 存储超过90天的历史日志"""
    __tablename__ = 'operation_log_archive'

    id = Column(BigInteger, primary_key=True, comment='原日志ID')
    user_id = Column(BigInteger, nullable=True, comment='操作用户ID')
    user_name = Column(String(64), comment='操作用户名')
    operation_type = Column(String(32), nullable=False, comment='操作类型')
    module = Column(String(32), nullable=False, comment='模块')
    target_id = Column(BigInteger, comment='操作目标ID')
    target_type = Column(String(32), comment='操作目标类型')
    content = Column(JSON, comment='操作详情')
    ip_address = Column(String(45), comment='IP地址')
    create_time = Column(DateTime, index=True, comment='创建时间')
    create_date = Column(String(10), index=True, comment='创建日期')
    archive_time = Column(DateTime, server_default=func.now(), comment='归档时间')

    __table_args__ = (
        Index('idx_archive_date', 'create_date'),
        Index('idx_archive_user', 'user_id', 'create_time'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '操作日志归档表'}
    )


class LoginLogArchive(Base):
    """登录日志归档表 - 存储超过180天的历史日志"""
    __tablename__ = 'login_log_archive'

    id = Column(BigInteger, primary_key=True, comment='原日志ID')
    user_id = Column(BigInteger, nullable=True, comment='用户ID')
    user_name = Column(String(64), comment='用户名')
    login_type = Column(String(16), nullable=False, comment='登录类型')
    login_status = Column(TINYINT, nullable=False, comment='登录状态')
    ip_address = Column(String(45), comment='IP地址')
    location = Column(String(64), comment='登录地点')
    create_time = Column(DateTime, index=True, comment='登录时间')
    create_date = Column(String(10), index=True, comment='创建日期')
    archive_time = Column(DateTime, server_default=func.now(), comment='归档时间')

    __table_args__ = (
        Index('idx_login_archive_date', 'create_date'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '登录日志归档表'}
    )
