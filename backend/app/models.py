from sqlalchemy import (
    Column, BigInteger, String, DateTime, Text, Boolean,
    JSON, DECIMAL, ForeignKey, UniqueConstraint, Index, SmallInteger
)
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.base import Base


# =========================================================
#  用户 / 权限
# =========================================================

class User(Base):
    """用户表：系统登录主体（教师/管理员等都属于用户）"""
    __tablename__ = 'user'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='用户ID')
    user_on = Column(String(32), unique=True, nullable=False, index=True, comment='工号/账号')
    user_name = Column(String(64), nullable=False, comment='用户名/姓名')

    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='SET NULL'),
                        nullable=True, index=True, comment='所属学院ID（可空）')

    password = Column(String(255), nullable=False, comment='密码（bcrypt加密）')
    status = Column(TINYINT, default=1, index=True, comment='状态 1-启用 0-禁用')

    # Token（无 Redis 时可用）
    token = Column(String(512), comment='用户token')
    refresh_token = Column(String(512), comment='refresh_token')
    token_expire_time = Column(DateTime, comment='token过期时间')

    # 登录信息
    last_login_time = Column(DateTime, comment='最近登录时间')
    last_login_ip = Column(String(45), comment='最近登录IP（支持IPv6）')
    login_fail_count = Column(TINYINT, default=0, comment='连续登录失败次数')
    lock_until = Column(DateTime, comment='锁定截止时间')

    # 教务系统登录Key（可选）
    nnlg_key = Column(String(128), comment='教务系统登录key（可选）')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    # 推荐保留：软删除避免历史记录断链
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    # 关联
    college = relationship("College", back_populates="users")
    roles = relationship("Role", secondary="user_role", back_populates="users", lazy="selectin")
    wechat_bind = relationship("UserWechatBind", back_populates="user", uselist=False)

    # 教师扩展档案（可选，不影响系统独立运行）
    teacher_profile = relationship("TeacherProfile", back_populates="user", uselist=False)

    # 课表：此用户作为授课教师
    teach_timetables = relationship("Timetable", foreign_keys="Timetable.teacher_id", back_populates="teacher")

    # 评教：被评价的教师 / 听课评价人（都是 User）
    evaluation_records = relationship(
        "TeachingEvaluation",
        foreign_keys="TeachingEvaluation.teach_teacher_id",
        back_populates="teach_teacher"
    )
    listen_evaluations = relationship(
        "TeachingEvaluation",
        foreign_keys="TeachingEvaluation.listen_teacher_id",
        back_populates="listen_teacher"
    )

    __table_args__ = (
        Index('idx_user_status_delete', 'status', 'is_delete'),
        Index('idx_user_token', 'token'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '用户表'}
    )

    def get_permissions(self):
        """获取用户所有权限编码集合"""
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

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='绑定ID')
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False, unique=True, comment='用户ID')
    openid = Column(String(64), unique=True, nullable=False, index=True, comment='微信openid')
    unionid = Column(String(64), unique=True, nullable=True, index=True, comment='微信unionid（可空）')
    session_key = Column(String(64), comment='session_key（可空）')
    nickname = Column(String(64), comment='微信昵称（可空）')
    avatar_url = Column(String(512), comment='微信头像（可空）')
    bind_time = Column(DateTime, server_default=func.now(), comment='绑定时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    user = relationship("User", back_populates="wechat_bind")

    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '用户微信绑定表'}
    )


class Permission(Base):
    """权限表：菜单/按钮等权限点"""
    __tablename__ = 'permission'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='权限ID')
    permission_code = Column(String(64), unique=True, nullable=False, index=True, comment='权限编码')
    permission_name = Column(String(128), nullable=False, comment='权限名称')
    permission_type = Column(TINYINT, nullable=False, index=True, comment='权限类型 1-查看 2-操作 3-导出 4-配置')
    parent_id = Column(BigInteger, ForeignKey('permission.id', ondelete='CASCADE'),
                       nullable=True, index=True, comment='父权限ID（可空）')
    sort_order = Column(SmallInteger, default=0, comment='排序')
    permission_description = Column(String(256), comment='权限描述（可空）')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

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
    role_level = Column(TINYINT, default=0, comment='角色级别（用于权限继承/排序）')
    description = Column(String(256), comment='角色描述（可空）')
    status = Column(TINYINT, default=1, index=True, comment='状态 1-启用 0-禁用')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

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
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')

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
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
        {'mysql_charset': 'utf8mb4', 'comment': '角色权限关联表'}
    )


