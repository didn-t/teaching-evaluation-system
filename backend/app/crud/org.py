# app/crud/org.py
from __future__ import annotations

from app.crud.base import CRUDBase
from app.models import College, ResearchRoom, Major, Clazz, TeacherProfile  # 按你的实际路径改

college_crud = CRUDBase(College)
research_room_crud = CRUDBase(ResearchRoom)
major_crud = CRUDBase(Major)
clazz_crud = CRUDBase(Clazz)
teacher_profile_crud = CRUDBase(TeacherProfile)
