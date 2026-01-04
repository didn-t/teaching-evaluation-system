from fastapi import APIRouter
from . import eval, user, org

api_router = APIRouter()
api_router.include_router(eval.router)
api_router.include_router(user.router)
api_router.include_router(org.router)