import pytest
import traceback
from ttc_agent.tests.ui.conftest import RUN_DIR, LOGGER, REPORT_GENERATOR
from ttc_agent.tests.ui.test_utils import UITestResult
from ttc_agent.tests.ui.test_conversation import ConversationPage

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
        
        # Create second conversation with technical support bot
        LOGGER.info("Step 2: Creating technical support bot conversation")
        test_result.add_step("Creating technical support bot conversation")
        ts_conv_id = conversation_page.create_new_conversation("technical_support")
        LOGGER.info(f"Technical support conversation ID: {ts_conv_id}")
        
        # Verify both conversations exist
        LOGGER.info("Step 3: Verifying both conversations exist")
        test_result.add_step("Verifying both conversations exist")
        
        # Check customer service conversation
        conversation_page.switch_to_conversation(cs_conv_id)
        current_id = conversation_page.get_current_conversation_id()
        assert current_id == cs_conv_id, f"Expected current conversation to be {cs_conv_id}, got {current_id}"
        
        # Check technical support conversation
        conversation_page.switch_to_conversation(ts_conv_id)
        current_id = conversation_page.get_current_conversation_id()
        assert current_id == ts_conv_id, f"Expected current conversation to be {ts_conv_id}, got {current_id}"
        
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
