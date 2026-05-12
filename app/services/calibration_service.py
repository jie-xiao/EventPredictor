# app/services/calibration_service.py
"""Calibration service: Platt scaling and calibration metrics."""
import json
from typing import Dict, Any, List, Optional
from sklearn.linear_model import LogisticRegression
import numpy as np


class CalibrationService:
    """Calibrates prediction confidence scores using Platt scaling
    and computes calibration metrics (Brier score, rating)."""

    async def calibrate(
        self, scores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply Platt scaling to calibrate confidence scores."""
        if len(scores) < 3:
            return scores

        X = np.array([[s["confidence"]] for s in scores])
        y = np.array([1 if s["correct"] else 0 for s in scores])

        try:
            model = LogisticRegression()
            model.fit(X, y)
            probs = model.predict_proba(X)[:, 1]

            result = []
            for i, s in enumerate(scores):
                s_copy = dict(s)
                s_copy["calibrated_confidence"] = round(float(probs[i]), 4)
                result.append(s_copy)
            return result
        except Exception:
            # Fallback: no calibration possible
            return scores

    def _compute_brier_score(self, scores: List[Dict]) -> float:
        if not scores:
            return 0.0
        total = 0.0
        for s in scores:
            conf = s.get("confidence", 0.5)
            actual = 1.0 if s.get("correct") else 0.0
            total += (conf - actual) ** 2
        return round(total / len(scores), 4)

    def _get_rating(self, brier_score: float) -> str:
        if brier_score <= 0.10:
            return "优秀"
        elif brier_score <= 0.15:
            return "良好"
        elif brier_score <= 0.25:
            return "一般"
        else:
            return "需改进"

    async def get_calibration_status(self) -> Dict[str, Any]:
        """Get current calibration stats from prediction_records."""
        try:
            from app.db.database import get_session_factory
            from app.db.models import PredictionRecord
            from sqlalchemy import select

            session_factory = get_session_factory()
            async with session_factory() as session:
                result = await session.execute(select(PredictionRecord))
                records = result.scalars().all()

            total = len(records)
            resolved = [r for r in records if r.outcome_status in ("correct", "incorrect", "partial")]
            pending = total - len(resolved)

            if not resolved:
                return {
                    "total_predictions": total,
                    "resolved": 0,
                    "pending": pending,
                    "directional_accuracy": 0.0,
                    "brier_score": 0.0,
                    "calibration_rating": "数据不足",
                }

            correct = sum(1 for r in resolved if r.outcome_status == "correct")
            dir_acc = correct / len(resolved)

            # Brier score
            brier_total = 0.0
            for r in resolved:
                actual = 1.0 if r.outcome_status == "correct" else 0.0
                brier_total += (r.confidence - actual) ** 2
            brier = brier_total / len(resolved)

            return {
                "total_predictions": total,
                "resolved": len(resolved),
                "pending": pending,
                "directional_accuracy": round(dir_acc, 4),
                "brier_score": round(brier, 4),
                "calibration_rating": self._get_rating(brier),
            }
        except Exception:
            return {
                "total_predictions": 0,
                "resolved": 0,
                "pending": 0,
                "directional_accuracy": 0.0,
                "brier_score": 0.0,
                "calibration_rating": "数据不足",
            }

    async def get_calibration_curve(self, n_bins: int = 10) -> Dict[str, Any]:
        """Get calibration curve from resolved predictions."""
        try:
            from app.db.database import get_session_factory
            from app.db.models import PredictionRecord
            from sqlalchemy import select

            session_factory = get_session_factory()
            async with session_factory() as session:
                result = await session.execute(select(PredictionRecord))
                records = result.scalars().all()

            resolved = [r for r in records if r.outcome_status in ("correct", "incorrect", "partial")]
            if not resolved:
                return {"curve": [], "bins": n_bins}

            bin_size = 1.0 / n_bins
            bins = [[] for _ in range(n_bins)]

            for r in resolved:
                idx = min(int(r.confidence / bin_size), n_bins - 1)
                actual = 1.0 if r.outcome_status == "correct" else 0.0
                bins[idx].append((r.confidence, actual))

            curve = []
            for i, bucket in enumerate(bins):
                if not bucket:
                    continue
                confs = [b[0] for b in bucket]
                actuals = [b[1] for b in bucket]
                curve.append({
                    "bin_low": round(i * bin_size, 2),
                    "bin_high": round((i + 1) * bin_size, 2),
                    "avg_predicted": round(sum(confs) / len(confs), 4),
                    "avg_actual": round(sum(actuals) / len(actuals), 4),
                    "count": len(bucket),
                })

            return {"curve": curve, "bins": n_bins}
        except Exception:
            return {"curve": [], "bins": n_bins}


# Global singleton
calibration_service = CalibrationService()
