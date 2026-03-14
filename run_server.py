# 测试服务器启动脚本
import os
import sys

# 在所有导入之前设置NO_PROXY
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
os.environ["no_proxy"] = "localhost,127.0.0.1"
# 清除可能的代理设置
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8005)
