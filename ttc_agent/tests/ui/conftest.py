"""
pytest配置文件，用于UI测试
"""
import os
import pytest
from typing import Any, Generator
from playwright.sync_api import Page, Browser, BrowserContext
from ttc_agent.tests.ui.test_conversation import ConversationPage

# 这个文件的存在使pytest能够正确识别测试目录结构
# 同时，我们可以在这里添加全局夹具和配置

def pytest_configure(config: Any) -> None:
    """配置pytest"""
    # 添加标记
    config.addinivalue_line("markers", "ui: 标记UI测试")
    
    # 可以在这里添加其他配置

@pytest.fixture
def conversation_page(page: Page) -> Generator[ConversationPage, None, None]:
    """创建一个ConversationPage实例用于测试"""
    # 设置基础URL
    base_url = "http://localhost:5173"
    
    # 访问应用
    page.goto(base_url)
    
    # 等待页面加载完成
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("networkidle")
    
    # 创建ConversationPage实例
    conversation_page = ConversationPage(page)
    
    # 返回实例
    yield conversation_page
