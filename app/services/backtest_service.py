# app/services/backtest_service.py
"""Backtest engine: batch evaluate prediction accuracy against historical outcomes."""
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List


class BacktestService:
    """Runs backtests on resolved predictions to compute Brier score,
    directional accuracy, and calibration curves."""

    async def run_backtest(
        self,
        predictions: List[Dict[str, Any]],
        config_snapshot: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        resolved = [p for p in predictions if p.get("outcome_status") in ("correct", "incorrect", "partial")]

        event_count = len(predictions)
        resolved_count = len(resolved)

        brier = self._compute_brier_score(resolved) if resolved else 0.0
        dir_acc = self._compute_directional_accuracy(resolved) if resolved else 0.0
        curve = self._generate_calibration_curve(resolved) if resolved else []
        auc = self._compute_auc(resolved) if resolved else 0.0
        sharpe = self._compute_sharpe(resolved) if resolved else 0.0

        duration_ms = int((time.time() - start) * 1000)

        # Persist backtest run
        try:
            from app.db.database import get_session_factory
            from app.db.models import BacktestRun
            session_factory = get_session_factory()
            async with session_factory() as session:
                run = BacktestRun(
                    event_count=event_count,
                    resolved_count=resolved_count,
                    brier_score=round(brier, 6) if brier else None,
                    auc=round(auc, 4) if auc else None,
                    directional_accuracy=round(dir_acc, 4),
                    sharpe_ratio=round(sharpe, 4) if sharpe else None,
                    calibration_curve=json.dumps(curve) if curve else None,
                    config_snapshot=json.dumps(config_snapshot) if config_snapshot else None,
                    duration_ms=duration_ms,
                )
                session.add(run)
                await session.commit()
        except Exception:
            pass

        return {
            "event_count": event_count,
            "resolved_count": resolved_count,
            "brier_score": round(brier, 4),
            "auc": round(auc, 4),
            "directional_accuracy": round(dir_acc, 4),
            "sharpe_ratio": round(sharpe, 4),
            "calibration_curve": curve,
            "duration_ms": duration_ms,
        }

    def _compute_brier_score(self, resolved: List[Dict]) -> float:
        if not resolved:
            return 0.0
        total = 0.0
        for p in resolved:
            confidence = p.get("confidence", 0.5)
            actual = 1.0 if p.get("outcome_status") == "correct" else 0.0
            total += (confidence - actual) ** 2
        return total / len(resolved)

    def _compute_directional_accuracy(self, resolved: List[Dict]) -> float:
        if not resolved:
            return 0.0
        correct = sum(1 for p in resolved if p.get("outcome_status") == "correct")
        return correct / len(resolved)

    def _generate_calibration_curve(
        self, resolved: List[Dict], n_bins: int = 10
    ) -> List[Dict[str, Any]]:
        if not resolved:
            return []
        bin_size = 1.0 / n_bins
        bins = [[] for _ in range(n_bins)]

        for p in resolved:
            conf = p.get("confidence", 0.5)
            idx = min(int(conf / bin_size), n_bins - 1)
            actual = 1.0 if p.get("outcome_status") == "correct" else 0.0
            bins[idx].append((conf, actual))

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
        return curve

    def _compute_auc(self, resolved: List[Dict]) -> float:
        if len(resolved) < 2:
            return 0.0
        sorted_preds = sorted(resolved, key=lambda p: p.get("confidence", 0.5), reverse=True)
        pos = sum(1 for p in resolved if p.get("outcome_status") == "correct")
        neg = len(resolved) - pos
        if pos == 0 or neg == 0:
            return 0.5
        tp = 0
        fp = 0
        auc = 0.0
        prev_fpr = 0.0
        for p in sorted_preds:
            if p.get("outcome_status") == "correct":
                tp += 1
            else:
                fp += 1
                tpr = tp / pos
                fpr = fp / neg
                auc += tpr * (fpr - prev_fpr)
                prev_fpr = fpr
        return round(auc, 4)

    def _compute_sharpe(self, resolved: List[Dict]) -> float:
        if len(resolved) < 2:
            return 0.0
        returns = []
        for p in resolved:
            if p.get("outcome_status") == "correct":
                returns.append(p.get("confidence", 0.5))
            else:
                returns.append(-(1 - p.get("confidence", 0.5)))
        mean_ret = sum(returns) / len(returns)
        if mean_ret == 0:
            return 0.0
        variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
        if variance == 0:
            return 0.0
        return round(mean_ret / (variance ** 0.5), 4)

    async def save_prediction_record(
        self,
        event_id: str,
        event_title: str,
        trend: str,
        confidence: float,
        time_horizon: str = "Short-term (1-7 days)",
        probability_dist: Optional[Dict] = None,
    ) -> str:
        """Save a new prediction record for tracking."""
        from app.db.models import PredictionRecord
        from app.db.database import get_session_factory
        session_factory = get_session_factory()
        async with session_factory() as session:
            record = PredictionRecord(
                event_id=event_id,
                event_title=event_title,
                predicted_trend=trend,
                confidence=confidence,
                time_horizon=time_horizon,
                probability_dist=json.dumps(probability_dist) if probability_dist else None,
            )
            session.add(record)
            await session.commit()
            return record.prediction_id


# Global singleton
backtest_service = BacktestService()
