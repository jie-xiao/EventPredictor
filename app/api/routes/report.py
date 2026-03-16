# 报告生成 API 路由 - P1阶段
"""
报告生成API接口

Endpoints:
- POST /api/v1/report/generate - 生成完整报告
- POST /api/v1/report/quick - 快速生成简要报告
- GET /api/v1/report/list - 列出已生成报告
- GET /api/v1/report/{report_id} - 获取报告内容
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

from app.services.report_service import (
    report_service,
    ReportRequest,
    ReportType,
    ReportFormat,
    GeneratedReport
)

router = APIRouter(prefix="/api/v1/report", tags=["Report Generation"])


class GenerateReportRequest(BaseModel):
    """生成报告请求"""
    event_id: str = Field(..., description="事件ID")
    event_title: str = Field(..., description="事件标题")
    event_description: str = Field(..., description="事件描述")
    event_category: str = Field(default="other", description="事件类别")
    event_importance: int = Field(default=3, ge=1, le=5, description="事件严重程度")
    report_type: str = Field(default="full", description="报告类型: full/summary/executive/technical")
    report_format: str = Field(default="markdown", description="报告格式: markdown/html")
    include_sections: Optional[List[str]] = Field(default=None, description="自定义包含的章节")
    analysis_result: Optional[Dict[str, Any]] = Field(default=None, description="多Agent分析结果")
    sandbox_result: Optional[Dict[str, Any]] = Field(default=None, description="沙盘推演结果")
    custom_sections: Optional[List[Dict[str, str]]] = Field(default=None, description="自定义章节")


class QuickReportRequest(BaseModel):
    """快速报告请求"""
    event: Dict[str, Any] = Field(..., description="事件信息")
    analysis_result: Dict[str, Any] = Field(..., description="分析结果")


class ReportResponse(BaseModel):
    """报告响应"""
    success: bool
    report_id: str
    title: str
    summary: str
    sections_count: int
    file_path: Optional[str] = None


@router.post("/generate", response_model=ReportResponse)
async def generate_report(request: GenerateReportRequest):
    """
    生成完整分析报告

    根据事件信息和分析结果，自动生成结构化的分析报告。

    - **event_id**: 事件唯一标识
    - **event_title**: 事件标题
    - **event_description**: 事件详细描述
    - **report_type**: 报告类型（full/summary/executive/technical）
    - **report_format**: 报告格式（markdown/html）
    - **analysis_result**: 多Agent分析结果（可选）
    - **sandbox_result**: 沙盘推演结果（可选）
    """
    try:
        # 解析报告类型
        try:
            report_type = ReportType(request.report_type)
        except ValueError:
            report_type = ReportType.FULL

        # 解析报告格式
        try:
            report_format = ReportFormat(request.report_format)
        except ValueError:
            report_format = ReportFormat.MARKDOWN

        # 构建请求
        report_request = ReportRequest(
            event_id=request.event_id,
            event_title=request.event_title,
            event_description=request.event_description,
            event_category=request.event_category,
            event_importance=request.event_importance,
            report_type=report_type,
            report_format=report_format,
            include_sections=request.include_sections,
            analysis_result=request.analysis_result,
            sandbox_result=request.sandbox_result,
            custom_sections=request.custom_sections
        )

        # 生成报告
        result = await report_service.generate_report(report_request)

        return ReportResponse(
            success=True,
            report_id=result.metadata.report_id,
            title=result.title,
            summary=result.summary[:200] + "..." if len(result.summary) > 200 else result.summary,
            sections_count=len(result.sections),
            file_path=result.file_path
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick")
async def generate_quick_report(request: QuickReportRequest):
    """
    快速生成简要报告

    快速生成Markdown格式的简要分析报告，适合API直接返回。

    - **event**: 事件信息字典
    - **analysis_result**: 多Agent分析结果
    """
    try:
        report_content = await report_service.generate_quick_report(
            event=request.event,
            analysis_result=request.analysis_result
        )

        return {
            "success": True,
            "content": report_content,
            "format": "markdown"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_reports(
    limit: int = 20,
    report_type: Optional[str] = None
):
    """
    列出已生成的报告

    - **limit**: 返回数量限制
    - **report_type**: 过滤报告类型（可选）
    """
    try:
        # 解析报告类型
        rpt_type = None
        if report_type:
            try:
                rpt_type = ReportType(report_type)
            except ValueError:
                pass

        reports = await report_service.list_reports(
            limit=limit,
            report_type=rpt_type
        )

        return {
            "success": True,
            "count": len(reports),
            "reports": reports
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}")
async def get_report(report_id: str, format: str = "raw"):
    """
    获取报告内容

    - **report_id**: 报告ID
    - **format**: 返回格式（raw/html）
    """
    try:
        content = await report_service.get_report_content(report_id)

        if content is None:
            raise HTTPException(status_code=404, detail="Report not found")

        if format == "html" and content.startswith("<!DOCTYPE"):
            return HTMLResponse(content=content)
        else:
            return PlainTextResponse(content=content)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{report_id}/metadata")
async def get_report_metadata(report_id: str):
    """
    获取报告元数据

    - **report_id**: 报告ID
    """
    try:
        content = await report_service.get_report_content(report_id)

        if content is None:
            raise HTTPException(status_code=404, detail="Report not found")

        # 从文件路径获取信息
        import os
        from pathlib import Path
        from datetime import datetime

        reports_dir = Path(os.getenv("REPORTS_DIR", "E:/EventPredictor/reports"))
        for ext in [".md", ".html"]:
            file_path = reports_dir / f"{report_id}{ext}"
            if file_path.exists():
                stat = file_path.stat()
                return {
                    "success": True,
                    "report_id": report_id,
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "size_bytes": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                }

        raise HTTPException(status_code=404, detail="Report not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """报告服务健康检查"""
    return {
        "status": "healthy",
        "service": "report_service",
        "features": [
            "multi_format_support",
            "auto_section_generation",
            "quick_report",
            "report_persistence"
        ],
        "supported_formats": ["markdown", "html"],
        "report_types": ["full", "summary", "executive", "technical"]
    }
