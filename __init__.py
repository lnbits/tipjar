from http import HTTPStatus

from starlette.exceptions import HTTPException

from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from lnbits.db import Database
from lnbits.helpers import template_renderer

from os.path import exists

if exists(..satspay.models.py):
    db = Database("ext_tipjar")

    tipjar_ext: APIRouter = APIRouter(prefix="/tipjar", tags=["tipjar"])

    tipjar_static_files = [
        {
            "path": "/tipjar/static",
            "app": StaticFiles(directory="lnbits/extensions/tipjar/static"),
            "name": "tipjar_static",
        }
    ]


    def tipjar_renderer():
        return template_renderer(["lnbits/extensions/tipjar/templates"])

    from .views import *  # noqa: F401,F403
    from .views_api import *  # noqa: F401,F403
else:
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Tipjar does not exist."
    )

