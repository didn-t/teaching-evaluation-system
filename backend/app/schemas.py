from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict, Any, Generic, TypeVar

T = TypeVar("T")  # 泛型类型


# 用户相关模型
class UserBase(BaseModel):
    user_on: str  # 学号 / 工号 / 账号
    password: str


class UserCreate(UserBase):
    user_name: Optional[str]
    college_id: Optional[str] = None


class UserUpdate(BaseModel):
    user_name: Optional[str] = None
    college_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BaseResponse(BaseModel, Generic[T]):
    """全局统一响应模型"""
    # 状态码（自定义业务码，200表示成功，非200表示异常）
    code: int
    # 提示信息（成功时返回成功提示，失败时返回错误详情）
    msg: str
    # 业务数据（泛型类型，支持任意数据结构，无数据时为None）
    data: Optional[T] = None
    # 时间戳（统一返回秒级整数时间戳）
    timestamp: int = int(datetime.now().timestamp())

    class Config:
        # 支持ORM对象序列化
        from_attributes = True


# 认证相关模型
class Token(BaseModel):
    token: str


class TokenData(BaseModel):
    id: int
    user_on: str
    college_id: Optional[int] = None
    status: Optional[int] = 1
    is_delete: Optional[bool] = 0


# 学院相关模型
class CollegeCreate(BaseModel):
    college_code: str = Field(..., max_length=32)
    college_name: str = Field(..., max_length=64)
    short_name: Optional[str] = Field(None, max_length=16)
    sort_order: int = 0


class CollegeUpdate(BaseModel):
    college_name: Optional[str] = Field(None, max_length=64)
    short_name: Optional[str] = Field(None, max_length=16)
    sort_order: Optional[int] = None
    is_delete: Optional[bool] = None


# -------- ResearchRoom --------
class ResearchRoomCreate(BaseModel):
    college_id: int
    room_name: str = Field(..., max_length=64)


class ResearchRoomUpdate(BaseModel):
    room_name: Optional[str] = Field(None, max_length=64)
    is_delete: Optional[bool] = None


# -------- Major --------
class MajorCreate(BaseModel):
    college_id: int
    major_name: str = Field(..., max_length=64)
    major_code: Optional[str] = Field(None, max_length=32)
    short_name: Optional[str] = Field(None, max_length=32)


class MajorUpdate(BaseModel):
    major_name: Optional[str] = Field(None, max_length=64)
    major_code: Optional[str] = Field(None, max_length=32)
    short_name: Optional[str] = Field(None, max_length=32)
    is_delete: Optional[bool] = None


# -------- Clazz --------
class ClazzCreate(BaseModel):
    major_id: Optional[int] = None
    class_name: str = Field(..., max_length=64)
    class_code: Optional[str] = Field(None, max_length=32)
    grade: Optional[str] = Field(None, max_length=16)


class ClazzUpdate(BaseModel):
    major_id: Optional[int] = None
    class_name: Optional[str] = Field(None, max_length=64)
    class_code: Optional[str] = Field(None, max_length=32)
    grade: Optional[str] = Field(None, max_length=16)
    is_delete: Optional[bool] = None


# -------- Response Models --------
class CollegeResponse(BaseModel):
    id: int
    college_code: str
    college_name: str
    short_name: Optional[str] = None
    sort_order: int
    create_time: datetime
    update_time: Optional[datetime] = None
    is_delete: bool = False

    class Config:
        from_attributes = True


class ResearchRoomResponse(BaseModel):
    id: int
    college_id: int
    room_name: str
    create_time: datetime
    update_time: Optional[datetime] = None
    is_delete: bool = False

    class Config:
        from_attributes = True


class MajorResponse(BaseModel):
    id: int
    college_id: int
    major_name: str
    major_code: Optional[str] = None
    short_name: Optional[str] = None
    create_time: datetime
    update_time: Optional[datetime] = None
    is_delete: bool = False

    class Config:
        from_attributes = True


