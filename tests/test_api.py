# EventPredictor 测试文件
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.models import PredictRequest, TrendDirection


client = TestClient(app)


class TestHealthEndpoints:
    """健康检查接口测试"""
    
    def test_health_check(self):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data
    
    def test_root(self):
        """测试根路径"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["version"] == "1.0.0"


class TestPredictionEndpoints:
    """预测接口测试"""
    
    def test_predict_basic(self):
        """测试基本预测"""
        request_data = {
            "title": "Federal Reserve cuts rates by 50 basis points",
            "description": "The Fed announced a 50bp rate cut to address economic slowdown",
            "source": "WorldMonitor",
            "category": "Monetary Policy",
            "importance": 5
        }
        
        response = client.post("/api/v1/predict", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "prediction_id" in data
        assert "event_id" in data
        assert "trend" in data
        assert "confidence" in data
        assert "reasoning" in data
        assert "time_horizon" in data
        assert "factors" in data
    
    def test_predict_minimal(self):
        """测试最小请求"""
        request_data = {
            "title": "Test Event",
            "description": "Test Description"
        }
        
        response = client.post("/api/v1/predict", json=request_data)
        assert response.status_code == 200
    
    def test_predict_validation(self):
        """测试请求验证"""
        # 缺少必需字段
        request_data = {"title": "Test"}
        response = client.post("/api/v1/predict", json=request_data)
        assert response.status_code == 422
    
    def test_invalid_importance(self):
        """测试无效的重要性值"""
        request_data = {
            "title": "Test Event",
            "description": "Test Description",
            "importance": 10  # 超过范围
        }
        response = client.post("/api/v1/predict", json=request_data)
        assert response.status_code == 422


class TestEventEndpoints:
    """事件接口测试"""
    
    def test_list_events_empty(self):
        """测试空事件列表"""
        response = client.get("/api/v1/events")
        assert response.status_code == 200
        data = response.json()
        assert "events" in data
        assert "total" in data
    
    def test_get_event_not_found(self):
        """测试获取不存在的事件"""
        response = client.get("/api/v1/events/not-found-id")
        assert response.status_code == 404


class TestPredictionResults:
    """预测结果测试"""
    
    @pytest.fixture
    def sample_prediction(self):
        """创建示例预测请求"""
        return {
            "title": "Central Bank maintains interest rates",
            "description": "The central bank decided to keep rates unchanged",
            "source": "Test",
            "category": "Monetary Policy",
            "importance": 3
        }
    
    def test_prediction_trend_values(self, sample_prediction):
        """测试预测趋势值"""
        response = client.post("/api/v1/predict", json=sample_prediction)
        data = response.json()

        # 验证趋势在允许的范围内 (支持中文和英文)
        valid_trends = ["UP", "DOWN", "SIDEWAYS", "UNCERTAIN", "上涨", "下跌", "平稳", "不确定"]
        assert data["trend"] in valid_trends
    
    def test_prediction_confidence_range(self, sample_prediction):
        """测试置信度范围"""
        response = client.post("/api/v1/predict", json=sample_prediction)
        data = response.json()

        # 验证置信度 - 可能是百分比(0-100)或小数(0-1)
        confidence = data["confidence"]
        if confidence > 1:
            # 如果是百分比形式
            assert 0 <= confidence <= 100
        else:
            # 如果是小数形式
            assert 0 <= confidence <= 1
    
    def test_prediction_id_format(self, sample_prediction):
        """测试预测ID格式"""
        response = client.post("/api/v1/predict", json=sample_prediction)
        data = response.json()
        
        # 验证ID格式
        assert data["prediction_id"].startswith("pred-")
        assert data["event_id"].startswith("evt-")


class TestIntegration:
    """集成测试"""
    
    def test_full_prediction_flow(self):
        """完整预测流程测试"""
        # 1. 创建预测
        request_data = {
            "title": "Major geopolitical event",
            "description": "Significant international development",
            "category": "Geopolitical",
            "importance": 5
        }
        
        response = client.post("/api/v1/predict", json=request_data)
        assert response.status_code == 200
        
        pred_data = response.json()
        prediction_id = pred_data["prediction_id"]
        event_id = pred_data["event_id"]
        
        # 2. 获取预测
        response = client.get(f"/api/v1/predictions/{prediction_id}")
        assert response.status_code == 200
        
        # 3. 获取事件
        response = client.get(f"/api/v1/events/{event_id}")
        assert response.status_code == 200
        
        # 4. 列出预测
        response = client.get("/api/v1/predictions")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