# =========================================================
#  校区 / 学院 / 教研室 / 专业 / 班级 / 教师档案
# =========================================================

class Campus(Base):
    """校区表：学校的不同校区"""
    __tablename__ = 'campus'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='校区ID')
    campus_name = Column(String(64), nullable=False, unique=True, comment='校区名称')
    sort_order = Column(SmallInteger, default=0, comment='排序')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    colleges = relationship("College", back_populates="campus")

    __table_args__ = (
        Index('idx_campus_delete', 'is_delete'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '校区表'}
    )


class College(Base):
    """学院表：基础组织维度"""
    __tablename__ = 'college'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='学院ID')
    college_code = Column(String(32), unique=True, nullable=False, index=True, comment='学院编码')
    college_name = Column(String(64), nullable=False, comment='学院名称')
    short_name = Column(String(16), comment='学院简称（可空）')
    sort_order = Column(SmallInteger, default=0, comment='排序')

    campus_id = Column(BigInteger, ForeignKey('campus.id', ondelete='SET NULL'), nullable=True, index=True, comment='校区ID')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    campus = relationship("Campus", back_populates="colleges")
    users = relationship("User", back_populates="college")
    timetables = relationship("Timetable", back_populates="college")

    research_rooms = relationship("ResearchRoom", back_populates="college", cascade="all, delete-orphan")
    majors = relationship("Major", back_populates="college", cascade="all, delete-orphan")

    college_stats = relationship("CollegeEvaluationStat", back_populates="college")
    teacher_stats = relationship("TeacherEvaluationStat", back_populates="college")

    __table_args__ = (
        Index('idx_college_delete', 'is_delete'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '学院表'}
    )


class ResearchRoom(Base):
    """教研室表：学院下属教研室"""
    __tablename__ = 'research_room'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='教研室ID')
    room_name = Column(String(64), nullable=False, comment='教研室名称')
    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='RESTRICT'),
                        nullable=False, index=True, comment='学院ID')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    college = relationship("College", back_populates="research_rooms")
    teacher_profiles = relationship("TeacherProfile", back_populates="research_room")

    __table_args__ = (
        UniqueConstraint('college_id', 'room_name', name='uk_room_college_name'),
        Index('idx_room_delete', 'is_delete'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '教研室表'}
    )


class Major(Base):
    """专业表：学院下属专业"""
    __tablename__ = 'major'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='专业ID')
    major_code = Column(String(32), unique=True, nullable=True, index=True, comment='专业编码（可空）')
    major_name = Column(String(64), nullable=False, comment='专业名称')
    short_name = Column(String(32), comment='专业简称（可空）')
    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='RESTRICT'),
                        nullable=False, index=True, comment='学院ID')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    college = relationship("College", back_populates="majors")
    classes = relationship("Clazz", back_populates="major", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_major_delete', 'is_delete'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '专业表'}
    )


class Clazz(Base):
    """班级表：专业下属班级"""
    __tablename__ = 'clazz'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='班级ID')
    class_code = Column(String(32), unique=True, nullable=True, index=True, comment='班级编号（可空）')
    class_name = Column(String(64), nullable=False, index=True, comment='班级名称')
    grade = Column(String(16), comment='年级（可空）')

    major_id = Column(BigInteger, ForeignKey('major.id', ondelete='SET NULL'),
                      nullable=True, index=True, comment='专业ID（可空）')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    major = relationship("Major", back_populates="classes")
    timetables = relationship("Timetable", back_populates="clazz")

    __table_args__ = (
        Index('idx_clazz_delete', 'is_delete'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '班级表'}
    )


