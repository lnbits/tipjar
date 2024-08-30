from typing import Optional

from lnbits.db import SQLITE, Database

from .models import CreateTipJar, Tip, TipJar

db = Database("ext_tipjar")


async def create_tip(
    tip_id: str, wallet: str, message: str, name: str, sats: int, tipjar: str
) -> Tip:
    """Create a new Tip"""
    await db.execute(
        """
        INSERT INTO tipjar.Tips (
            id,
            wallet,
            name,
            message,
            sats,
            tipjar
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (tip_id, wallet, name, message, sats, tipjar),
    )

    tip = await get_tip(tip_id)
    assert tip, "Newly created tip couldn't be retrieved"
    return tip


async def create_tipjar(data: CreateTipJar) -> TipJar:
    """Create a new TipJar"""

    returning = "" if db.type == SQLITE else "RETURNING ID"
    method = db.execute if db.type == SQLITE else db.fetchone

    result = await method(
        f"""
        INSERT INTO tipjar.TipJars (
            name,
            wallet,
            webhook,
            onchain,
            onchain_limit
        )
        VALUES (?, ?, ?, ?, ?)
        {returning}
        """,
        (data.name, data.wallet, data.webhook, data.onchain, data.onchain_limit),
    )
    if db.type == SQLITE:
        tipjar_id = result._result_proxy.lastrowid
    else:
        tipjar_id = result[0]  # type: ignore

    tipjar = await get_tipjar(tipjar_id)
    assert tipjar
    return tipjar


async def get_tipjar(tipjar_id: int) -> Optional[TipJar]:
    """Return a tipjar by ID"""
    row = await db.fetchone("SELECT * FROM tipjar.TipJars WHERE id = ?", (tipjar_id,))
    return TipJar(**row) if row else None


async def get_tipjars(wallet_id: str) -> Optional[list]:
    """Return all TipJars belonging assigned to the wallet_id"""
    rows = await db.fetchall(
        "SELECT * FROM tipjar.TipJars WHERE wallet = ?", (wallet_id,)
    )
    return [TipJar(**row) for row in rows] if rows else None


async def delete_tipjar(tipjar_id: int) -> None:
    """Delete a TipJar and all corresponding Tips"""
    tips = await get_tipjar_tips(tipjar_id)
    for tip in tips:
        await delete_tip(tip.id)
    await db.execute("DELETE FROM tipjar.TipJars WHERE id = ?", (tipjar_id,))


async def get_tip(tip_id: str) -> Optional[Tip]:
    """Return a Tip"""
    row = await db.fetchone("SELECT * FROM tipjar.Tips WHERE id = ?", (tip_id,))
    return Tip(**row) if row else None


async def get_tipjar_tips(tipjar_id: int) -> list[Tip]:
    """Return all Tips for a tipjar"""
    rows = await db.fetchall("SELECT * FROM tipjar.Tips WHERE tipjar = ?", (tipjar_id,))
    return [Tip(**row) for row in rows]


async def get_tips(wallet_id: str) -> Optional[list]:
    """Return all Tips assigned to wallet_id"""
    rows = await db.fetchall("SELECT * FROM tipjar.Tips WHERE wallet = ?", (wallet_id,))
    return [Tip(**row) for row in rows] if rows else None


async def delete_tip(tip_id: str) -> None:
    """Delete a Tip and its corresponding statspay charge"""
    await db.execute("DELETE FROM tipjar.Tips WHERE id = ?", (tip_id,))


async def update_tip(tip_id: str, **kwargs) -> Tip:
    """Update a Tip"""
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE tipjar.Tips SET {q} WHERE id = ?", (*kwargs.values(), tip_id)
    )
    row = await db.fetchone("SELECT * FROM tipjar.Tips WHERE id = ?", (tip_id,))
    assert row, "Newly updated tip couldn't be retrieved"
    return Tip(**row)


async def update_tipjar(tipjar_id: str, **kwargs) -> TipJar:
    """Update a tipjar"""
    q = ", ".join([f"{field[0]} = ?" for field in kwargs.items()])
    await db.execute(
        f"UPDATE tipjar.TipJars SET {q} WHERE id = ?", (*kwargs.values(), tipjar_id)
    )
    row = await db.fetchone("SELECT * FROM tipjar.TipJars WHERE id = ?", (tipjar_id,))
    assert row, "Newly updated tipjar couldn't be retrieved"
    return TipJar(**row)
