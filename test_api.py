import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        # 测试health端点
        r = await client.get('http://localhost:8004/health')
        print(f'Health Status: {r.status_code}')
        print(f'Health Response: {r.text}')
        
        # 测试predict端点
        r = await client.post(
            'http://localhost:8004/api/v1/predict',
            json={'title': 'test', 'description': 'test', 'category': 'Technology', 'importance': 3}
        )
        print(f'Predict Status: {r.status_code}')
        print(f'Predict Response: {r.text}')

asyncio.run(test())