class TeacherProfile(Base):
    """
    教师扩展档案表（可选）：
    - 系统运行的“教师身份”仍然用 User（Timetable.teacher_id -> user.id）
    - 该表只承载：职称/教研室/教务映射等扩展信息，不绑定则不影响功能
    """
    __tablename__ = 'teacher_profile'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='教师档案ID')
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='CASCADE'),
                     nullable=False, unique=True, index=True, comment='用户ID（user.id）')

    title = Column(String(32), comment='职称（可空）')
    research_room_id = Column(BigInteger, ForeignKey('research_room.id', ondelete='SET NULL'),
                              nullable=True, index=True, comment='教研室ID（可空）')

    # 教务接入：外部教师唯一ID（可空）
    external_id = Column(String(64), nullable=True, index=True, comment='教务教师唯一ID（可空）')
    raw_payload = Column(JSON, comment='教务原始数据（可空）')
    sync_time = Column(DateTime, comment='最后同步时间（可空）')
    sync_status = Column(TINYINT, default=1, comment='同步状态 1-成功 0-失败')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    user = relationship("User", back_populates="teacher_profile")
    research_room = relationship("ResearchRoom", back_populates="teacher_profiles")

    __table_args__ = (
        UniqueConstraint('external_id', name='uk_teacher_profile_external_id'),
        Index('idx_teacher_profile_delete', 'is_delete'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '教师扩展档案表'}
    )


class SupervisorScope(Base):
    """22300417陈俫坤开发：督导负责范围配置

    支持：
    - 多学院（scope_type='college'）
    - 多教研组（scope_type='research_room'）

    注意：若某督导未配置范围，业务侧可回退到 current_user.college_id。
    """

    __tablename__ = 'supervisor_scope'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='督导范围ID')

    supervisor_user_id = Column(
        BigInteger,
        ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='督导用户ID（user.id）',
    )

    scope_type = Column(String(16), nullable=False, index=True, comment="范围类型 college/research_room")
    scope_id = Column(BigInteger, nullable=False, index=True, comment='范围对象ID')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    supervisor_user = relationship('User')

    __table_args__ = (
        UniqueConstraint('supervisor_user_id', 'scope_type', 'scope_id', name='uk_supervisor_scope'),
        Index('idx_supervisor_scope_user_type', 'supervisor_user_id', 'scope_type'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '督导负责范围配置'}
    )


# =========================================================
#  课表（核心业务：适配你的JSON课表数据）
# =========================================================

