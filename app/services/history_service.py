# 预测历史记录服务
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


class PredictionHistoryService:
    """预测历史记录服务 - 持久化存储预测结果"""

    def __init__(self, storage_path: str = "data/prediction_history"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.history_file = self.storage_path / "history.json"
        self._cache: Dict[str, Any] = {}
        self._load_history()

    def _load_history(self):
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
            except Exception as e:
                print(f"加载历史记录失败: {e}")
                self._cache = {"predictions": [], "by_event": {}}
        else:
            self._cache = {"predictions": [], "by_event": {}}

    def _save_history(self):
        """保存历史记录"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")

    async def save_prediction(
        self,
        event_id: str,
        event_title: str,
        event_description: str,
        prediction_result: Dict[str, Any],
        scenario_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        保存预测结果

        Args:
            event_id: 事件ID
            event_title: 事件标题
            event_description: 事件描述
            prediction_result: 预测分析结果
            scenario_result: 情景推演结果（可选）

        Returns:
            保存的记录
        """
        record_id = f"pred_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{event_id[:8]}"

        record = {
            "id": record_id,
            "event_id": event_id,
            "event_title": event_title,
            "event_description": event_description[:500],  # 限制描述长度
            "prediction": {
                "trend": prediction_result.get("prediction", {}).get("trend", "N/A"),
                "confidence": prediction_result.get("prediction", {}).get("confidence", 0),
                "summary": prediction_result.get("prediction", {}).get("summary", ""),
                "key_insights": prediction_result.get("prediction", {}).get("key_insights", []),
                "timeline": prediction_result.get("prediction", {}).get("timeline", [])
            },
            "scenario": scenario_result,
            "overall_confidence": prediction_result.get("overall_confidence", 0.5),
            "category": prediction_result.get("category", "Other"),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }

        # 添加到历史列表
        self._cache["predictions"].insert(0, record)

        # 按事件ID索引
        if event_id not in self._cache["by_event"]:
            self._cache["by_event"][event_id] = []
        self._cache["by_event"][event_id].insert(0, record_id)

        # 限制历史记录数量
        if len(self._cache["predictions"]) > 1000:
            removed = self._cache["predictions"][1000:]
            for r in removed:
                if r["event_id"] in self._cache["by_event"]:
                    self._cache["by_event"][r["event_id"]] = [
                        rid for rid in self._cache["by_event"][r["event_id"]]
                        if rid != r["id"]
                    ]
            self._cache["predictions"] = self._cache["predictions"][:1000]

        self._save_history()

        return record

    async def get_prediction(self, record_id: str) -> Optional[Dict[str, Any]]:
        """获取单条预测记录"""
        for record in self._cache["predictions"]:
            if record["id"] == record_id:
                return record
        return None

    async def get_predictions_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        """获取事件的所有预测记录"""
        records = []
        for record in self._cache["predictions"]:
            if record["event_id"] == event_id:
                records.append(record)
        return records

    async def list_predictions(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        列出预测记录

        Args:
            page: 页码
            page_size: 每页数量
            category: 筛选类别
            start_date: 开始日期 (ISO格式)
            end_date: 结束日期 (ISO格式)

        Returns:
            包含记录列表和分页信息的字典
        """
        filtered = self._cache["predictions"]

        # 类别筛选
        if category:
            filtered = [r for r in filtered if r.get("category") == category]

        # 日期筛选
        if start_date:
            filtered = [r for r in filtered if r.get("created_at", "") >= start_date]
        if end_date:
            filtered = [r for r in filtered if r.get("created_at", "") <= end_date]

        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size

        return {
            "predictions": filtered[start:end],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def delete_prediction(self, record_id: str) -> bool:
        """删除预测记录"""
        for i, record in enumerate(self._cache["predictions"]):
            if record["id"] == record_id:
                # 从主列表移除
                self._cache["predictions"].pop(i)
                # 从事件索引移除
                event_id = record["event_id"]
                if event_id in self._cache["by_event"]:
                    self._cache["by_event"][event_id] = [
                        rid for rid in self._cache["by_event"][event_id]
                        if rid != record_id
                    ]
                self._save_history()
                return True
        return False

    async def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        predictions = self._cache["predictions"]

        if not predictions:
            return {
                "total": 0,
                "categories": {},
                "avg_confidence": 0,
                "recent_count": 0
            }

        # 类别统计
        categories = {}
        for p in predictions:
            cat = p.get("category", "Other")
            categories[cat] = categories.get(cat, 0) + 1

        # 平均置信度
        confidences = [p.get("overall_confidence", 0) for p in predictions if p.get("overall_confidence")]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # 最近24小时预测数
        now = datetime.utcnow()
        recent_count = 0
        for p in predictions:
            try:
                created = datetime.fromisoformat(p.get("created_at", ""))
                if (now - created).total_seconds() < 86400:
                    recent_count += 1
            except:
                pass

        return {
            "total": len(predictions),
            "categories": categories,
            "avg_confidence": round(avg_confidence, 2),
            "recent_count": recent_count
        }

    async def update_prediction(
        self,
        record_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """更新预测记录"""
        for record in self._cache["predictions"]:
            if record["id"] == record_id:
                # 更新允许的字段
                if "scenario" in updates:
                    record["scenario"] = updates["scenario"]
                record["updated_at"] = datetime.utcnow().isoformat()
                self._save_history()
                return record
        return None

    async def export_history(self, format: str = "json") -> str:
        """导出历史记录"""
        if format == "json":
            return json.dumps(self._cache["predictions"], ensure_ascii=False, indent=2)
        elif format == "csv":
            import csv
            import io
            output = io.StringIO()
            writer = csv.writer(output)
            # 写入表头
            writer.writerow([
                "ID", "事件ID", "事件标题", "类别", "趋势",
                "置信度", "创建时间"
            ])
            # 写入数据
            for p in self._cache["predictions"]:
                writer.writerow([
                    p.get("id", ""),
                    p.get("event_id", ""),
                    p.get("event_title", ""),
                    p.get("category", ""),
                    p.get("prediction", {}).get("trend", ""),
                    p.get("overall_confidence", ""),
                    p.get("created_at", "")
                ])
            return output.getvalue()
        else:
            return json.dumps(self._cache["predictions"], ensure_ascii=False)


# 全局服务实例
history_service = PredictionHistoryService()
