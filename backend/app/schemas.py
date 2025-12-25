from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


# 用户相关模型
class UserBase(BaseModel):
    username: str
    name: str
    college: Optional[str] = None


class UserCreate(BaseModel):
    user_id: str  # 学号 / 工号 / 账号
    user_name: str
    password: str
    college_id: Optional[str] = None


class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    role_type: Optional[int] = None
    college_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# 登录表单
class LoginForm(BaseModel):
    user_id: str  # 学号 / 工号 / 账号
    password: str


# 认证相关模型
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    expire_time: datetime


class TokenData(BaseModel):
    user_id: int
    user_id: str
    role_type: int
    college_id: int


# 学院相关模型
class CollegeBase(BaseModel):
    college_code: str
    college_name: str


class CollegeCreate(CollegeBase):
    pass


class CollegeUpdate(BaseModel):
    college_name: Optional[str] = None


class CollegeResponse(CollegeBase):
    id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    is_delete: bool = False

    class Config:
        from_attributes = True


# 权限字典相关模型
class PermissionDictBase(BaseModel):
    permission_code: str
    permission_name: str
    permission_type: int
    parent_id: Optional[int] = 0
    sort: int = 0


class PermissionDictCreate(PermissionDictBase):
    pass


class PermissionDictUpdate(BaseModel):
    permission_name: Optional[str] = None
    permission_type: Optional[int] = None
    sort: Optional[int] = None


class PermissionDictResponse(PermissionDictBase):
    id: int
    create_time: datetime
    is_delete: bool = False

    class Config:
        from_attributes = True


# 用户表相关模型
class UserNewBase(BaseModel):
    user_id: str
    user_name: str
    role_type: int  # 角色类型 1-普通教师 2-督导 3-学院管理员 4-学校管理员
    college_id: int


class UserNewCreate(UserNewBase):
    password: str


class UserNewUpdate(BaseModel):
    user_name: Optional[str] = None
    role_type: Optional[int] = None
    college_id: Optional[int] = None


class UserNewResponse(UserNewBase):
    id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    is_delete: bool = False

    class Config:
        from_attributes = True


# 用户权限关联模型
class UserPermissionBase(BaseModel):
    user_id: int
    permission_id: int
    scope_college_ids: Optional[List[str]] = None


class UserPermissionCreate(UserPermissionBase):
    operator_id: int


class UserPermissionUpdate(BaseModel):
    scope_college_ids: Optional[List[str]] = None


class UserPermissionResponse(UserPermissionBase):
    id: int
    create_time: datetime
    is_delete: bool = False

    class Config:
        from_attributes = True


# 课表相关模型
class TimetableBase(BaseModel):
    timetable_no: str
    college_id: int
    teacher_id: int
    course_name: str
    course_type: str  # 课程类型（必修课/选修课/实训课）
    class_name: str
    teach_week: str  # 授课周次（如1-16周）
    teach_time: str  # 授课时间（如周一第3-4节）
    teach_place: str  # 授课地点
    sync_time: datetime  # 最后同步时间


class TimetableCreate(TimetableBase):
    pass


class TimetableUpdate(BaseModel):
    course_name: Optional[str] = None
    course_type: Optional[str] = None
    class_name: Optional[str] = None
    teach_week: Optional[str] = None
    teach_time: Optional[str] = None
    teach_place: Optional[str] = None
    sync_time: Optional[datetime] = None


class TimetableResponse(TimetableBase):
    id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    is_delete: bool = False

    class Config:
        from_attributes = True


# 评教相关模型
class TeachingEvaluationBase(BaseModel):
    evaluation_no: str
    timetable_id: int
    teach_teacher_id: int
    listen_teacher_id: int
    total_score: int  # 评教总分（0-100）
    dimension_scores: Dict[str, Any]  # 各维度得分（如{"课程导入":20,"互动性":15}）
    advantage_content: Optional[str] = None  # 优点描述
    problem_content: Optional[str] = None  # 问题描述
    improve_suggestion: Optional[str] = None  # 改进建议
    is_anonymous: bool = False  # 是否匿名 0-实名 1-匿名
    submit_time: datetime  # 提交时间


class TeachingEvaluationCreate(TeachingEvaluationBase):
    pass


class TeachingEvaluationUpdate(BaseModel):
    total_score: Optional[int] = None
    dimension_scores: Optional[Dict[str, Any]] = None
    advantage_content: Optional[str] = None
    problem_content: Optional[str] = None
    improve_suggestion: Optional[str] = None
    is_anonymous: Optional[bool] = None


class TeachingEvaluationResponse(TeachingEvaluationBase):
    id: int
    create_time: datetime
    update_time: Optional[datetime] = None
    is_delete: bool = False

    class Config:
        from_attributes = True


# 教师评教统计模型
class TeacherEvaluationStatBase(BaseModel):
    teacher_id: int
    college_id: int
    stat_year: str  # 统计年份
    stat_semester: int  # 统计学期 1-春季 2-秋季
    total_evaluation_num: int = 0  # 评教总次数
    avg_total_score: Optional[float] = None  # 总分平均分
    dimension_avg_scores: Optional[Dict[str, Any]] = None  # 各维度平均分
    school_rank: Optional[int] = None  # 全校排名
    college_rank: Optional[int] = None  # 院内排名
    high_freq_problems: Optional[List[str]] = None  # 高频问题
    high_freq_suggestions: Optional[List[str]] = None  # 高频建议


