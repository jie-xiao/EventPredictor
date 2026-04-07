# P2.2 高级分析引擎 API 路由
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth_deps import get_optional_user
from app.services.advanced_analysis.models import (
    AdvancedAnalysisRequest,
    AnalysisMethodInfo,
    AnalysisMethodsResponse,
    BayesianResponse,
    BayesianResult,
    CausalResponse,
    CausalResult,
    EnsembleResponse,
    EnsembleResult,
    MonteCarloResponse,
    MonteCarloResult,
)
from app.services.advanced_analysis.monte_carlo_service import monte_carlo_service
from app.services.advanced_analysis.bayesian_service import bayesian_service
from app.services.advanced_analysis.causal_service import causal_service
from app.services.advanced_analysis.ensemble_service import ensemble_service

router = APIRouter(prefix="/api/v1/analysis/advanced", tags=["Advanced Analysis"])


@router.post(
    "/monte-carlo",
    response_model=MonteCarloResponse,
    summary="蒙特卡洛模拟",
    description="对事件进行蒙特卡洛模拟分析",
)
async def monte_carlo_analysis(
    request: AdvancedAnalysisRequest,
    n_simulations: int = 1000,
    user=Depends(get_optional_user),
):
    """蒙特卡洛模拟分析"""
    try:
        result = await monte_carlo_service.simulate(request, n_simulations)
        return MonteCarloResponse(
            event_title=request.title,
            result=result,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monte Carlo analysis failed: {str(e)}")


@router.post(
    "/bayesian",
    response_model=BayesianResponse,
    summary="贝叶斯网络推理",
    description="对事件进行贝叶斯网络推理分析",
)
async def bayesian_analysis(
    request: AdvancedAnalysisRequest,
    user=Depends(get_optional_user),
):
    """贝叶斯网络推理"""
    try:
        result = await bayesian_service.analyze(request)
        return BayesianResponse(
            event_title=request.title,
            result=result,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bayesian analysis failed: {str(e)}")


@router.post(
    "/causal",
    response_model=CausalResponse,
    summary="因果推理分析",
    description="对事件进行因果推理分析",
)
async def causal_analysis(
    request: AdvancedAnalysisRequest,
    user=Depends(get_optional_user),
):
    """因果推理分析"""
    try:
        result = await causal_service.analyze(request)
        return CausalResponse(
            event_title=request.title,
            result=result,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Causal analysis failed: {str(e)}")


@router.post(
    "/ensemble",
    response_model=EnsembleResponse,
    summary="集成预测",
    description="并行运行多种分析方法并综合预测",
)
async def ensemble_analysis(
    request: AdvancedAnalysisRequest,
    user=Depends(get_optional_user),
):
    """集成预测分析"""
    try:
        result = await ensemble_service.predict(request)
        return EnsembleResponse(
            event_title=request.title,
            result=result,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ensemble analysis failed: {str(e)}")


@router.get(
    "/methods",
    response_model=AnalysisMethodsResponse,
    summary="分析方法列表",
    description="获取可用的高级分析方法列表",
)
async def get_analysis_methods():
    """获取分析方法列表"""
    methods = [
        AnalysisMethodInfo(
            id="monte_carlo",
            name="蒙特卡洛模拟",
            description="通过随机模拟评估事件结果的概率分布和置信区间",
            endpoint="/api/v1/analysis/advanced/monte-carlo",
        ),
        AnalysisMethodInfo(
            id="bayesian",
            name="贝叶斯网络推理",
            description="构建贝叶斯网络进行概率推理和证据更新",
            endpoint="/api/v1/analysis/advanced/bayesian",
        ),
        AnalysisMethodInfo(
            id="causal",
            name="因果推理分析",
            description="提取因果图并分析直接效应、间接效应和混杂因素",
            endpoint="/api/v1/analysis/advanced/causal",
        ),
        AnalysisMethodInfo(
            id="ensemble",
            name="集成预测",
            description="综合多种方法的预测结果，加权投票得出最终预测",
            endpoint="/api/v1/analysis/advanced/ensemble",
        ),
    ]
    return AnalysisMethodsResponse(methods=methods)
