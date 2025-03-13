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

def test_conversation_switching(conversation_page: ConversationPage):
    """
    Test switching between conversations.
    
    Steps:
    1. Create first conversation and send a message
    2. Create second conversation and send a message
    3. Switch back to first conversation
    4. Verify the correct conversation is active
    """
    test_result = UITestResult("test_conversation_switching", RUN_DIR)
    
    try:
        LOGGER.info("Starting test_conversation_switching")
        
        # 截图以便调试
        test_result.add_screenshot("test-start", conversation_page.page)
        
        # First conversation
        LOGGER.info("Step 1: Creating first conversation")
        test_result.add_step("Creating first conversation")
        conv1_id = conversation_page.create_new_conversation()
        LOGGER.info(f"First conversation ID: {conv1_id}")
        
        LOGGER.info("Step 2: Sending message in first conversation")
        test_result.add_step("Sending message in first conversation")
        conversation_page.send_message("Message in first conversation")
        conversation_page.wait_for_response()
        
        # Second conversation
        LOGGER.info("Step 3: Creating second conversation")
        test_result.add_step("Creating second conversation")
        conv2_id = conversation_page.create_new_conversation()
        LOGGER.info(f"Second conversation ID: {conv2_id}")
        
        LOGGER.info("Step 4: Sending message in second conversation")
        test_result.add_step("Sending message in second conversation")
        conversation_page.send_message("Message in second conversation")
        conversation_page.wait_for_response()
        
        # Switch back to first conversation
        LOGGER.info(f"Step 5: Switching back to first conversation: {conv1_id}")
        test_result.add_step(f"Switching back to first conversation: {conv1_id}")
        conversation_page.switch_to_conversation(conv1_id)
        
        # Verify correct conversation is active
        current_id = conversation_page.get_current_conversation_id()
        assert current_id == conv1_id, f"Expected current conversation to be {conv1_id}, got {current_id}"
        
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
