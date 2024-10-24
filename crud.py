from typing import Optional

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import CreateTipJar, Tip, TipJar

db = Database("ext_tipjar")


async def create_tip(tip: Tip) -> Tip:
    """Create a new Tip"""
    await db.insert("tipjar.tip", tip)
    return tip


async def create_tipjar(data: CreateTipJar) -> TipJar:
    """Create a new TipJar"""

    tipjar = TipJar(
        id=urlsafe_short_hash(),
        **data.dict(),
    )
    await db.insert("tipjar.tipjar", tipjar)
    return tipjar


async def get_tipjar(tipjar_id: str) -> Optional[TipJar]:
    """Return a tipjar by ID"""
    return await db.fetchone(
        "SELECT * FROM tipjar.tipjar WHERE id = :id",
        {"id": tipjar_id},
        TipJar,
    )


async def get_tipjars(wallet_id: str) -> Optional[list]:
    """Return all TipJars belonging assigned to the wallet_id"""
    return await db.fetchall(
        "SELECT * FROM tipjar.tipjar WHERE wallet = :wallet_id",
        {"wallet_id": wallet_id},
        TipJar,
    )


async def delete_tipjar(tipjar_id: str) -> None:
    """Delete a TipJar and all corresponding Tips"""
    tips = await get_tipjar_tips(tipjar_id)
    for tip in tips:
        await delete_tip(tip.id)
    await db.execute("DELETE FROM tipjar.tipjar WHERE id = :id", {"id": tipjar_id})


async def get_tip(tip_id: str) -> Optional[Tip]:
    """Return a Tip"""
    return await db.fetchone(
        "SELECT * FROM tipjar.tip WHERE id = :id",
        {"id": tip_id},
        Tip,
    )


async def get_tipjar_tips(tipjar_id: str) -> list[Tip]:
    """Return all Tips for a tipjar"""
    return await db.fetchall(
        "SELECT * FROM tipjar.tip WHERE tipjar = :tipjar_id",
        {"tipjar_id": tipjar_id},
        Tip,
    )


async def get_tips(wallet_id: str) -> list[Tip]:
    """Return all Tips assigned to wallet_id"""
    return await db.fetchall(
        "SELECT * FROM tipjar.tip WHERE wallet = :wallet_id",
        {"wallet_id": wallet_id},
        Tip,
    )


async def delete_tip(tip_id: str) -> None:
    """Delete a Tip and its corresponding statspay charge"""
    await db.execute("DELETE FROM tipjar.tip WHERE id = :id", {"id": tip_id})


async def update_tip(tip: Tip) -> Tip:
    """Update a Tip"""
    await db.update("tipjar.tip", tip)
    return tip


async def update_tipjar(tipjar: TipJar) -> TipJar:
    """Update a tipjar"""
    await db.update("tipjar.tipjar", tipjar)
    return tipjar
