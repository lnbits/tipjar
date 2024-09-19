from typing import Optional

from pydantic import BaseModel


class CreateTip(BaseModel):
    id: str
    wallet: str
    sats: int
    tipjar: int
    name: str = "Anonymous"
    message: str = ""


class Tip(BaseModel):
    """A Tip represents a single donation"""

    id: str  # This ID always corresponds to a satspay charge ID
    wallet: str
    name: str  # Name of the donor
    message: str  # Donation message
    sats: int
    tipjar: str  # The ID of the corresponding tip jar


class CreateTipJar(BaseModel):
    name: str
    wallet: str
    webhook: Optional[str]
    onchain: Optional[str]
    onchain_limit: Optional[int]


class CreateTips(BaseModel):
    name: str
    sats: str
    tipjar: str
    message: str


class TipJar(BaseModel):
    """A TipJar represents a user's tip jar"""

    id: str
    name: str  # The name of the donatee
    wallet: str  # Lightning wallet
    onchain: Optional[str]  # Watchonly wallet
    webhook: Optional[str]  # URL to POST tips to
    onchain_limit: Optional[int]  # Bellow this amount, tips will be offchain only
