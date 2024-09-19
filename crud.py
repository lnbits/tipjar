from typing import Optional

from lnbits.db import Database
from lnbits.helpers import insert_query, update_query, urlsafe_short_hash

from .models import CreateTipJar, Tip, TipJar

db = Database("ext_tipjar")


async def create_tip(tip: Tip) -> Tip:
    """Create a new Tip"""
    await db.execute(insert_query("tipjar.Tips", tip), tip.dict())
    return tip


async def create_tipjar(data: CreateTipJar) -> TipJar:
    """Create a new TipJar"""

    tipjar = TipJar(
        id=urlsafe_short_hash(),
        **data.dict(),
    )
    await db.execute(insert_query("tipjar.TipJars", tipjar), tipjar.dict())
    return tipjar


async def get_tipjar(tipjar_id: int) -> Optional[TipJar]:
    """Return a tipjar by ID"""
    row = await db.fetchone(
        "SELECT * FROM tipjar.TipJars WHERE id = :id", {"id": tipjar_id}
    )
    return TipJar(**row) if row else None


async def get_tipjars(wallet_id: str) -> Optional[list]:
    """Return all TipJars belonging assigned to the wallet_id"""
    rows = await db.fetchall(
        "SELECT * FROM tipjar.TipJars WHERE wallet = :wallet_id",
        {"wallet_id": wallet_id},
    )
    return [TipJar(**row) for row in rows] if rows else None


async def delete_tipjar(tipjar_id: int) -> None:
    """Delete a TipJar and all corresponding Tips"""
    tips = await get_tipjar_tips(tipjar_id)
    for tip in tips:
        await delete_tip(tip.id)
    await db.execute("DELETE FROM tipjar.TipJars WHERE id = :id", {"id": tipjar_id})


async def get_tip(tip_id: str) -> Optional[Tip]:
    """Return a Tip"""
    row = await db.fetchone("SELECT * FROM tipjar.Tips WHERE id = :id", {"id": tip_id})
    return Tip(**row) if row else None


async def get_tipjar_tips(tipjar_id: int) -> list[Tip]:
    """Return all Tips for a tipjar"""
    rows = await db.fetchall(
        "SELECT * FROM tipjar.Tips WHERE tipjar = :tipjar_id", {"tipjar_id": tipjar_id}
    )
    return [Tip(**row) for row in rows]


async def get_tips(wallet_id: str) -> Optional[list]:
    """Return all Tips assigned to wallet_id"""
    rows = await db.fetchall(
        "SELECT * FROM tipjar.Tips WHERE wallet = :wallet_id", {"wallet_id": wallet_id}
    )
    return [Tip(**row) for row in rows] if rows else None


async def delete_tip(tip_id: str) -> None:
    """Delete a Tip and its corresponding statspay charge"""
    await db.execute("DELETE FROM tipjar.Tips WHERE id = :id", {"id": tip_id})


async def update_tip(tip: Tip) -> Tip:
    """Update a Tip"""
    await db.execute(update_query("tipjar.Tips", tip), tip.dict())
    return tip


async def update_tipjar(tipjar: TipJar) -> TipJar:
    """Update a tipjar"""
    await db.execute(update_query("tipjar.TipJars", tipjar), tipjar.dict())
    return tipjar
