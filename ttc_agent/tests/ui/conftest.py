import pytest
import time
import os
from typing import Dict, Any, List
from playwright.sync_api import Page, Browser, BrowserContext, sync_playwright
from ttc_agent.tests.ui.test_utils import create_test_run_dir, setup_logger, UITestResult, ReportGenerator
from ttc_agent.tests.ui.port_utils import get_frontend_port, get_ports_to_try

# 全局变量，在所有测试之间共享
RUN_DIR = create_test_run_dir()
LOGGER = setup_logger(RUN_DIR)
REPORT_GENERATOR = ReportGenerator(RUN_DIR)

@pytest.fixture(scope="session")
def browser():
    """创建浏览器实例，在整个测试会话中共享"""
    LOGGER.info("Starting browser")
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=True)
    yield browser
    LOGGER.info("Closing browser")
    browser.close()
    playwright.stop()

@pytest.fixture
def context(browser: Browser):
    """创建浏览器上下文，每个测试用例一个"""
    LOGGER.info("Creating browser context")
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    yield context
    LOGGER.info("Closing browser context")
    context.close()

@pytest.fixture
def page(context: BrowserContext):
    """创建页面，每个测试用例一个"""
    LOGGER.info("Creating page")
    page = context.new_page()
    yield page
    LOGGER.info("Closing page")
    page.close()

@pytest.fixture
def conversation_page(page: Page):
    """创建ConversationPage实例，每个测试用例一个"""
    from ttc_agent.tests.ui.test_conversation import ConversationPage
    LOGGER.info("Creating ConversationPage")
    conversation_page = ConversationPage(page)
    
    # 记录当前使用的前端端口
    frontend_port = get_frontend_port()
    if frontend_port:
        LOGGER.info(f"Using frontend port from environment: {frontend_port}")
    else:
        LOGGER.info(f"No frontend port specified in environment, will try default ports")
    
    # 导航到主页
    try:
        LOGGER.info("Navigating to home page")
        conversation_page.navigate_to_home()
    except Exception as e:
        LOGGER.error(f"Failed to navigate to home page: {str(e)}")
        # 捕获当前页面截图以便调试
        screenshot_path = f"{RUN_DIR}/screenshots/navigation-error.png"
        LOGGER.debug(f"Taking error screenshot: {screenshot_path}")
        page.screenshot(path=screenshot_path)
        raise
    
    yield conversation_page

# 在所有测试完成后生成报告
@pytest.fixture(scope="session", autouse=True)
def generate_report():
    """在所有测试完成后生成报告"""
    yield
    LOGGER.info("Generating test report")
    json_report = REPORT_GENERATOR.generate_json_report()
    html_report = REPORT_GENERATOR.generate_html_report()
    LOGGER.info(f"JSON report generated: {json_report}")
    LOGGER.info(f"HTML report generated: {html_report}")
