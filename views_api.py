from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from lnbits.core.crud import get_user, get_wallet
from lnbits.core.models import WalletTypeInfo
from lnbits.decorators import require_admin_key
from loguru import logger

from .crud import (
    create_tip,
    create_tipjar,
    delete_tip,
    delete_tipjar,
    get_tip,
    get_tipjar,
    get_tipjar_tips,
    get_tipjars,
    get_tips,
    update_tip,
    update_tipjar,
)
from .helpers import create_charge, delete_charge
from .models import CreateTip, CreateTipJar, CreateTips

tipjar_api_router = APIRouter()


@tipjar_api_router.post("/api/v1/tipjars")
async def api_create_tipjar(data: CreateTipJar):
    """Create a tipjar, which holds data about how/where to post tips"""
    try:
        tipjar = await create_tipjar(data)
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(exc)
        ) from exc

    return tipjar.dict()


@tipjar_api_router.post("/api/v1/tips")
async def api_create_tip(data: CreateTips):
    """Public route to take data from tip form and return satspay charge"""
    logger.debug(f"Creating tip with data: {data}")
    sats = int(data.sats)
    message = data.message
    if not message:
        message = "No message"
    tipjar_id = int(data.tipjar)
    tipjar = await get_tipjar(tipjar_id)
    if not tipjar:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Tipjar does not exist."
        )
    wallet_id = tipjar.wallet
    wallet = await get_wallet(wallet_id)
    if not wallet:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Tipjar wallet does not exist."
        )
    logger.debug(f"Creating tip for wallet: {wallet}")
    name = data.name or "Anonymous"

    name = data.name or "Anonymous"
    try:
        charge_id = await create_charge(
            data={
                "amount": sats,
                "webhook": tipjar.webhook or None,
                "name": name,
                "description": message,
                "onchainwallet": tipjar.onchain or None,
                "lnbitswallet": tipjar.wallet,
                "completelink": f"/tipjar/{tipjar_id}",
                "completelinktext": "Thanks for the tip!",
                "time": 1440,
                "custom_css": "",
            },
            api_key=wallet.inkey,
        )
    except Exception as exc:
        msg = f"Failed to create charge: {exc!s}"
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=msg
        ) from exc

    await create_tip(
        tip_id=charge_id,
        wallet=tipjar.wallet,
        message=message,
        name=name,
        sats=int(data.sats),
        tipjar=data.tipjar,
    )

    return {"redirect_url": f"/satspay/{charge_id}"}


@tipjar_api_router.get("/api/v1/tipjars")
async def api_get_tipjars(key_type: WalletTypeInfo = Depends(require_admin_key)):
    """Return list of all tipjars assigned to wallet with given invoice key"""
    user = await get_user(key_type.wallet.user)
    if not user:
        return []
    tipjars = []
    for wallet_id in user.wallet_ids:
        new_tipjars = await get_tipjars(wallet_id)
        tipjars += new_tipjars if new_tipjars else []
    return [tipjar.dict() for tipjar in tipjars]


@tipjar_api_router.get("/api/v1/tips")
async def api_get_tips(key_type: WalletTypeInfo = Depends(require_admin_key)):
    """Return list of all tips assigned to wallet with given invoice key"""
    user = await get_user(key_type.wallet.user)
    if not user:
        return []
    tips = []
    for wallet_id in user.wallet_ids:
        new_tips = await get_tips(wallet_id)
        tips += new_tips if new_tips else []
    return [tip.dict() for tip in tips]


@tipjar_api_router.put("/api/v1/tips/{tip_id}")
async def api_update_tip(
    data: CreateTip,
    tip_id: str,
    key_type: WalletTypeInfo = Depends(require_admin_key),
):
    """Update a tip with the data given in the request"""
    if tip_id:
        tip = await get_tip(tip_id)

        if not tip:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="Tip does not exist."
            )

        if tip.wallet != key_type.wallet.id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Not your tip."
            )

        tip = await update_tip(tip_id, **data.dict())
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="No tip ID specified"
        )
    return tip.dict()


@tipjar_api_router.put("/api/v1/tipjars/{tipjar_id}")
async def api_update_tipjar(
    data: CreateTipJar,
    tipjar_id: int,
    key_type: WalletTypeInfo = Depends(require_admin_key),
):
    """Update a tipjar with the data given in the request"""
    if tipjar_id:
        tipjar = await get_tipjar(tipjar_id)

        if not tipjar:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="TipJar does not exist."
            )

        if tipjar.wallet != key_type.wallet.id:
            raise HTTPException(
                status_code=HTTPStatus.FORBIDDEN, detail="Not your tipjar."
            )

        tipjar = await update_tipjar(str(tipjar_id), **data.dict())
    else:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="No tipjar ID specified"
        )
    return tipjar.dict()


@tipjar_api_router.delete("/api/v1/tips/{tip_id}")
async def api_delete_tip(
    tip_id: str, key_type: WalletTypeInfo = Depends(require_admin_key)
):
    """Delete the tip with the given tip_id"""
    tip = await get_tip(tip_id)
    if not tip:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No tip with this ID!"
        )
    if tip.wallet != key_type.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not authorized to delete this tip!",
        )
    await delete_tip(tip_id)
    try:
        await delete_charge(tip_id, key_type.wallet.inkey)
    except Exception as exc:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete charge: {exc!s}",
        ) from exc

    return "", HTTPStatus.NO_CONTENT


@tipjar_api_router.delete("/api/v1/tipjars/{tipjar_id}")
async def api_delete_tipjar(
    tipjar_id: int, key_type: WalletTypeInfo = Depends(require_admin_key)
):
    """Delete the tipjar with the given tipjar_id"""
    tipjar = await get_tipjar(tipjar_id)
    if not tipjar:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="No tipjar with this ID!"
        )
    if tipjar.wallet != key_type.wallet.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not authorized to delete this tipjar!",
        )

    tips = await get_tipjar_tips(tipjar_id)
    for tip in tips:
        await delete_charge(tip.id, key_type.wallet.inkey)

    await delete_tipjar(tipjar_id)

    return "", HTTPStatus.NO_CONTENT