class TeacherEvaluationStatCreate(TeacherEvaluationStatBase):
    pass


class TeacherEvaluationStatUpdate(BaseModel):
    total_evaluation_num: Optional[int] = None
    avg_total_score: Optional[float] = None
    dimension_avg_scores: Optional[Dict[str, Any]] = None
    school_rank: Optional[int] = None
    college_rank: Optional[int] = None


class TeacherEvaluationStatResponse(TeacherEvaluationStatBase):
    id: int
    update_time: datetime

    class Config:
        from_attributes = True


# 学院评教统计模型
class CollegeEvaluationStatBase(BaseModel):
    college_id: int
    stat_year: str  # 统计年份
    stat_semester: int  # 统计学期 1-春季 2-秋季
    total_teacher_num: int = 0  # 参评教师总数
    avg_total_score: Optional[float] = None  # 学院总平均分
    dimension_avg_scores: Optional[Dict[str, Any]] = None  # 学院各维度平均分
    school_rank: Optional[int] = None  # 学院全校排名
    high_freq_problems: Optional[List[str]] = None  # 学院高频问题
    report_export_num: int = 0  # 报表导出次数


class CollegeEvaluationStatCreate(CollegeEvaluationStatBase):
    pass


class CollegeEvaluationStatUpdate(BaseModel):
    total_teacher_num: Optional[int] = None
    avg_total_score: Optional[float] = None
    school_rank: Optional[int] = None
    report_export_num: Optional[int] = None


class CollegeEvaluationStatResponse(CollegeEvaluationStatBase):
    id: int
    update_time: datetime

    class Config:
        from_attributes = True


# 系统配置模型
class SystemConfigBase(BaseModel):
    config_key: str
    config_value: Dict[str, Any]
    config_desc: str


class SystemConfigCreate(SystemConfigBase):
    operator_id: int


class SystemConfigUpdate(BaseModel):
    config_value: Optional[Dict[str, Any]] = None
    config_desc: Optional[str] = None


class SystemConfigResponse(SystemConfigBase):
    id: int
    create_time: datetime
    update_time: datetime

    class Config:
        from_attributes = True


# 课程相关模型
class CourseBase(BaseModel):
    name: str
    teacher_id: int
    college_id: int
    semester: str
    credit: float


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    teacher_id: Optional[int] = None
    college_id: Optional[int] = None
    semester: Optional[str] = None
    credit: Optional[float] = None


class CourseResponse(CourseBase):
    id: int
    teacher: UserResponse
    college: CollegeResponse

    class Config:
        from_attributes = True


# 评价相关模型
class EvaluationScores(BaseModel):
    teachingAttitude: float
    content: float
    method: float
    effect: float
    detail: Dict[str, Dict[str, float]]


class EvaluationBase(BaseModel):
    course_id: int
    teacher_id: int
    evaluator_id: int
    evaluator_role: str
    anonymous: bool
    scores: EvaluationScores
    total_score: float
    level: str
    suggestion: Optional[str] = None


class EvaluationCreate(BaseModel):
    course_id: int
    teacher_id: int
    evaluator_role: str
    anonymous: bool
    scores: EvaluationScores
    total_score: float
    level: str
    suggestion: Optional[str] = None


class EvaluationResponse(EvaluationBase):
    id: int
    course: CourseResponse
    teacher: UserResponse
    evaluator: UserResponse
    created_at: datetime

    class Config:
        from_attributes = True


# 听课记录相关模型
class ListenRecordScores(BaseModel):
    teachingAttitude: float
    content: float
    method: float
    effect: float
    detail: Dict[str, Dict[str, float]]


class ListenRecordBase(BaseModel):
    course_id: int
    teacher_id: int
    listener_id: int
    scores: ListenRecordScores
    total_score: float
    level: str
    suggestion: Optional[str] = None


class ListenRecordCreate(ListenRecordBase):
    pass


class ListenRecordResponse(ListenRecordBase):
    id: int
    course: CourseResponse
    teacher: UserResponse
    listener: UserResponse
    created_at: datetime

    class Config:
        from_attributes = True


# 统计相关模型
class TeacherStatistics(BaseModel):
    teacher_id: int
    teacher_name: str
    total_evaluations: int
    average_score: float
    college_name: str
    course_count: int

    class Config:
        from_attributes = True


class CollegeStatistics(BaseModel):
    college_id: int
    college_name: str
    total_teachers: int
    average_score: float
    total_evaluations: int

    class Config:
        from_attributes = True


class CourseStatistics(BaseModel):
    course_id: int
    course_name: str
    teacher_name: str
    average_score: float
    total_evaluations: int

    class Config:
        from_attributes = True


# 配置相关模型
class ConfigBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class ConfigCreate(ConfigBase):
    pass


class ConfigUpdate(BaseModel):
    value: str
    description: Optional[str] = None


class ConfigResponse(ConfigBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
