from fastapi import APIRouter

from .crud import db
from .views import tipjar_generic_router
from .views_api import tipjar_api_router

tipjar_ext: APIRouter = APIRouter(prefix="/tipjar", tags=["tipjar"])
tipjar_ext.include_router(tipjar_generic_router)
tipjar_ext.include_router(tipjar_api_router)

tipjar_static_files = [
    {
        "path": "/tipjar/static",
        "name": "tipjar_static",
    }
]


__all__ = ["db", "tipjar_ext", "tipjar_static_files"]
