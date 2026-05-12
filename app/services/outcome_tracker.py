# app/services/outcome_tracker.py
"""Outcome tracker: periodically resolves pending predictions and updates status."""
import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional


class OutcomeTracker:
    """Background service that resolves prediction outcomes.
    Checks expired predictions and marks them."""

    def __init__(self, interval: int = 3600):
        self.interval = interval
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self):
        while self._running:
            try:
                await self._resolve_expired()
            except Exception:
                pass
            await asyncio.sleep(self.interval)

    async def _resolve_expired(self):
        """Check for predictions past their expiry and auto-resolve."""
        try:
            from app.db.database import get_session_factory
            from app.db.models import PredictionRecord
            from sqlalchemy import select, update

            session_factory = get_session_factory()
            async with session_factory() as session:
                result = await session.execute(
                    select(PredictionRecord).where(
                        PredictionRecord.outcome_status == "pending",
                        PredictionRecord.predicted_expires.isnot(None),
                    )
                )
                pending = result.scalars().all()

                now = datetime.now(timezone.utc).isoformat()
                for p in pending:
                    if p.predicted_expires and p.predicted_expires < now:
                        # Mark as unresolved (uncertain outcome)
                        p.outcome_status = "partial"
                        p.actual_outcome = "Auto-expired without resolution"
                        p.resolved_at = now
                        p.resolution_source = "auto_expired"

                await session.commit()
        except Exception:
            pass

    async def resolve_manual(
        self,
        prediction_id: str,
        outcome_status: str,
        actual_outcome: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Manually resolve a prediction."""
        try:
            from app.db.database import get_session_factory
            from app.db.models import PredictionRecord
            from sqlalchemy import select

            session_factory = get_session_factory()
            async with session_factory() as session:
                result = await session.execute(
                    select(PredictionRecord).where(
                        PredictionRecord.prediction_id == prediction_id
                    )
                )
                record = result.scalar_one_or_none()
                if record is None:
                    return None

                record.outcome_status = outcome_status
                record.actual_outcome = actual_outcome
                record.resolved_at = datetime.now(timezone.utc).isoformat()
                record.resolution_source = "manual"

                await session.commit()

                return {
                    "prediction_id": record.prediction_id,
                    "outcome_status": record.outcome_status,
                    "resolved_at": record.resolved_at,
                }
        except Exception:
            return None

    def _check_single_prediction(self, prediction: Dict) -> Dict[str, Any]:
        """Check resolution logic for a single prediction (test helper)."""
        result = dict(prediction)
        if result.get("outcome_status") == "pending":
            predicted_at = result.get("predicted_at", "")
            if predicted_at:
                try:
                    pred_dt = datetime.fromisoformat(predicted_at.replace("Z", "+00:00"))
                    if pred_dt.tzinfo is None:
                        pred_dt = pred_dt.replace(tzinfo=timezone.utc)
                    now = datetime.now(timezone.utc)
                    if (now - pred_dt) > timedelta(days=30):
                        result["outcome_status"] = "partial"
                        result["resolution_source"] = "auto_expired"
                except Exception:
                    pass
        return result

    def _apply_resolution(
        self, prediction: Dict, outcome_status: str, source: str
    ) -> Dict[str, Any]:
        """Apply a resolution to a prediction dict (test helper)."""
        result = dict(prediction)
        result["outcome_status"] = outcome_status
        result["resolution_source"] = source
        result["resolved_at"] = datetime.now(timezone.utc).isoformat()
        return result

    def _compute_stats(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Compute stats from a list of predictions (test helper)."""
        total = len(predictions)
        resolved = [p for p in predictions if p.get("outcome_status") in ("correct", "incorrect", "partial")]
        correct = sum(1 for p in resolved if p.get("outcome_status") == "correct")
        return {
            "total": total,
            "resolved": len(resolved),
            "correct": correct,
            "accuracy": round(correct / len(resolved), 4) if resolved else 0.0,
        }


# Global singleton
outcome_tracker = OutcomeTracker()