class Timetable(Base):
    """
    课表表（课程安排/课表槽位）——评教的“被评价对象”来源之一
    适配导入数据：
      - 班级(class_name)
      - 星期(weekday/weekday_text)
      - 节次(period)       -> 只会“大节”，如：第一大节
      - 小节范围(section_time) -> 如：01-02
      - 周次(week_info)     -> 仅逗号列表：1,2,3,4...
      - 教室(classroom)
    """
    __tablename__ = 'timetable'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='课表记录ID')

    # 学院维度：可从教师/班级推导，但保留便于筛选与统计（可空）
    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='SET NULL'),
                        nullable=True, index=True, comment='所属学院ID（可空）')

    # 授课教师：用 User 统一身份（系统可独立运行）
    teacher_id = Column(BigInteger, ForeignKey('user.id', ondelete='RESTRICT'),
                        nullable=False, index=True, comment='授课教师ID（user.id）')

    # 班级：既支持维表，也支持仅存文本（建议两者都填，导入时可先填文本）
    class_id = Column(BigInteger, ForeignKey('clazz.id', ondelete='SET NULL'),
                      nullable=True, index=True, comment='班级ID（可空）')
    class_name = Column(String(128), nullable=False, comment='授课班级名称（快照）')

    # 课程信息
    course_code = Column(String(32), nullable=True, index=True, comment='课程编码（可空）')
    course_name = Column(String(128), nullable=False, index=True, comment='课程名称')

    # 学期信息：建议必填，评教统计/归档强依赖（你可以在导入时统一写入当前学期）
    academic_year = Column(String(9), nullable=False, index=True, comment='学年（如2024-2025）')
    semester = Column(TINYINT, nullable=False, index=True, comment='学期 1-春季 2-秋季')

    # 上课安排（与你的JSON一致）
    weekday = Column(TINYINT, nullable=False, index=True, comment='星期 1-7')
    weekday_text = Column(String(8), comment='星期文本（可空，如星期四）')

    period = Column(String(16), nullable=False, comment='节次（大节，如第一大节）')
    section_time = Column(String(16), nullable=False, comment='小节范围（如01-02）')
    week_info = Column(String(128), nullable=False, comment='上课周次（逗号列表，如1,2,3,4,...)')
    classroom = Column(String(128), default='', nullable=False, comment='教室（空字符串表示未知）')

    # 可选：课程容量信息（独立运行可不填；教务接入可填）
    student_count = Column(SmallInteger, comment='学生人数（可空）')
    credit = Column(DECIMAL(3, 1), comment='学分（可空）')
    course_type = Column(String(32), comment='待评，已评')

    # 教务接入：可插拔
    sync_source = Column(TINYINT, default=0, comment='数据来源 0-手工/系统内 1-教务')
    external_id = Column(String(64), nullable=True, index=True, comment='教务课表唯一ID（可空）')
    raw_payload = Column(JSON, comment='教务原始数据（可空）')
    sync_time = Column(DateTime, comment='最后同步时间（可空）')
    sync_status = Column(TINYINT, default=1, comment='同步状态 1-成功 0-失败')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    # 关联
    college = relationship("College", back_populates="timetables")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teach_timetables")
    clazz = relationship("Clazz", back_populates="timetables")
    evaluations = relationship("TeachingEvaluation", back_populates="timetable")

    __table_args__ = (
        # 教务幂等：同来源+外部ID唯一（external_id 为空时不影响）
        UniqueConstraint('sync_source', 'external_id', name='uk_timetable_source_external'),

        # 手工/无外部ID时：用“课表槽位”防重复（覆盖你JSON的全部字段）
        UniqueConstraint(
            'academic_year', 'semester',
            'teacher_id', 'class_name', 'course_name',
            'weekday', 'period', 'section_time', 'week_info', 'classroom',
            name='uk_timetable_slot'
        ),

        Index('idx_timetable_college_teacher', 'college_id', 'teacher_id'),
        Index('idx_timetable_year_semester', 'academic_year', 'semester'),
        Index('idx_timetable_schedule', 'weekday', 'period'),
        Index('idx_timetable_delete', 'is_delete'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '课表表'}
    )


# =========================================================
#  评价相关
# =========================================================

class EvaluationDimension(Base):
    """评价维度配置：用于动态配置评分项"""
    __tablename__ = 'evaluation_dimension'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='维度ID')
    dimension_code = Column(String(32), unique=True, nullable=False, index=True, comment='维度编码')
    dimension_name = Column(String(64), nullable=False, comment='维度名称')

    max_score = Column(TINYINT, nullable=False, default=20, comment='该维度最高分')
    weight = Column(DECIMAL(3, 2), nullable=False, default=1.00, comment='权重')
    sort_order = Column(SmallInteger, default=0, comment='排序')

    description = Column(String(256), comment='维度说明（可空）')
    scoring_criteria = Column(JSON, comment='评分标准说明（可空）')

    is_required = Column(Boolean, default=True, comment='是否必填')
    status = Column(TINYINT, default=1, comment='状态 1-启用 0-禁用')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

    __table_args__ = (
        Index('idx_dimension_status_order', 'status', 'sort_order'),
        Index('idx_dimension_delete', 'is_delete'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '评价维度配置表'}
    )


