"""
pytest配置文件，用于UI测试
"""
from typing import Any

# 这个文件的存在使pytest能够正确识别测试目录结构
# 同时，我们可以在这里添加全局夹具和配置

def pytest_configure(config: Any) -> None:
    """配置pytest"""
    # 添加标记
    config.addinivalue_line("markers", "ui: 标记UI测试")
    
    # 可以在这里添加其他配置 