# 报告生成服务 - P1阶段核心功能
"""
报告生成服务 - 自动生成结构化分析报告

核心功能：
1. 多格式支持 - Markdown / PDF
2. 完整报告 - 摘要、分析详情、图表、建议
3. 自定义模板 - 支持不同报告类型
4. 批量生成 - 支持批量报告生成
"""
import os
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
from enum import Enum
from pydantic import BaseModel, Field

from app.services.llm_service import llm_service


class ReportType(str, Enum):
    """报告类型"""
    FULL = "full"           # 完整报告
    SUMMARY = "summary"     # 摘要报告
    EXECUTIVE = "executive" # 执行摘要
    TECHNICAL = "technical" # 技术报告


class ReportFormat(str, Enum):
    """报告格式"""
    MARKDOWN = "markdown"
    PDF = "pdf"
    HTML = "html"


class ReportRequest(BaseModel):
    """报告生成请求"""
    event_id: str
    event_title: str
    event_description: str
    event_category: str = "other"
    event_importance: int = 3
    report_type: ReportType = ReportType.FULL
    report_format: ReportFormat = ReportFormat.MARKDOWN
    include_sections: Optional[List[str]] = None  # 自定义章节
    analysis_result: Optional[Dict[str, Any]] = None
    sandbox_result: Optional[Dict[str, Any]] = None
    custom_sections: Optional[List[Dict[str, str]]] = None


class ReportSection(BaseModel):
    """报告章节"""
    title: str
    content: str
    order: int
    subsections: List["ReportSection"] = Field(default_factory=list)


class ReportMetadata(BaseModel):
    """报告元数据"""
    report_id: str
    report_type: ReportType
    report_format: ReportFormat
    event_id: str
    generated_at: str
    version: str = "1.0"
    author: str = "EventPredictor AI"


class GeneratedReport(BaseModel):
    """生成的报告"""
    metadata: ReportMetadata
    title: str
    summary: str
    sections: List[Dict[str, Any]]
    appendices: List[Dict[str, Any]] = Field(default_factory=list)
    raw_content: str = ""
    file_path: Optional[str] = None


