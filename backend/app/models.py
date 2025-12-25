from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Boolean, JSON, DECIMAL, ForeignKey, select, \
    UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.base import Base


class User(Base):
    """用户表"""
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='用户ID')
    user_id = Column(String(32), unique=True, nullable=False, comment='工号/账号')
    user_name = Column(String(64), nullable=False, comment='用户名')
    college_id = Column(BigInteger, ForeignKey('college.id'), nullable=True, comment='所属学院ID')
    password = Column(String(128), nullable=False, comment='密码（加密存储）')
    status = Column(Integer, default=1, comment='状态 1-启用 0-禁用')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    is_delete = Column(Boolean, default=False, comment='逻辑删除')
    wx_openid = Column(String(64), comment='微信openid')
    wx_session_key = Column(String(64), comment='用户session_key')
    token = Column(String(64), comment='用户token')
    refresh_token = Column(String(64), comment='用户refresh_token')
    last_login_ip = Column(String(64), comment='最近登录IP')
    nnlg_key = Column(String(128), comment='用户nnlg_key')

    # 关联
    college = relationship("College", back_populates="users")
    roles = relationship("Role", secondary="user_role", back_populates="users")

    def get_permissions(self):
        """获取用户所有权限"""
        permissions = set()
        for role in self.roles:
            if role.status == 1 and not role.is_delete:
                for perm in role.permissions:
                    if not perm.is_delete:
                        permissions.add(perm.permission_code)
        return permissions


class Permission(Base):
    """权限表"""
    __tablename__ = 'permission'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='权限ID')
    permission_code = Column(String(64), unique=True, nullable=False, comment='权限编码')
    permission_name = Column(String(128), nullable=False, comment='权限名称')
    permission_type = Column(Integer, nullable=False, comment='权限类型 1-查看 2-操作 3-导出 4-配置')
    permission_description = Column(String(256), comment='权限描述')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    is_delete = Column(Boolean, default=False, comment='逻辑删除')

    # 关联
    roles = relationship("Role", secondary="role_permission", back_populates="permissions")


class Role(Base):
    """角色表"""
    __tablename__ = 'role'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='角色ID')
    role_code = Column(String(64), unique=True, nullable=False, comment='角色编码')
    role_name = Column(String(128), nullable=False, comment='角色名称')
    description = Column(String(256), comment='角色描述')
    status = Column(Integer, default=1, comment='状态 1-启用 0-禁用')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    is_delete = Column(Boolean, default=False, comment='逻辑删除')

    # 关联
    users = relationship("User", secondary="user_role", back_populates="roles")
    permissions = relationship("Permission", secondary="role_permission", back_populates="roles")


class UserRole(Base):
    """用户-角色关联表"""
    __tablename__ = 'user_role'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False)
    role_id = Column(BigInteger, ForeignKey('role.id'), nullable=False)
    create_time = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uk_user_role'),
    )


class RolePermission(Base):
    """角色-权限关联表"""
    __tablename__ = 'role_permission'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    role_id = Column(BigInteger, ForeignKey('role.id'), nullable=False)
    permission_id = Column(BigInteger, ForeignKey('permission.id'), nullable=False)
    create_time = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
    )


class College(Base):
    __tablename__ = 'college'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='学院ID')
    college_code = Column(String(32), unique=True, nullable=False, comment='学院编码（如01：信息工程学院）')
    college_name = Column(String(64), nullable=False, comment='学院名称')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    is_delete = Column(Boolean, default=False, comment='逻辑删除 0-正常 1-删除')

    # 关联关系
    users = relationship("User", back_populates="college")
    timetables = relationship("Timetable", back_populates="college")
    college_stats = relationship("CollegeEvaluationStat", back_populates="college")


class Timetable(Base):
    __tablename__ = 'timetable'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='课表记录ID')
    timetable_no = Column(String(64), unique=True, nullable=False, comment='课表编号（教务系统同步）')
    college_id = Column(BigInteger, ForeignKey('college.id'), nullable=False, comment='所属学院ID')
    teacher_id = Column(BigInteger, ForeignKey('user.id'), nullable=False, comment='授课教师ID')
    course_name = Column(String(128), nullable=False, comment='课程名称')
    course_type = Column(String(32), nullable=False, comment='课程类型（必修课/选修课/实训课）')
    class_name = Column(String(64), nullable=False, comment='授课班级')
    teach_week = Column(String(64), nullable=False, comment='授课周次（如1-16周）')
    teach_time = Column(String(64), nullable=False, comment='授课时间（如周一第3-4节）')
    teach_place = Column(String(64), nullable=False, comment='授课地点')
    sync_time = Column(DateTime, nullable=False, comment='最后同步时间')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    is_delete = Column(Boolean, default=False, comment='逻辑删除 0-正常 1-删除')

    # 关联关系
    college = relationship("College", back_populates="timetables")
    teacher = relationship("User", back_populates="teach_timetables")
    evaluations = relationship("TeachingEvaluation", back_populates="timetable")