class ClazzResponse(BaseModel):
    id: int
    major_id: Optional[int] = None
    class_name: str
    class_code: Optional[str] = None
    grade: Optional[str] = None
    create_time: datetime
    update_time: Optional[datetime] = None
    is_delete: bool = False

    class Config:
        from_attributes = True


# -------- Timetable (新版本)--------
class TimetableCreate(BaseModel):
    college_id: Optional[int] = None
    teacher_id: int
    class_id: Optional[int] = None
    class_name: str = Field(..., max_length=128)
    course_code: Optional[str] = Field(None, max_length=32)
    course_name: str = Field(..., max_length=128)
    academic_year: str = Field(..., max_length=9)  # 2024-2025
    semester: int = Field(..., ge=1, le=2)  # 1/2
    weekday: int = Field(..., ge=1, le=7)
    weekday_text: Optional[str] = Field(None, max_length=8)
    period: str = Field(..., max_length=16)
    section_time: str = Field(..., max_length=16)
    week_info: str = Field(..., max_length=128)
    classroom: str = Field("", max_length=128)
    student_count: Optional[int] = None
    credit: Optional[float] = None
    course_type: Optional[str] = Field(None, max_length=32)


class TimetableUpdate(BaseModel):
    college_id: Optional[int] = None
    teacher_id: Optional[int] = None
    class_id: Optional[int] = None
    class_name: Optional[str] = Field(None, max_length=128)
    course_code: Optional[str] = Field(None, max_length=32)
    course_name: Optional[str] = Field(None, max_length=128)
    academic_year: Optional[str] = Field(None, max_length=9)
    semester: Optional[int] = Field(None, ge=1, le=2)
    weekday: Optional[int] = Field(None, ge=1, le=7)
    weekday_text: Optional[str] = Field(None, max_length=8)
    period: Optional[str] = Field(None, max_length=16)
    section_time: Optional[str] = Field(None, max_length=16)
    week_info: Optional[str] = Field(None, max_length=128)
    classroom: Optional[str] = Field(None, max_length=128)
    student_count: Optional[int] = None
    credit: Optional[float] = None
    course_type: Optional[str] = Field(None, max_length=32)
    is_delete: Optional[bool] = None


# 课表响应模型
class TimetableResponse(BaseModel):
    id: int
    college_id: Optional[int] = None
    teacher_id: int
    class_id: Optional[int] = None
    class_name: str
    course_code: Optional[str] = None
    course_name: str
    academic_year: str  # 2024-2025
    semester: int  # 1/2
    weekday: int  # 1-7
    weekday_text: Optional[str] = None
    period: str
    section_time: str
    week_info: str
    classroom: str
    student_count: Optional[int] = None
    credit: Optional[float] = None
    course_type: Optional[str] = None
    sync_source: int = 0
    external_id: Optional[str] = None
    sync_time: Optional[datetime] = None
    sync_status: int = 1
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


# 提交评教请求模型(前端提交)
class EvaluationSubmit(BaseModel):
    timetable_id: int
    total_score: int = Field(..., ge=0, le=100, description='评教总分（0-100）')
    dimension_scores: Dict[str, Any] = Field(..., description='各维度得分')
    advantage_content: Optional[str] = Field(None, description='优点描述')
    problem_content: Optional[str] = Field(None, description='问题描述')
    improve_suggestion: Optional[str] = Field(None, description='改进建议')
    listen_date: datetime = Field(..., description='实际听课日期')
    listen_duration: Optional[int] = Field(None, ge=0, description='听课时长（分钟）')
    listen_location: Optional[str] = Field(None, max_length=64, description='实际听课地点')
    is_anonymous: bool = Field(False, description='是否匿名')


class EvaluationSubmitResponse(BaseModel):
    id: int
    evaluation_no: str
    total_score: int
    score_level: str
    submit_time: datetime

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


