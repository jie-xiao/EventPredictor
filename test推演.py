import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1'
import requests
import json

# 当前热点事件推演
event = {
    'title': '美国宣布对中国AI芯片实施全面出口禁令',
    'description': '美国商务部宣布将对中国实施更严格的AI芯片和半导体设备出口限制，旨在遏制中国人工智能产业发展。分析对全球半导体产业链、科技竞争格局的影响。',
    'category': 'Technology',
    'importance': 5
}

r = requests.post('http://localhost:8005/api/v1/predict', json=event, timeout=120)
print(f'Status: {r.status_code}')
result = r.json()
print(f'Prediction ID: {result.get("prediction_id")}')
print(f'Event ID: {result.get("event_id")}')
print(f'Trend: {result.get("trend")}')
print(f'Confidence: {result.get("confidence")}%')
print(f'Time Horizon: {result.get("time_horizon")}')
print(f'Impact Scope: {result.get("impact_scope")}')
print(f'Sentiment: {result.get("sentiment")}')
print(f'Reasoning: {result.get("reasoning")[:500]}')
