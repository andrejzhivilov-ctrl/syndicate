"""Report actual public provider availability from the machine running this command."""
import asyncio
import json

from src.sam_public_sources import URLS, read


async def probe(key):
    try:
        result = await asyncio.wait_for(read(key), timeout=25)
    except asyncio.TimeoutError:
        result = {"status": "unavailable", "reason": "timeout"}
    return {"source": key, "status": result["status"], "reason": result.get("reason"),
            "retrieved_at": result.get("retrieved_at")}


async def main():
    for row in await asyncio.gather(*(probe(key) for key in URLS)):
        print(json.dumps(row, ensure_ascii=True))


if __name__ == "__main__":
    asyncio.run(main())
