import httpx

from lnbits.app import settings


async def create_charge(data: dict, api_key: str):
    async with httpx.AsyncClient() as client:
        headers = {"X-API-KEY": api_key}
        r = await client.post(
            url=f"http://{settings.host}:{settings.port}/satspay/api/v1/charge",
            headers=headers,
            json=data,
        )
        r.raise_for_status()
        return r.json()["id"]
