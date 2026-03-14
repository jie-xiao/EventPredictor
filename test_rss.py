import asyncio
import httpx

async def test_rss():
    url = "https://feeds.bbci.co.uk/news/world/rss.xml"
    proxy = "http://192.168.2.115:10811"
    
    try:
        async with httpx.AsyncClient(timeout=15, proxies={"http://": proxy, "https://": proxy}) as client:
            response = await client.get(url)
            print(f"Status: {response.status_code}")
            print(f"Content length: {len(response.text)}")
            print(f"First 200 chars: {response.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test_rss())
