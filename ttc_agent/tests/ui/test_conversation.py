import pytest
import time
import traceback
from playwright.sync_api import Page
from ttc_agent.tests.ui.test_utils import create_test_run_dir, setup_logger, UITestResult, ReportGenerator

# 全局变量
RUN_DIR = create_test_run_dir()
LOGGER = setup_logger(RUN_DIR)
REPORT_GENERATOR = ReportGenerator(RUN_DIR)

class ConversationPage:
    """Page object for conversation interactions"""
    def __init__(self, page: Page):
        self.page = page
        
    def create_new_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        LOGGER.info("Creating new conversation")
        
        # 使用 data-testid 定位新建对话按钮
        new_conv_button = self.page.locator('[data-testid="new-conversation-button"]')
        LOGGER.debug("Waiting for new conversation button to be visible")
        new_conv_button.wait_for(state="visible")
        LOGGER.debug("Clicking new conversation button")
        new_conv_button.click()
        
        # 等待网络请求完成
        LOGGER.debug("Waiting for network idle")
        self.page.wait_for_load_state("networkidle")
        # 等待一小段时间确保UI更新
        LOGGER.debug("Waiting for UI update")
        time.sleep(1)
        
        # 获取当前对话ID
        conversation_id = self.get_current_conversation_id() or ""
        LOGGER.info(f"Created new conversation with ID: {conversation_id}")
        return conversation_id
        
    def send_message(self, message: str):
        """Send a message in the current conversation"""
        LOGGER.info(f"Sending message: {message}")
        
        # 使用 data-testid 定位消息输入框
        input_box = self.page.locator('[data-testid="message-input"]')
        LOGGER.debug("Waiting for message input to be visible")
        input_box.wait_for(state="visible")
        LOGGER.debug("Filling message input")
        input_box.fill(message)
        
        # 使用 data-testid 定位发送按钮
        send_button = self.page.locator('[data-testid="send-button"]')
        LOGGER.debug("Waiting for send button to be visible")
        send_button.wait_for(state="visible")
        LOGGER.debug("Clicking send button")
        send_button.click()
        
        # 等待消息发送
        LOGGER.debug("Waiting for network idle after sending message")
        self.page.wait_for_load_state("networkidle")
        LOGGER.info("Message sent successfully")
        
    def wait_for_response(self, timeout: int = 60000):
        """Wait for and verify the assistant's response"""
        LOGGER.info(f"Waiting for assistant response (timeout: {timeout}ms)")
        try:
            # 等待加载指示器出现
            loading = self.page.locator('[data-testid="loading-indicator"]')
            if loading.count() > 0:
                # 如果加载指示器出现，等待它消失
                LOGGER.debug("Loading indicator found, waiting for it to disappear")
                loading.wait_for(state="hidden", timeout=timeout)
                LOGGER.debug("Loading indicator disappeared")
            else:
                LOGGER.debug("No loading indicator found")
            
            # 等待消息内容出现
            LOGGER.debug("Waiting for message content to appear")
            self.page.locator('[data-testid="message-content"]').last.wait_for(
                state="visible", 
                timeout=timeout
            )
            LOGGER.debug("Message content appeared")
            
            # 等待网络请求完成
            LOGGER.debug("Waiting for network idle")
            self.page.wait_for_load_state("networkidle")
            
            # 额外等待以确保响应完全加载
            LOGGER.debug("Waiting additional time for response to fully load")
            time.sleep(1)
            LOGGER.info("Assistant response received")
        except Exception as e:
            error_msg = f"Error waiting for response: {str(e)}"
            LOGGER.error(error_msg)
            LOGGER.error(traceback.format_exc())
            # 捕获当前页面截图以便调试
            screenshot_path = f"{RUN_DIR}/screenshots/error-waiting-response.png"
            LOGGER.debug(f"Taking error screenshot: {screenshot_path}")
            self.page.screenshot(path=screenshot_path)
            raise
        
    def switch_to_conversation(self, conversation_id: str):
        """Switch to a specific conversation"""
        LOGGER.info(f"Switching to conversation: {conversation_id}")
        if not conversation_id:
            warning_msg = "Attempting to switch to conversation with empty ID"
            LOGGER.warning(warning_msg)
            return
            
        try:
            # 使用 data-testid 定位特定对话
            conv_selector = f'[data-testid="conversation-{conversation_id}"]'
            LOGGER.debug(f"Waiting for conversation element to be visible: {conv_selector}")
            self.page.locator(conv_selector).wait_for(state="visible")
            LOGGER.debug("Clicking conversation element")
            self.page.locator(conv_selector).click()
            
            # 等待网络请求完成
            LOGGER.debug("Waiting for network idle after switching conversation")
            self.page.wait_for_load_state("networkidle")
            LOGGER.info(f"Successfully switched to conversation: {conversation_id}")
        except Exception as e:
            error_msg = f"Error switching to conversation {conversation_id}: {str(e)}"
            LOGGER.error(error_msg)
            LOGGER.error(traceback.format_exc())
            # 捕获当前页面截图以便调试
            screenshot_path = f"{RUN_DIR}/screenshots/switch-error-{conversation_id}.png"
            LOGGER.debug(f"Taking error screenshot: {screenshot_path}")
            self.page.screenshot(path=screenshot_path)
            raise
        
    def get_current_conversation_id(self) -> str:
        """Get the ID of the current conversation"""
        LOGGER.debug("Getting current conversation ID")
        try:
            # 使用 data-is-current 属性找到当前活跃的对话
            current_conv = self.page.locator('[data-is-current="true"]')
            if current_conv.count() == 0:
                LOGGER.warning("No active conversation found")
                return ""
            conversation_id = current_conv.get_attribute("data-conversation-id") or ""
            LOGGER.debug(f"Current conversation ID: {conversation_id}")
            return conversation_id
        except Exception as e:
            error_msg = f"Error getting current conversation ID: {str(e)}"
            LOGGER.error(error_msg)
            LOGGER.error(traceback.format_exc())
            return ""
        
    def get_last_message(self) -> str:
        """Get the text of the last message in the conversation"""
        LOGGER.debug("Getting last message text")
        try:
            # 使用 data-testid 定位消息文本
            messages = self.page.locator('[data-testid="message-text"]')
            if messages.count() == 0:
                LOGGER.warning("No messages found")
                return ""
            last_message = messages.last
            message_text = last_message.text_content() or ""
            LOGGER.debug(f"Last message text: {message_text[:50]}...")  # 只记录前50个字符
            return message_text
        except Exception as e:
            error_msg = f"Error getting last message: {str(e)}"
            LOGGER.error(error_msg)
            LOGGER.error(traceback.format_exc())
            return ""

