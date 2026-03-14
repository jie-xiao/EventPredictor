import asyncio
from app.services.rss_service import rss_service

async def test():
    print("Fetching RSS feeds...")
    events = await rss_service.fetch_all_feeds()
    print(f"Total events: {len(events)}")
    for e in events[:3]:
        print(f"- {e.get('title', 'No title')[:50]}")

asyncio.run(test())
