# 校准接口
from fastapi import APIRouter, HTTPException, status, Query
from app.services.calibration_service import calibration_service

router = APIRouter(prefix="/api/v1", tags=["Calibration"])


@router.get(
    "/calibration/status",
    summary="Get calibration status",
    description="Get current calibration metrics including Brier score, directional accuracy, and rating.",
)
async def get_calibration_status():
    """Get calibration status."""
    try:
        return await calibration_service.get_calibration_status()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/calibration/curve",
    summary="Get calibration curve",
    description="Get calibration curve data for plotting.",
)
async def get_calibration_curve(n_bins: int = Query(default=10, ge=2, le=20)):
    """Get calibration curve."""
    try:
        return await calibration_service.get_calibration_curve(n_bins=n_bins)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
