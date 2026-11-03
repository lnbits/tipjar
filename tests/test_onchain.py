from datetime import datetime, timezone
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import HTTPException
from lnbits.core.models import KeyType, User, Wallet, WalletTypeInfo

from .. import views_api
from ..models import CreateTipJar, CreateTips, TipJar

TIME = datetime(2025, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def merchant(monkeypatch):
    wallet = Wallet(
        id="merchant",
        name="Tips",
        user="owner",
        adminkey="admin",
        inkey="invoice",
        created_at=TIME,
        updated_at=TIME,
    )
    chain = wallet.model_copy(
        update={"id": "chain", "wallet_type": "onchain", "onchain_network": "Testnet4"}
    )
    user = User(id="owner", wallets=[wallet, chain], created_at=TIME, updated_at=TIME)
    monkeypatch.setattr(views_api, "get_user", AsyncMock(return_value=user))
    monkeypatch.setattr(views_api, "check_satspay", AsyncMock(return_value=True))
    return WalletTypeInfo(KeyType.admin, wallet)


@pytest.mark.asyncio
@pytest.mark.parametrize("edit", [False, True])
@pytest.mark.parametrize(
    "wallet, onchain, status",
    [
        ("merchant", "core:chain", 400),
        ("merchant", "core:foreign", 403),
        ("foreign", "core:chain", 403),
    ],
)
async def test_reject_invalid_wallet_before_saving(
    merchant, monkeypatch, edit, wallet, onchain, status
):
    jar = TipJar(id="jar", name="Before", wallet="merchant", onchain="watch-id")
    monkeypatch.setattr(views_api, "get_tipjar", AsyncMock(return_value=jar))
    monkeypatch.setattr(
        views_api, "get_satspay_network", AsyncMock(return_value="Mainnet")
    )
    create = AsyncMock()
    update = AsyncMock()
    monkeypatch.setattr(views_api, "create_tipjar", create)
    monkeypatch.setattr(views_api, "update_tipjar", update)

    data = CreateTipJar(name="After", wallet=wallet, onchain=onchain)
    with pytest.raises(HTTPException) as exc:
        if edit:
            await views_api.api_update_tipjar(jar.id, data, merchant)
        else:
            await views_api.api_create_tipjar(data, merchant)
    assert exc.value.status_code == status
    create.assert_not_awaited()
    update.assert_not_awaited()
    assert (jar.name, jar.onchain) == ("Before", "watch-id")


@pytest.mark.asyncio
@pytest.mark.parametrize("reference", ["core:unavailable", " "])
async def test_edit_preserves_saved_reference_without_discovery(
    merchant, monkeypatch, reference
):
    jar = TipJar(id="jar", name="Before", wallet="merchant", onchain=reference)
    monkeypatch.setattr(views_api, "get_tipjar", AsyncMock(return_value=jar))
    network = AsyncMock(side_effect=httpx.ConnectError("SatsPay unavailable"))
    monkeypatch.setattr(views_api, "get_satspay_network", network)
    save = AsyncMock(side_effect=lambda updated: updated)
    monkeypatch.setattr(views_api, "update_tipjar", save)

    data = CreateTipJar(name="After", wallet="merchant", onchain=reference)
    result = await views_api.api_update_tipjar(jar.id, data, merchant)
    assert (result.name, result.onchain) == ("After", reference)
    save.assert_awaited_once_with(result)
    network.assert_not_awaited()


@pytest.mark.asyncio
async def test_checkout_forwards_core_reference_only_above_limit(merchant, monkeypatch):
    jar = TipJar(
        id="jar",
        name="Tips",
        wallet="merchant",
        onchain="core:chain",
        onchain_limit=100,
    )
    monkeypatch.setattr(views_api, "get_tipjar", AsyncMock(return_value=jar))
    monkeypatch.setattr(
        views_api, "get_wallet", AsyncMock(return_value=merchant.wallet)
    )
    charge = AsyncMock(return_value="charge")
    monkeypatch.setattr(views_api, "create_charge", charge)
    monkeypatch.setattr(views_api, "create_tip", AsyncMock())

    for sats in (100, 101):
        tip = CreateTips(name="Donor", tipjar=jar.id, sats=sats, message="")
        assert await views_api.api_create_tip(tip) == {
            "redirect_url": "/satspay/charge"
        }
    assert [
        call.kwargs["data"]["onchainwallet"] for call in charge.await_args_list
    ] == [
        None,
        "core:chain",
    ]
