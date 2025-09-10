from pydantic import BaseModel


class CreateTip(BaseModel):
    id: str
    wallet: str
    sats: int
    tipjar: str
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


class CreateTips(BaseModel):
    name: str
    sats: str
    tipjar: str
    message: str


class CreateTipJar(BaseModel):
    name: str
    wallet: str
    webhook: str | None = ""
    onchain: str | None = ""
    onchain_limit: int | None = 0


class TipJar(CreateTipJar):
    """A TipJar represents a user's tip jar"""

    id: str
