# 直接运行推演测试
import sys
sys.path.insert(0, 'E:/EventPredictor')

import asyncio
from app.services.prediction_service import prediction_service
from app.api.models import PredictRequest

async def run_prediction():
    # 创建请求
    request = PredictRequest(
        title="美联储宣布降息50个基点",
        description="美联储宣布将联邦基金利率下调50个基点，以应对经济增长放缓",
        category="Monetary Policy",
        importance=5
    )
    
    # 执行预测
    result = await prediction_service.predict(request)
    
    # 输出结果
    print("="*50)
    print("推演结果")
    print("="*50)
    print(f"事件: {request.title}")
    print(f"预测趋势: {result.trend}")
    print(f"置信度: {result.confidence:.0%}")
    print(f"时间范围: {result.time_horizon}")
    print(f"推理: {result.reasoning}")
    print(f"因素: {result.factors}")
    
    return result

# 运行
result = asyncio.run(run_prediction())
