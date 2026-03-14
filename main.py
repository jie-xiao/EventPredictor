#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EventPredictor - 全球局势推演决策系统

运行方式:
    python main.py              # 直接运行
    uvicorn app.main:app        # 使用uvicorn
    python main.py --reload     # 开发模式
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn
from app.core.config import config


def main():
    """主入口"""
    print("=" * 50)
    print("  EventPredictor - 全球局势推演决策系统")
    print(f"  Version: {config.api.version}")
    print("=" * 50)
    print(f"LLM Provider: {config.llm.provider}")
    print(f"Model: {config.llm.model}")
    print(f"API: http://{config.api.host}:{config.api.port}")
    print("Docs: http://{host}:{port}/docs".format(
        host=config.api.host, 
        port=config.api.port
    ))
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.debug,
        log_level="info"
    )


if __name__ == "__main__":
    main()
