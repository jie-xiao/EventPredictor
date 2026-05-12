# 回测接口
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.services.backtest_service import backtest_service

router = APIRouter(prefix="/api/v1", tags=["Backtest"])


class BacktestRequest(BaseModel):
    historical_data_path: Optional[str] = None


@router.post(
    "/backtest/run",
    summary="Run backtest",
    description="Run a backtest on resolved predictions to compute Brier score, directional accuracy, and calibration curve.",
)
async def run_backtest(request: BacktestRequest):
    """Trigger a backtest run."""
    try:
        from app.db.database import get_session_factory
        from app.db.models import PredictionRecord
        from sqlalchemy import select

        session_factory = get_session_factory()
        async with session_factory() as session:
            result = await session.execute(select(PredictionRecord))
            records = result.scalars().all()

        predictions = [
            {
                "prediction_id": r.prediction_id,
                "event_id": r.event_id,
                "event_title": r.event_title,
                "predicted_trend": r.predicted_trend,
                "confidence": r.confidence,
                "outcome_status": r.outcome_status,
                "predicted_at": r.predicted_at,
                "resolved_at": r.resolved_at,
            }
            for r in records
        ]

        result = await backtest_service.run_backtest(predictions)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/backtest/history",
    summary="List backtest runs",
    description="Get history of backtest runs.",
)
async def list_backtest_runs():
    """List all backtest runs."""
    try:
        from app.db.database import get_session_factory
        from app.db.models import BacktestRun
        from sqlalchemy import select

        session_factory = get_session_factory()
        async with session_factory() as session:
            result = await session.execute(
                select(BacktestRun).order_by(BacktestRun.run_at.desc()).limit(20)
            )
            runs = result.scalars().all()

        return [
            {
                "id": r.id,
                "run_at": r.run_at,
                "event_count": r.event_count,
                "resolved_count": r.resolved_count,
                "brier_score": r.brier_score,
                "directional_accuracy": r.directional_accuracy,
                "duration_ms": r.duration_ms,
            }
            for r in runs
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