# 评教维度配置响应模型(用于返回评教维度的配置信息)
class EvaluationDimensionResponse(BaseModel):
    id: int
    dimension_code: str
    dimension_name: str
    max_score: int
    weight: float
    sort_order: int
    description: Optional[str] = None
    scoring_criteria: Optional[Dict[str, Any]] = None
    is_required: bool = True
    status: int = 1

    class Config:
        from_attributes = True


# 评教审核请求模型(同于审核评教记录时提交请求：)
class EvaluationReviewRequest(BaseModel):
    status: int = Field(..., ge=0, le=2, description='状态 0-作废 1-有效 2-待审核')
    review_comment: Optional[str] = Field(None, description='审核意见')


# 教师评教详情响应模型(用于返回单条评教记录的完整详情)
class TeacherEvaluationDetailResponse(BaseModel):
    id: int
    evaluation_no: str
    timetable_id: int
    course_name: str
    course_type: str
    class_name: str
    teach_teacher_id: int
    teach_teacher_name: str
    total_score: int
    dimension_scores: Dict[str, Any]
    score_level: str
    advantage_content: Optional[str] = None
    problem_content: Optional[str] = None
    improve_suggestion: Optional[str] = None
    listen_date: datetime
    listen_duration: Optional[int] = None
    listen_location: Optional[str] = None
    is_anonymous: bool
    status: int
    submit_time: datetime
    listen_teacher_id: Optional[int] = None
    listen_teacher_name: Optional[str] = None

    class Config:
        from_attributes = True


# 教师统计响应模型(用于返回教师的评教统计数据：)
class TeacherStatisticsResponse(BaseModel):
    teacher_id: int
    teacher_name: str
    college_id: int
    college_name: str
    total_evaluation_num: int
    avg_total_score: Optional[float] = None
    max_score: Optional[int] = None
    min_score: Optional[int] = None
    dimension_avg_scores: Optional[Dict[str, Any]] = None
    school_rank: Optional[int] = None
    school_total: Optional[int] = None
    college_rank: Optional[int] = None
    college_total: Optional[int] = None
    score_distribution: Optional[Dict[str, int]] = None
    high_freq_problems: Optional[List[str]] = None
    high_freq_suggestions: Optional[List[str]] = None

    class Config:
        from_attributes = True


# 学院统计响应模型(用于返回学院的评教统计数据)
class CollegeStatisticsResponse(BaseModel):
    college_id: int
    college_name: str
    total_teacher_num: int
    total_evaluation_num: int
    avg_total_score: Optional[float] = None
    dimension_avg_scores: Optional[Dict[str, Any]] = None
    school_rank: Optional[int] = None
    school_total: Optional[int] = None
    excellent_rate: Optional[float] = None
    score_distribution: Optional[Dict[str, int]] = None
    high_freq_problems: Optional[List[str]] = None

    class Config:
        from_attributes = True


# 全校统计响应模型(用于返回全校范围的评教统计汇总)
class SchoolStatisticsResponse(BaseModel):
    total_college_num: int
    total_teacher_num: int
    total_evaluation_num: int
    avg_total_score: Optional[float] = None
    dimension_avg_scores: Optional[Dict[str, Any]] = None
    excellent_rate: Optional[float] = None
    score_distribution: Optional[Dict[str, int]] = None
    college_rankings: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


# 评教列表查询模型(用于分页查询评教记录时的条件筛选)
class EvaluationListQuery(BaseModel):
    page: int = Field(1, ge=1, description='页码')
    page_size: int = Field(10, ge=1, le=100, description='每页数量')
    teacher_id: Optional[int] = Field(None, description='授课教师ID')
    course_name: Optional[str] = Field(None, description='课程名称')
    score_level: Optional[str] = Field(None, description='评分等级')
    status: Optional[int] = Field(None, description='状态')
    start_date: Optional[datetime] = Field(None, description='开始日期')
    end_date: Optional[datetime] = Field(None, description='结束日期')


# 课程类型更新请求模型
class CourseTypeUpdate(BaseModel):
    course_type: Optional[str] = Field(None, max_length=32, description='课程评价状态：空/待评/已评')