class TeachingEvaluation(Base):
    """教学评价表：一次听课/评教记录"""
    __tablename__ = 'teaching_evaluation'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='评教记录ID')
    evaluation_no = Column(String(64), unique=True, nullable=False, index=True, comment='评教编号')

    timetable_id = Column(BigInteger, ForeignKey('timetable.id', ondelete='RESTRICT'),
                          nullable=False, index=True, comment='关联课表ID')

    # 冗余快照：避免后续课表教师变更导致历史记录对不上（也便于查询）
    teach_teacher_id = Column(BigInteger, ForeignKey('user.id', ondelete='RESTRICT'),
                              nullable=False, index=True, comment='授课教师ID（user.id）')

    # 听课教师：发起评教的人
    listen_teacher_id = Column(BigInteger, ForeignKey('user.id', ondelete='RESTRICT'),
                               nullable=False, index=True, comment='听课教师ID（user.id）')

    eval_source = Column(String(16), nullable=True, index=True, comment='评教来源（peer/supervisor，可空）')

    # 评分
    total_score = Column(TINYINT, nullable=False, comment='评教总分（0-100）')
    dimension_scores = Column(JSON, nullable=False, comment='各维度得分（JSON）')
    score_level = Column(String(8), index=True, comment='等级（优秀/良好/合格/不合格，可空）')

    # 文本反馈
    advantage_content = Column(Text, comment='优点描述（可空）')
    problem_content = Column(Text, comment='问题描述（可空）')
    improve_suggestion = Column(Text, comment='改进建议（可空）')

    # 听课信息
    listen_date = Column(DateTime, nullable=False, index=True, comment='实际听课日期')
    listen_duration = Column(SmallInteger, comment='听课时长（分钟，可空）')
    listen_location = Column(String(128), comment='实际听课地点（可空）')

    is_anonymous = Column(Boolean, default=False, comment='是否匿名')
    status = Column(TINYINT, default=1, index=True, comment='状态 1-有效 0-作废 2-待审核')

    submit_time = Column(DateTime, nullable=False, index=True, comment='提交时间')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')
    is_delete = Column(Boolean, default=False, index=True, comment='逻辑删除')

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


# =========================================================
#  统计相关（保持你原思路：按学年学期聚合）
# =========================================================

class TeacherEvaluationStat(Base):
    """教师评价统计表：按学年/学期聚合"""
    __tablename__ = 'teacher_evaluation_stat'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='统计记录ID')
    teacher_id = Column(BigInteger, ForeignKey('user.id', ondelete='CASCADE'),
                        nullable=False, index=True, comment='教师ID（user.id）')
    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='CASCADE'),
                        nullable=False, index=True, comment='所属学院ID')

    stat_year = Column(String(9), nullable=False, index=True, comment='统计学年（如2024-2025）')
    stat_semester = Column(TINYINT, nullable=False, comment='统计学期 1-春季 2-秋季')

    total_evaluation_num = Column(SmallInteger, default=0, comment='评教总次数')
    avg_total_score = Column(DECIMAL(5, 2), comment='总分平均分（可空）')
    max_score = Column(TINYINT, comment='最高分（可空）')
    min_score = Column(TINYINT, comment='最低分（可空）')
    dimension_avg_scores = Column(JSON, comment='各维度平均分（可空）')

    school_rank = Column(SmallInteger, comment='全校排名（可空）')
    school_total = Column(SmallInteger, comment='全校参评教师总数（可空）')
    college_rank = Column(SmallInteger, comment='院内排名（可空）')
    college_total = Column(SmallInteger, comment='院内参评教师总数（可空）')

    high_freq_problems = Column(JSON, comment='高频问题（可空）')
    high_freq_suggestions = Column(JSON, comment='高频建议（可空）')
    score_distribution = Column(JSON, comment='分数分布（可空）')

    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    teacher = relationship("User", foreign_keys=[teacher_id])
    college = relationship("College", back_populates="teacher_stats")

    __table_args__ = (
        UniqueConstraint('teacher_id', 'stat_year', 'stat_semester', name='uk_teacher_stat_period'),
        Index('idx_teacher_stat_year_semester', 'stat_year', 'stat_semester'),
        Index('idx_teacher_stat_college', 'college_id', 'stat_year', 'stat_semester'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '教师评价统计表'}
    )


