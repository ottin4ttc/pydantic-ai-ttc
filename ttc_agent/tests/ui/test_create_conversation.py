import pytest
import time
import traceback
from playwright.sync_api import Page
from ttc_agent.tests.ui.test_utils import create_test_run_dir, setup_logger, UITestResult, ReportGenerator
from ttc_agent.tests.ui.test_conversation import ConversationPage

# 全局变量
RUN_DIR = create_test_run_dir()
LOGGER = setup_logger(RUN_DIR)
REPORT_GENERATOR = ReportGenerator(RUN_DIR)

def test_create_conversation(conversation_page: ConversationPage):
    """
    Test creating conversations with different bot types.
    
    Steps:
    1. Create a conversation with customer service bot
    2. Create a conversation with technical support bot
    3. Verify both conversations exist
    """
    test_result = UITestResult("test_create_conversation", RUN_DIR)
    
    try:
        LOGGER.info("Starting test_create_conversation")
        
        # 截图以便调试
        test_result.add_screenshot("test-start", conversation_page.page)
        
        # Create first conversation with customer service bot
        LOGGER.info("Step 1: Creating customer service bot conversation")
        test_result.add_step("Creating customer service bot conversation")
        cs_conv_id = conversation_page.create_new_conversation("customer_service")
        LOGGER.info(f"Customer service conversation ID: {cs_conv_id}")
        
        # Verify the conversation exists
        LOGGER.info("Step 2: Verifying customer service conversation exists")
        test_result.add_step("Verifying customer service conversation exists")
        current_id = conversation_page.get_current_conversation_id()
        assert current_id == cs_conv_id, f"Expected current conversation to be {cs_conv_id}, got {current_id}"
        
        # 截图以便调试
        test_result.add_screenshot("final-state", conversation_page.page)
        
        LOGGER.info("Test completed successfully!")
        test_result.mark_passed()
        
    except Exception as e:
        error_msg = f"Test failed: {str(e)}"
        LOGGER.error(error_msg)
        LOGGER.error(traceback.format_exc())
        test_result.mark_failed(error_msg)
        test_result.add_screenshot("failure", conversation_page.page)
        raise
    
    finally:
        # 添加测试结果到报告生成器
        REPORT_GENERATOR.add_result(test_result)
        
        # 生成报告
        json_report = REPORT_GENERATOR.generate_json_report()
        html_report = REPORT_GENERATOR.generate_html_report()
        
        LOGGER.info(f"Test report generated: {json_report}")
        LOGGER.info(f"HTML report generated: {html_report}")
