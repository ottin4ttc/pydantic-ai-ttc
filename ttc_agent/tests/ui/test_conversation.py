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
        
        
    def create_new_conversation(self, bot_type: str = "customer_service") -> str:
        """Create a new conversation and return its ID"""
        LOGGER.info(f"Creating new conversation with bot type: {bot_type}")
        
        # 使用 data-testid 定位新建对话按钮
        new_conv_button = self.page.locator('[data-testid="new-conversation-button"]')
        LOGGER.debug("Waiting for new conversation button to be visible")
        new_conv_button.wait_for(state="visible")
        LOGGER.debug("Clicking new conversation button")
        new_conv_button.click()
        
        # 等待对话框出现
        LOGGER.debug("Waiting for bot selection dialog to appear")
        self.page.locator('[data-testid="bot-selection-dialog"]').wait_for(state="visible")
        
        # 选择机器人类型
        if bot_type != "customer_service":  # 默认已经选择了customer_service
            LOGGER.debug(f"Selecting bot type: {bot_type}")
            self.page.locator('[data-testid="bot-type-selector"]').click()
            self.page.locator(f'[data-value="{bot_type}"]').click()
        
        # 点击创建按钮
        LOGGER.debug("Clicking create button")
        create_button = self.page.locator('[data-testid="create-bot-button"]')
        create_button.click()
        
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

