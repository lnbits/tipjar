from fastapi import APIRouter

from lnbits.db import Database
from lnbits.helpers import template_renderer

db = Database("ext_tipjar")

tipjar_ext: APIRouter = APIRouter(prefix="/tipjar", tags=["tipjar"])

tipjar_static_files = [
    {
        "path": "/tipjar/static",
        "name": "tipjar_static",
    }
]


def tipjar_renderer():
    return template_renderer(["tipjar/templates"])


from .views import *  # noqa: F401,F403
from .views_api import *  # noqa: F401,F403
