import asyncio
from app.services.worldmonitor_service import worldmonitor_service

async def test():
    try:
        result = await worldmonitor_service.fetch_events(limit=5)
        print("WorldMonitor Events:", result)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
