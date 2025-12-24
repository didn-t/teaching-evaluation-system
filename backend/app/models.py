from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Boolean, JSON, DECIMAL, ForeignKey, select
from sqlalchemy.orm import relationship
from datetime import datetime
from app.base import Base


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


class PermissionDict(Base):
    __tablename__ = 'permission_dict'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='权限ID')
    permission_code = Column(String(64), unique=True, nullable=False, comment='权限编码（唯一）')
    permission_name = Column(String(128), nullable=False, comment='权限名称')
    permission_type = Column(Integer, nullable=False, comment='权限类型 1-数据查看 2-操作管理 3-报表导出 4-系统配置')
    parent_id = Column(BigInteger, default=0, comment='父权限ID（0=顶级权限）')
    sort = Column(Integer, default=0, comment='排序值')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    is_delete = Column(Boolean, default=False, comment='逻辑删除 0-正常 1-删除')

    # 关联关系
    user_permissions = relationship("UserPermission", back_populates="permission")


class User(Base):
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='用户ID')
    user_no = Column(String(32), unique=True, nullable=False, comment='工号/账号')
    user_name = Column(String(64), nullable=False, comment='用户名')
    role_type = Column(Integer, nullable=False, comment='角色类型 1-普通教师 2-督导 3-学院管理员 4-学校管理员')
    college_id = Column(BigInteger, ForeignKey('college.id'), nullable=False, comment='所属学院ID')
    password = Column(String(128), nullable=False, comment='密码（加密存储）')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    is_delete = Column(Boolean, default=False, comment='逻辑删除 0-正常 1-删除')
    wx_openid = Column(String(64), comment='微信openid')

    # 关联关系
    college = relationship("College", back_populates="users")
    teach_timetables = relationship("Timetable", foreign_keys="[Timetable.teacher_id]", back_populates="teacher")
    evaluation_records = relationship("TeachingEvaluation", foreign_keys="[TeachingEvaluation.teach_teacher_id]",
                                      back_populates="teach_teacher")
    listen_evaluations = relationship("TeachingEvaluation", foreign_keys="[TeachingEvaluation.listen_teacher_id]",
                                      back_populates="listen_teacher")
    permissions = relationship("UserPermission", back_populates="user")
    user_permissions = relationship("UserPermission", foreign_keys="[UserPermission.operator_id]",
                                    back_populates="operator")

    @classmethod
    async def get_by_user_no(cls, session, user_no: str):
        stmt = select(cls).where(cls.user_no == user_no)
        result = await session.execute(stmt)
        return result.scalars().first()


class UserPermission(Base):
    __tablename__ = 'user_permission'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='关联ID')
    user_id = Column(BigInteger, ForeignKey('user.id'), nullable=False, comment='用户ID')
    permission_id = Column(BigInteger, ForeignKey('permission_dict.id'), nullable=False,
                           comment='权限ID（关联permission_dict）')
    scope_college_ids = Column(JSON, comment='权限生效范围（如["1","2"]=仅1/2学院生效）')
    create_time = Column(DateTime, default=datetime.now, comment='绑定时间')
    operator_id = Column(BigInteger, ForeignKey('user.id'), nullable=False, comment='授权人ID（学校管理员）')
    is_delete = Column(Boolean, default=False, comment='逻辑删除 0-正常 1-删除')

    # 关联关系
    user = relationship("User", back_populates="permissions")
    permission = relationship("PermissionDict", back_populates="user_permissions")
    operator = relationship("User", foreign_keys=[operator_id], back_populates="user_permissions")


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
    teach_teacher = relationship("User", foreign_keys=[teach_teacher_id], back_populates="evaluation_records")
    listen_teacher = relationship("User", foreign_keys=[listen_teacher_id], back_populates="listen_evaluations")


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