class CollegeEvaluationStat(Base):
    """学院评价统计表：按学年/学期聚合"""
    __tablename__ = 'college_evaluation_stat'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='统计记录ID')
    college_id = Column(BigInteger, ForeignKey('college.id', ondelete='CASCADE'),
                        nullable=False, index=True, comment='学院ID')

    stat_year = Column(String(9), nullable=False, index=True, comment='统计学年')
    stat_semester = Column(TINYINT, nullable=False, comment='统计学期 1-春季 2-秋季')

    total_teacher_num = Column(SmallInteger, default=0, comment='参评教师总数')
    total_evaluation_num = Column(SmallInteger, default=0, comment='评价总次数')
    avg_total_score = Column(DECIMAL(5, 2), comment='学院总平均分（可空）')
    dimension_avg_scores = Column(JSON, comment='学院各维度平均分（可空）')

    school_rank = Column(SmallInteger, comment='学院全校排名（可空）')
    school_total = Column(SmallInteger, comment='参评学院总数（可空）')

    high_freq_problems = Column(JSON, comment='学院高频问题（可空）')
    score_distribution = Column(JSON, comment='分数分布（可空）')
    excellent_rate = Column(DECIMAL(5, 2), comment='优秀率（可空）')

    report_export_num = Column(SmallInteger, default=0, comment='报表导出次数')
    last_export_time = Column(DateTime, comment='最后导出时间（可空）')

    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    college = relationship("College", back_populates="college_stats")

    __table_args__ = (
        UniqueConstraint('college_id', 'stat_year', 'stat_semester', name='uk_college_stat_period'),
        Index('idx_college_stat_year_semester', 'stat_year', 'stat_semester'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '学院评价统计表'}
    )


# =========================================================
#  系统配置与日志（基本保留你的设计）
# =========================================================

class SystemConfig(Base):
    """系统配置表：建议存业务开关、当前学年学期、导入规则等"""
    __tablename__ = 'system_config'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='配置ID')
    config_key = Column(String(64), unique=True, nullable=False, index=True, comment='配置键')
    config_value = Column(JSON, nullable=False, comment='配置值（JSON）')
    config_type = Column(String(32), default='string', comment='配置类型 string/number/boolean/json')
    config_desc = Column(String(256), nullable=False, comment='配置描述')
    is_public = Column(Boolean, default=False, comment='是否前端可见')

    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')

    operator_id = Column(BigInteger, ForeignKey('user.id', ondelete='SET NULL'),
                         nullable=True, index=True, comment='操作人ID（可空）')

    operator = relationship("User", foreign_keys=[operator_id])

    __table_args__ = (
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '系统配置表'}
    )


class OperationLog(Base):
    """操作日志表：建议保留90天，定期归档"""
    __tablename__ = 'operation_log'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='SET NULL'),
                     nullable=True, index=True, comment='操作用户ID（可空）')
    user_name = Column(String(64), comment='操作用户名（冗余，防止用户删除后丢失）')

    operation_type = Column(String(32), nullable=False, index=True, comment='操作类型')
    module = Column(String(32), nullable=False, index=True, comment='模块')
    target_id = Column(BigInteger, comment='操作目标ID（可空）')
    target_type = Column(String(32), comment='操作目标类型（可空）')

    content = Column(JSON, comment='操作详情（可空）')
    before_data = Column(JSON, comment='操作前数据（可空）')
    after_data = Column(JSON, comment='操作后数据（可空）')

    ip_address = Column(String(45), comment='IP地址（可空）')
    user_agent = Column(String(512), comment='User-Agent（可空）')
    request_url = Column(String(256), comment='请求URL（可空）')
    request_method = Column(String(10), comment='请求方法（可空）')

    response_code = Column(SmallInteger, comment='响应状态码（可空）')
    execute_time = Column(SmallInteger, comment='执行耗时(ms，可空)')

    create_time = Column(DateTime, server_default=func.now(), index=True, comment='创建时间')
    create_date = Column(String(10), nullable=False, index=True, comment='创建日期YYYY-MM-DD（用于分区/归档）')

    __table_args__ = (
        Index('idx_log_user_time', 'user_id', 'create_time'),
        Index('idx_log_module_type', 'module', 'operation_type'),
        Index('idx_log_target', 'target_type', 'target_id'),
        Index('idx_log_date', 'create_date'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '操作日志表'}
    )