@pytest.fixture
def conversation_page(page: Page) -> ConversationPage:
    """Fixture to provide a ConversationPage instance"""
    LOGGER.info("Setting up conversation page fixture")
    
    # 设置更长的超时时间
    LOGGER.debug("Setting page timeout to 60000ms")
    page.set_default_timeout(60000)
    
    # 访问应用
    LOGGER.info("Navigating to application")
    page.goto("http://localhost:5173")
    
    # 等待页面加载完成
    LOGGER.debug("Waiting for page to load")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("networkidle")
    
    # 等待聊天容器出现
    LOGGER.debug("Waiting for chat container to be visible")
    page.wait_for_selector('[data-testid="chat-container"]', state="visible")
    
    # 截图以便调试
    screenshot_path = f"{RUN_DIR}/screenshots/page-loaded.png"
    LOGGER.debug(f"Taking screenshot: {screenshot_path}")
    page.screenshot(path=screenshot_path)
    
    LOGGER.info("Conversation page fixture setup complete")
    return ConversationPage(page)

def test_multiple_conversations(conversation_page: ConversationPage):
    """
    Test creating multiple conversations and switching between them.
    
    Steps:
    1. Create first conversation and send a message
    2. Create second conversation and send a message
    3. Switch back to first conversation and send another message
    """
    test_result = UITestResult("test_multiple_conversations", RUN_DIR)
    
    try:
        LOGGER.info("Starting test_multiple_conversations")
        
        # 截图以便调试
        test_result.add_screenshot("test-start", conversation_page.page)
        LOGGER.debug("Took initial screenshot")
        
        # First conversation
        LOGGER.info("Step 1: Creating first conversation")
        test_result.add_step("Creating first conversation")
        conv1_id = conversation_page.create_new_conversation()
        LOGGER.info(f"First conversation ID: {conv1_id}")
        
        LOGGER.info("Step 2: Sending message in first conversation")
        test_result.add_step("Sending message in first conversation")
        conversation_page.send_message("Hello in first conversation")
        
        LOGGER.info("Step 3: Waiting for response in first conversation")
        test_result.add_step("Waiting for response in first conversation")
        conversation_page.wait_for_response()
        
        first_response = conversation_page.get_last_message()
        LOGGER.info(f"First response received: {first_response[:50]}...")  # 只记录前50个字符
        
        # 截图以便调试
        test_result.add_screenshot("after-first-conversation", conversation_page.page)
        LOGGER.debug("Took screenshot after first conversation")
        
        # Second conversation
        LOGGER.info("Step 4: Creating second conversation")
        test_result.add_step("Creating second conversation")
        second_id = conversation_page.create_new_conversation()
        LOGGER.info(f"Second conversation ID: {second_id}")
        
        LOGGER.info("Step 5: Sending message in second conversation")
        test_result.add_step("Sending message in second conversation")
        conversation_page.send_message("Hello in second conversation")
        
        LOGGER.info("Step 6: Waiting for response in second conversation")
        test_result.add_step("Waiting for response in second conversation")
        conversation_page.wait_for_response()
        
        second_response = conversation_page.get_last_message()
        LOGGER.info(f"Second response received: {second_response[:50]}...")  # 只记录前50个字符
        
        # 截图以便调试
        test_result.add_screenshot("after-second-conversation", conversation_page.page)
        LOGGER.debug("Took screenshot after second conversation")
        
        # Verify responses are different
        LOGGER.info("Step 7: Verifying responses are different")
        test_result.add_step("Verifying responses are different")
        assert first_response != second_response, "First and second responses should be different"
        LOGGER.info("Responses are different as expected")
        
        # Switch back to first conversation
        LOGGER.info(f"Step 8: Switching back to first conversation: {conv1_id}")
        test_result.add_step(f"Switching back to first conversation: {conv1_id}")
        conversation_page.switch_to_conversation(conv1_id)
        
        LOGGER.info("Step 9: Sending another message in first conversation")
        test_result.add_step("Sending another message in first conversation")
        conversation_page.send_message("Back to first conversation")
        
        LOGGER.info("Step 10: Waiting for response")
        test_result.add_step("Waiting for response")
        conversation_page.wait_for_response()
        
        new_response = conversation_page.get_last_message()
        LOGGER.info(f"New response received: {new_response[:50]}...")  # 只记录前50个字符
        
        # 截图以便调试
        test_result.add_screenshot("final-state", conversation_page.page)
        LOGGER.debug("Took final screenshot")
        
        # Verify we got a new response
        LOGGER.info("Step 11: Verifying new response is different from previous responses")
        test_result.add_step("Verifying new response is different from previous responses")
        assert new_response != first_response, "New response should be different from first response"
        assert new_response != second_response, "New response should be different from second response"
        
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
        
        # 打印测试结果摘要
        status = "PASSED" if test_result.status == "pass" else "FAILED"
        LOGGER.info(f"Test {test_result.name}: {status}")
        if test_result.error:
            LOGGER.info(f"Error: {test_result.error}")
        LOGGER.info(f"Duration: {round(test_result.end_time - test_result.start_time, 2) if test_result.end_time else 0} seconds")
        LOGGER.info(f"Screenshots: {len(test_result.screenshots)}")
        LOGGER.info(f"Steps: {len(test_result.steps)}")
        LOGGER.info(f"Test results directory: {RUN_DIR}") 