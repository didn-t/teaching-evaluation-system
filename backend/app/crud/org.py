# app/crud/org.py
from __future__ import annotations

from app.crud.base_async import CRUDBaseAsync
from app.models import College, ResearchRoom, Major, Clazz, TeacherProfile  # 按你的实际路径改

college_crud = CRUDBaseAsync(College)
research_room_crud = CRUDBaseAsync(ResearchRoom)
major_crud = CRUDBaseAsync(Major)
clazz_crud = CRUDBaseAsync(Clazz)
teacher_profile_crud = CRUDBaseAsync(TeacherProfile)
