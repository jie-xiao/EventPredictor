import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
os.environ['no_proxy'] = 'localhost,127.0.0.1'

import asyncio
from app.api.models import PredictRequest
from app.services.prediction_service import prediction_service

async def test():
    req = PredictRequest(title='test', description='test', category='Technology', importance=3)
    try:
        result = await prediction_service.predict(req)
        print('Success:', result)
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

asyncio.run(test())