class TeachingEvaluation(Base):
    __tablename__ = 'teaching_evaluation'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='评教记录ID')
    evaluation_no = Column(String(64), unique=True, nullable=False, comment='评教编号（学院编码+年份+随机数）')
    timetable_id = Column(BigInteger, ForeignKey('timetable.id'), nullable=False, comment='关联课表ID')
    teach_teacher_id = Column(BigInteger, ForeignKey('user.id'), nullable=False, comment='授课教师ID')
    listen_teacher_id = Column(BigInteger, ForeignKey('user.id'), nullable=False, comment='听课教师ID')
    total_score = Column(Integer, nullable=False, comment='评教总分（0-100）')
    dimension_scores = Column(JSON, nullable=False, comment='各维度得分（如{"课程导入":20,"互动性":15}）')
    advantage_content = Column(Text, comment='优点描述')
    problem_content = Column(Text, comment='问题描述')
    improve_suggestion = Column(Text, comment='改进建议')
    is_anonymous = Column(Boolean, default=False, comment='是否匿名 0-实名 1-匿名')
    submit_time = Column(DateTime, nullable=False, comment='提交时间')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    is_delete = Column(Boolean, default=False, comment='逻辑删除 0-正常 1-删除')

    # 关联关系
    timetable = relationship("Timetable", back_populates="evaluations")
    teach_teacher = relationship("User", foreign_keys="[teach_teacher_id]", back_populates="evaluation_records")
    listen_teacher = relationship("User", foreign_keys="[listen_teacher_id]", back_populates="listen_evaluations")


class TeacherEvaluationStat(Base):
    __tablename__ = 'teacher_evaluation_stat'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='统计记录ID')
    teacher_id = Column(BigInteger, ForeignKey('user.id'), nullable=False, comment='教师ID')
    college_id = Column(BigInteger, ForeignKey('college.id'), nullable=False, comment='所属学院ID')
    stat_year = Column(String(4), nullable=False, comment='统计年份')
    stat_semester = Column(Integer, nullable=False, comment='统计学期 1-春季 2-秋季')
    total_evaluation_num = Column(Integer, default=0, comment='评教总次数')
    avg_total_score = Column(DECIMAL(5, 2), comment='总分平均分')
    dimension_avg_scores = Column(JSON, comment='各维度平均分')
    school_rank = Column(Integer, comment='全校排名')
    college_rank = Column(Integer, comment='院内排名')
    high_freq_problems = Column(JSON, comment='高频问题')
    high_freq_suggestions = Column(JSON, comment='高频建议')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')


class CollegeEvaluationStat(Base):
    __tablename__ = 'college_evaluation_stat'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='统计记录ID')
    college_id = Column(BigInteger, ForeignKey('college.id'), nullable=False, comment='学院ID')
    stat_year = Column(String(4), nullable=False, comment='统计年份')
    stat_semester = Column(Integer, nullable=False, comment='统计学期 1-春季 2-秋季')
    total_teacher_num = Column(Integer, default=0, comment='参评教师总数')
    avg_total_score = Column(DECIMAL(5, 2), comment='学院总平均分')
    dimension_avg_scores = Column(JSON, comment='学院各维度平均分')
    school_rank = Column(Integer, comment='学院全校排名')
    high_freq_problems = Column(JSON, comment='学院高频问题')
    report_export_num = Column(Integer, default=0, comment='报表导出次数')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联关系
    college = relationship("College", back_populates="college_stats")


class SystemConfig(Base):
    __tablename__ = 'system_config'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='配置ID')
    config_key = Column(String(64), unique=True, nullable=False, comment='配置键（如anonymous_mode、data_visibility）')
    config_value = Column(JSON, nullable=False, comment='配置值')
    config_desc = Column(String(256), nullable=False, comment='配置描述')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    operator_id = Column(BigInteger, ForeignKey('user.id'), nullable=False, comment='操作人ID（学校管理员）')
