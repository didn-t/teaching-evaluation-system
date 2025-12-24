# 定义数据库

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from main import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    name = Column(String(50), nullable=False)
    role = Column(String(20), nullable=False)
    college = Column(String(50), nullable=True)
    courses = relationship("Course", back_populates="teacher")
    evaluations_given = relationship("Evaluation", foreign_keys="Evaluation.evaluator_id", back_populates="evaluator")
    evaluations_received = relationship("Evaluation", foreign_keys="Evaluation.teacher_id", back_populates="teacher")
    listen_records = relationship("ListenRecord", back_populates="listener")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

