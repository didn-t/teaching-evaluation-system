from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List, Dict

# 用户相关模型
class UserBase(BaseModel):
    username: str
    name: str
    role: str
    college: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    college: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 认证相关模型
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

# 学院相关模型
class CollegeBase(BaseModel):
    name: str

class CollegeCreate(CollegeBase):
    pass

class CollegeResponse(CollegeBase):
    id: int
    created_at: datetime
    
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