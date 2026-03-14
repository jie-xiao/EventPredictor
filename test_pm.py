import asyncio
from app.services.polymarket_service import polymarket_service

async def test():
    try:
        markets = await polymarket_service.get_trending_markets()
        print("Polymarket Markets:", markets[:2] if markets else "None")
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