class LoginLog(Base):
    """登录日志表：建议保留180天"""
    __tablename__ = 'login_log'

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    user_id = Column(BigInteger, ForeignKey('user.id', ondelete='SET NULL'),
                     nullable=True, index=True, comment='用户ID（可空）')
    user_name = Column(String(64), comment='用户名/工号（可空）')

    login_type = Column(String(16), nullable=False, comment='登录类型 PASSWORD/WECHAT/TOKEN')
    login_status = Column(TINYINT, nullable=False, comment='登录状态 1-成功 0-失败')
    fail_reason = Column(String(128), comment='失败原因（可空）')

    ip_address = Column(String(45), comment='IP地址（可空）')
    location = Column(String(64), comment='登录地点（可空）')
    device_type = Column(String(32), comment='设备类型（可空）')
    browser = Column(String(64), comment='浏览器（可空）')
    os = Column(String(64), comment='操作系统（可空）')
    user_agent = Column(String(512), comment='User-Agent（可空）')

    create_time = Column(DateTime, server_default=func.now(), index=True, comment='登录时间')
    create_date = Column(String(10), nullable=False, index=True, comment='创建日期YYYY-MM-DD')

    __table_args__ = (
        Index('idx_login_user_time', 'user_id', 'create_time'),
        Index('idx_login_status_time', 'login_status', 'create_time'),
        Index('idx_login_date', 'create_date'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '登录日志表'}
    )


class OperationLogArchive(Base):
    """操作日志归档表：存储超过90天的历史日志"""
    __tablename__ = 'operation_log_archive'

    id = Column(BigInteger, primary_key=True, comment='原日志ID')
    user_id = Column(BigInteger, nullable=True, comment='操作用户ID')
    user_name = Column(String(64), comment='操作用户名')

    operation_type = Column(String(32), nullable=False, comment='操作类型')
    module = Column(String(32), nullable=False, comment='模块')
    target_id = Column(BigInteger, comment='操作目标ID（可空）')
    target_type = Column(String(32), comment='操作目标类型（可空）')
    content = Column(JSON, comment='操作详情（可空）')

    ip_address = Column(String(45), comment='IP地址（可空）')
    create_time = Column(DateTime, index=True, comment='创建时间')
    create_date = Column(String(10), index=True, comment='创建日期')
    archive_time = Column(DateTime, server_default=func.now(), comment='归档时间')

    __table_args__ = (
        Index('idx_archive_date', 'create_date'),
        Index('idx_archive_user', 'user_id', 'create_time'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '操作日志归档表'}
    )


class LoginLogArchive(Base):
    """登录日志归档表：存储超过180天的历史日志"""
    __tablename__ = 'login_log_archive'

    id = Column(BigInteger, primary_key=True, comment='原日志ID')
    user_id = Column(BigInteger, nullable=True, comment='用户ID（可空）')
    user_name = Column(String(64), comment='用户名（可空）')

    login_type = Column(String(16), nullable=False, comment='登录类型')
    login_status = Column(TINYINT, nullable=False, comment='登录状态')
    ip_address = Column(String(45), comment='IP地址（可空）')
    location = Column(String(64), comment='登录地点（可空）')

    create_time = Column(DateTime, index=True, comment='登录时间')
    create_date = Column(String(10), index=True, comment='创建日期')
    archive_time = Column(DateTime, server_default=func.now(), comment='归档时间')

    __table_args__ = (
        Index('idx_login_archive_date', 'create_date'),
        {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci', 'comment': '登录日志归档表'}
    )