class ReportService:
    """报告生成服务"""

    def __init__(self):
        self.llm = llm_service
        self.reports_dir = Path(os.getenv("REPORTS_DIR", "E:/EventPredictor/reports"))
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    async def generate_report(
        self,
        request: ReportRequest
    ) -> GeneratedReport:
        """
        生成分析报告

        Args:
            request: 报告生成请求

        Returns:
            生成的报告
        """
        report_id = f"rpt-{uuid.uuid4().hex[:8]}"

        # 生成报告内容
        summary = await self._generate_summary(request)
        sections = await self._generate_sections(request)

        # 构建完整报告
        metadata = ReportMetadata(
            report_id=report_id,
            report_type=request.report_type,
            report_format=request.report_format,
            event_id=request.event_id,
            generated_at=datetime.utcnow().isoformat()
        )

        # 生成原始内容
        raw_content = self._format_report(
            request.report_format,
            request.event_title,
            summary,
            sections,
            metadata
        )

        # 保存报告
        file_path = await self._save_report(
            report_id,
            raw_content,
            request.report_format
        )

        return GeneratedReport(
            metadata=metadata,
            title=f"事件分析报告：{request.event_title}",
            summary=summary,
            sections=sections,
            raw_content=raw_content,
            file_path=str(file_path) if file_path else None
        )

    async def _generate_summary(
        self,
        request: ReportRequest
    ) -> str:
        """生成报告摘要"""

        # 提取分析结果中的关键信息
        analysis_context = ""
        if request.analysis_result:
            synthesis = request.analysis_result.get("synthesis", {})
            cross_analysis = request.analysis_result.get("cross_analysis", {})

            analysis_context = f"""
已有分析摘要：
- 整体趋势: {synthesis.get('overall_trend', 'N/A')}
- 置信度: {synthesis.get('confidence', 0) * 100:.0f}%
- 共识点: {', '.join(cross_analysis.get('consensus', ['无'])[:3])}
"""

        sandbox_context = ""
        if request.sandbox_result:
            projections = request.sandbox_result.get("final_projections", {})
            sandbox_context = f"""
沙盘推演摘要：
- 最可能结果: {projections.get('most_likely_outcome', 'N/A')}
- 关键因素: {', '.join(projections.get('key_factors', [])[:3])}
"""

        prompt = f"""请为以下事件分析报告生成一段简洁的执行摘要（200-300字）：

事件标题：{request.event_title}
事件描述：{request.event_description}
事件类别：{request.event_category}
严重程度：{request.event_importance}/5

{analysis_context}
{sandbox_context}

摘要应包含：
1. 事件概述
2. 核心发现
3. 主要建议
4. 风险提示

请直接输出摘要内容，不要包含标题或额外格式。"""

        try:
            return await self.llm.generate(prompt)
        except Exception as e:
            print(f"Summary generation failed: {e}")
            return f"本报告分析了{request.event_title}事件的发展态势。" \
                   f"事件类别为{request.event_category}，严重程度为{request.event_importance}/5级。" \
                   f"建议持续关注事态发展。"

    async def _generate_sections(
        self,
        request: ReportRequest
    ) -> List[Dict[str, Any]]:
        """生成报告章节"""

        # 确定要包含的章节
        if request.include_sections:
            section_names = request.include_sections
        else:
            section_names = self._get_default_sections(request.report_type)

        sections = []

        for i, section_name in enumerate(section_names):
            section = await self._generate_single_section(
                section_name,
                request,
                order=i + 1
            )
            sections.append(section)

        # 添加自定义章节
        if request.custom_sections:
            for i, custom in enumerate(request.custom_sections):
                sections.append({
                    "title": custom.get("title", f"自定义章节{i+1}"),
                    "content": custom.get("content", ""),
                    "order": len(sections) + i + 1,
                    "subsections": []
                })

        return sections

    def _get_default_sections(self, report_type: ReportType) -> List[str]:
        """获取默认章节列表"""
        sections_map = {
            ReportType.FULL: [
                "事件概述",
                "背景分析",
                "多视角分析",
                "情景推演",
                "风险评估",
                "建议与对策",
                "结论"
            ],
            ReportType.SUMMARY: [
                "事件概述",
                "核心发现",
                "建议"
            ],
            ReportType.EXECUTIVE: [
                "执行摘要",
                "关键发现",
                "战略建议"
            ],
            ReportType.TECHNICAL: [
                "事件详情",
                "分析方法",
                "数据来源",
                "详细分析",
                "技术结论"
            ]
        }
        return sections_map.get(report_type, sections_map[ReportType.FULL])

    async def _generate_single_section(
        self,
        section_name: str,
        request: ReportRequest,
        order: int
    ) -> Dict[str, Any]:
        """生成单个章节"""

        # 准备上下文
        context = self._prepare_section_context(section_name, request)

        prompt = f"""请为事件分析报告撰写"{section_name}"章节：

事件标题：{request.event_title}
事件描述：{request.event_description}
事件类别：{request.event_category}
严重程度：{request.event_importance}/5

{context}

要求：
1. 内容客观、专业
2. 字数300-500字
3. 结构清晰，可使用小标题
4. 避免重复摘要内容

请直接输出章节内容。"""

        try:
            content = await self.llm.generate(prompt)
        except Exception as e:
            print(f"Section generation failed for {section_name}: {e}")
            content = f"【{section_name}内容待补充】"

        return {
            "title": section_name,
            "content": content,
            "order": order,
            "subsections": []
        }

    def _prepare_section_context(
        self,
        section_name: str,
        request: ReportRequest
    ) -> str:
        """为章节准备上下文信息"""

        context = ""

        # 根据章节类型添加相关上下文
        if "多视角" in section_name or "视角" in section_name:
            if request.analysis_result:
                roles = request.analysis_result.get("role_analyses", [])
                role_summaries = [
                    f"- {r.get('role_name')}: {r.get('stance', '')[:50]}..."
                    for r in roles[:5]
                ]
                context = f"已有角色分析：\n{chr(10).join(role_summaries)}"

        elif "情景" in section_name or "推演" in section_name:
            if request.sandbox_result:
                branches = request.sandbox_result.get("branches", [])
                branch_info = [
                    f"- {b.get('name')}: 概率{b.get('probability', 0)*100:.0f}%"
                    for b in branches
                ]
                context = f"推演分支：\n{chr(10).join(branch_info)}"

        elif "风险" in section_name:
            if request.analysis_result:
                conflicts = request.analysis_result.get("cross_analysis", {}).get("conflicts", [])
                context = f"已识别冲突：{len(conflicts)}个"

        elif "建议" in section_name or "对策" in section_name:
            if request.analysis_result:
                recs = request.analysis_result.get("synthesis", {}).get("recommended_actions", [])
                context = f"已有建议：{', '.join(recs[:3])}"

        return context

    def _format_report(
        self,
        format_type: ReportFormat,
        title: str,
        summary: str,
        sections: List[Dict[str, Any]],
        metadata: ReportMetadata
    ) -> str:
        """格式化报告"""

        if format_type == ReportFormat.MARKDOWN:
            return self._format_markdown(title, summary, sections, metadata)
        elif format_type == ReportFormat.HTML:
            return self._format_html(title, summary, sections, metadata)
        else:
            # 默认Markdown
            return self._format_markdown(title, summary, sections, metadata)

    def _format_markdown(
        self,
        title: str,
        summary: str,
        sections: List[Dict[str, Any]],
        metadata: ReportMetadata
    ) -> str:
        """生成Markdown格式报告"""

        lines = [
            f"# {title}",
            "",
            f"> 生成时间: {metadata.generated_at}",
            f"> 报告ID: {metadata.report_id}",
            f"> 报告类型: {metadata.report_type.value}",
            "",
            "---",
            "",
            "## 摘要",
            "",
            summary,
            "",
            "---",
            ""
        ]

        # 添加章节
        for section in sorted(sections, key=lambda x: x.get("order", 0)):
            lines.extend([
                f"## {section['title']}",
                "",
                section["content"],
                ""
            ])

            # 添加子章节
            for subsection in section.get("subsections", []):
                lines.extend([
                    f"### {subsection['title']}",
                    "",
                    subsection["content"],
                    ""
                ])

        # 添加页脚
        lines.extend([
            "---",
            "",
            "*本报告由 EventPredictor AI 自动生成*",
            f"*报告版本: {metadata.version}*"
        ])

        return "\n".join(lines)

    def _format_html(
        self,
        title: str,
        summary: str,
        sections: List[Dict[str, Any]],
        metadata: ReportMetadata
    ) -> str:
        """生成HTML格式报告"""

        html_sections = ""
        for section in sorted(sections, key=lambda x: x.get("order", 0)):
            html_sections += f"""
    <section>
        <h2>{section['title']}</h2>
        <div class="content">
            {self._markdown_to_html(section['content'])}
        </div>
    </section>
"""

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        .metadata {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }}
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
        }}
        section {{ margin: 30px 0; }}
        .footer {{ margin-top: 50px; color: #95a5a6; font-size: 0.8em; text-align: center; }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <div class="metadata">
            生成时间: {metadata.generated_at}<br>
            报告ID: {metadata.report_id}
        </div>
    </header>

    <div class="summary">
        <h2>摘要</h2>
        {self._markdown_to_html(summary)}
    </div>

    {html_sections}

    <footer class="footer">
        <p>本报告由 EventPredictor AI 自动生成</p>
        <p>报告版本: {metadata.version}</p>
    </footer>
</body>
</html>"""

    def _markdown_to_html(self, markdown_text: str) -> str:
        """简单的Markdown到HTML转换"""
        html = markdown_text

        # 段落
        html = html.replace("\n\n", "</p><p>")
        html = f"<p>{html}</p>"

        # 粗体
        import re
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)

        # 斜体
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

        # 列表
        html = re.sub(r'- (.+)', r'<li>\1</li>', html)

        return html

    async def _save_report(
        self,
        report_id: str,
        content: str,
        format_type: ReportFormat
    ) -> Optional[Path]:
        """保存报告到文件"""

        ext_map = {
            ReportFormat.MARKDOWN: ".md",
            ReportFormat.HTML: ".html",
            ReportFormat.PDF: ".pdf"
        }

        ext = ext_map.get(format_type, ".md")
        filename = f"{report_id}{ext}"
        file_path = self.reports_dir / filename

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return file_path
        except Exception as e:
            print(f"Report save failed: {e}")
            return None

    async def generate_quick_report(
        self,
        event: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> str:
        """
        快速生成简要报告（用于API响应）

        Args:
            event: 事件信息
            analysis_result: 分析结果

        Returns:
            Markdown格式的简要报告
        """
        title = event.get("title", "未知事件")
        synthesis = analysis_result.get("synthesis", {})
        cross_analysis = analysis_result.get("cross_analysis", {})

        # 提取角色分析
        roles = analysis_result.get("role_analyses", [])
        role_lines = []
        for r in roles[:5]:
            role_lines.append(f"- **{r.get('role_name', 'Unknown')}**: {r.get('stance', '')[:80]}")

        # 提取共识
        consensus = cross_analysis.get("consensus", [])

        # 提取建议
        recommendations = synthesis.get("recommended_actions", [])

        report = f"""# {title} - 快速分析报告

## 核心发现

- **整体趋势**: {synthesis.get('overall_trend', 'N/A')}
- **置信度**: {synthesis.get('confidence', 0) * 100:.0f}%

## 多方视角

{chr(10).join(role_lines) if role_lines else '- 暂无角色分析'}

## 关键共识

{chr(10).join([f'- {c}' for c in consensus[:3]]) if consensus else '- 暂无共识'}

## 建议

{chr(10).join([f'{i+1}. {r}' for i, r in enumerate(recommendations[:3])]) if recommendations else '- 持续关注'}

---
*生成时间: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*
"""
        return report

    async def list_reports(
        self,
        limit: int = 20,
        report_type: Optional[ReportType] = None
    ) -> List[Dict[str, Any]]:
        """
        列出已生成的报告

        Args:
            limit: 返回数量限制
            report_type: 过滤报告类型

        Returns:
            报告列表
        """
        reports = []

        try:
            for file_path in self.reports_dir.glob("rpt-*.md"):
                stat = file_path.stat()
                reports.append({
                    "report_id": file_path.stem,
                    "file_name": file_path.name,
                    "file_path": str(file_path),
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
        except Exception:
            pass

        # 按创建时间倒序排序
        reports.sort(key=lambda x: x["created_at"], reverse=True)

        return reports[:limit]

    async def get_report_content(self, report_id: str) -> Optional[str]:
        """
        获取报告内容

        Args:
            report_id: 报告ID

        Returns:
            报告内容
        """
        # 尝试不同格式
        for ext in [".md", ".html"]:
            file_path = self.reports_dir / f"{report_id}{ext}"
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception:
                    pass

        return None


# 全局服务实例
report_service = ReportService()
