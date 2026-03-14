# 快速验证脚本
import sys
sys.path.insert(0, r'E:\EventPredictor')

print("=== EventPredictor v2 功能验证 ===\n")

# 1. 验证角色系统
print("1. 验证角色系统...")
from app.agents.roles import ROLES, get_all_role_ids, get_role
role_count = len(ROLES)
print(f"   已加载 {role_count} 个角色定义")
print(f"   角色ID: {get_all_role_ids()[:5]}...")

# 2. 验证多Agent服务
print("\n2. 验证多Agent服务...")
from app.services.multi_agent_service import multi_agent_service
print("   MultiAgentAnalysisService 已加载")

# 3. 验证API路由
print("\n3. 验证API路由...")
from app.main import app
routes = [r.path for r in app.routes if hasattr(r, 'path')]
analysis_routes = [r for r in routes if 'analysis' in r]
print(f"   发现 {len(analysis_routes)} 个分析相关路由:")
for r in analysis_routes:
    print(f"     - {r}")

# 4. 测试角色详情
print("\n4. 验证角色详情...")
cn_gov = get_role('cn_gov')
print(f"   角色: {cn_gov.name}")
print(f"   类别: {cn_gov.category}")
print(f"   立场: {cn_gov.stance}")
print(f"   关注点: {cn_gov.focus_points[:3]}...")

print("\n=== 所有核心功能验证通过 ===")
