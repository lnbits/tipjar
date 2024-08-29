from http import HTTPStatus

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer
from starlette.exceptions import HTTPException

from .crud import get_tipjar

templates = Jinja2Templates(directory="templates")
tipjar_generic_router = APIRouter()


def tipjar_renderer():
    return template_renderer(["tipjar/templates"])


@tipjar_generic_router.get("/")
async def index(request: Request, user: User = Depends(check_user_exists)):
    return tipjar_renderer().TemplateResponse(
        "tipjar/index.html", {"request": request, "user": user.dict()}
    )


@tipjar_generic_router.get("/{tipjar_id}")
async def tip(request: Request, tipjar_id: int):
    """Return the donation form for the Tipjar corresponding to id"""
    tipjar = await get_tipjar(tipjar_id)
    if not tipjar:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="TipJar does not exist."
        )

    return tipjar_renderer().TemplateResponse(
        "tipjar/display.html",
        {"request": request, "donatee": tipjar.name, "tipjar_id": tipjar.id},
    )
