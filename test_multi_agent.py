# 测试多Agent角色分析功能
import asyncio
import sys
sys.path.insert(0, r'E:\EventPredictor')

from app.services.multi_agent_service import multi_agent_service
from app.agents.roles import get_role, get_all_role_ids


async def test_multi_agent():
    """测试多Agent角色分析"""
    
    # 测试事件数据
    event = {
        "id": "test-001",
        "title": "美国宣布对华新关税政策",
        "description": "美国贸易代表办公室宣布将对价值2000亿美元的中国商品加征25%关税，涉及科技、制造等多个领域",
        "category": "Geopolitical",
        "importance": 5,
        "timestamp": "2026-03-12T10:00:00Z"
    }
    
    # 选择要分析的角色
    role_ids = ["cn_gov", "us_gov", "tech_giant", "common_public", "mainstream_media"]
    
    print(f"Testing with {len(role_ids)} roles:")
    for rid in role_ids:
        role = get_role(rid)
        print(f"  - {role.name} ({role.category})")
    print()
    
    # 执行分析
    result = await multi_agent_service.analyze_with_roles(
        event=event,
        role_ids=role_ids,
        depth="standard"
    )
    
    # 打印结果
    print("=" * 60)
    print("分析结果")
    print("=" * 60)
    
    print("\n【各角色分析】")
    for analysis in result.get("role_analyses", []):
        print(f"\n{analysis.role_name} ({analysis.category}):")
        print(f"  立场: {analysis.stance}")
        print(f"  反应: {analysis.reaction}")
    
    print("\n【交叉分析】")
    cross = result.get("cross_analysis", {})
    print(f"  冲突点: {cross.get('conflicts', [])}")
    print(f"  协同点: {cross.get('synergies', [])}")
    print(f"  共识: {cross.get('consensus', [])}")
    
    print("\n【综合推演】")
    synthesis = result.get("synthesis", {})
    print(f"  整体趋势: {synthesis.get('overall_trend')}")
    print(f"  置信度: {synthesis.get('confidence')}")
    print(f"  摘要: {synthesis.get('summary', '')[:200]}...")
    
    print("\n测试完成!")


if __name__ == "__main__":
    asyncio.run(test_multi_agent())
