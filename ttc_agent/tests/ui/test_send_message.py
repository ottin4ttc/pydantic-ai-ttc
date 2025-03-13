import pytest
import time
import traceback
from playwright.sync_api import Page
from ttc_agent.tests.ui.test_utils import UITestResult
from ttc_agent.tests.ui.test_conversation import ConversationPage
from ttc_agent.tests.ui.conftest import RUN_DIR, LOGGER, REPORT_GENERATOR

def test_send_message(conversation_page: ConversationPage):
    """
    Test sending a message and receiving a response.
    
    Steps:
    1. Create a conversation
    2. Send a message
    3. Wait for and verify the response
    """
    test_result = UITestResult("test_send_message", RUN_DIR)
    
    try:
        LOGGER.info("Starting test_send_message")
        
        # 截图以便调试
        test_result.add_screenshot("test-start", conversation_page.page)
        LOGGER.debug("Took initial screenshot")
        
        # Create conversation
        LOGGER.info("Step 1: Creating conversation")
        test_result.add_step("Creating conversation")
        conv_id = conversation_page.create_new_conversation()
        LOGGER.info(f"Conversation ID: {conv_id}")
        
        # Send message
        LOGGER.info("Step 2: Sending message")
        test_result.add_step("Sending message")
        conversation_page.send_message("Hello, this is a test message")
        
        # Wait for response
        LOGGER.info("Step 3: Waiting for response")
        test_result.add_step("Waiting for response")
        conversation_page.wait_for_response()
        
        # Verify response
        response = conversation_page.get_last_message()
        LOGGER.info(f"Response received: {response[:50]}...")  # 只记录前50个字符
        assert response, "Response should not be empty"
        
        # 截图以便调试
        test_result.add_screenshot("after-response", conversation_page.page)
        
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
