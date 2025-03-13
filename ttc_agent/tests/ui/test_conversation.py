import pytest
import time
import traceback
import os
from playwright.sync_api import Page
from ttc_agent.tests.ui.test_utils import UITestResult
from ttc_agent.tests.ui.conftest import RUN_DIR, LOGGER, REPORT_GENERATOR

class ConversationPage:
    """Page object for conversation interactions"""
    def __init__(self, page: Page):
        self.page = page
        
    def navigate_to_home(self):
        """Navigate to the home page and wait for it to load"""
        LOGGER.info("Navigating to home page")
        
        # Try multiple ports since Vite may use different ports if default is in use
        ports_to_try = [5173, 5174, 5175, 5176, 5177, 5178]
        connected = False
        
        # Check if frontend port is specified in environment
        frontend_port_env = os.environ.get("FRONTEND_PORT")
        if frontend_port_env and frontend_port_env.isdigit():
            # If we have a known port from environment, try it first
            port = int(frontend_port_env)
            LOGGER.info(f"Using frontend port from environment: {port}")
            ports_to_try = [port] + [p for p in ports_to_try if p != port]
        
        for port in ports_to_try:
            try:
                url = f"http://localhost:{port}"
                LOGGER.info(f"Trying to connect to {url}")
                # Use shorter timeout for quick failure
                self.page.goto(url, timeout=5000)
                
                # Check if page loaded successfully by looking for a common element
                try:
                    # Wait a short time for basic page elements
                    self.page.wait_for_selector("body", timeout=2000)
                    LOGGER.info(f"Successfully connected to {url}")
                    connected = True
                    break
                except Exception as e:
                    LOGGER.debug(f"Page at {url} loaded but no content found: {str(e)}")
                    continue
            except Exception as e:
                LOGGER.debug(f"Failed to connect to {url}: {str(e)}")
                continue
        
        if not connected:
            LOGGER.error("Failed to connect to frontend on any port")
            raise Exception("Could not connect to frontend service on any port")
            
        LOGGER.debug("Waiting for page to load")
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle")
        
        # 等待聊天容器出现
        LOGGER.debug("Waiting for chat container to be visible")
        self.page.wait_for_selector('[data-testid="chat-container"]', state="visible")
        
        # 截图以便调试
        screenshot_path = f"{RUN_DIR}/screenshots/page-loaded.png"
        LOGGER.debug(f"Taking screenshot: {screenshot_path}")
        self.page.screenshot(path=screenshot_path)
        
        LOGGER.info("Home page loaded successfully")
        
    def create_new_conversation(self, bot_type: str = "customer_service") -> str:
        """Create a new conversation and return its ID"""
        LOGGER.info(f"Creating new conversation with bot type: {bot_type}")
        
        try:
            # 使用 data-testid 定位新建对话按钮
            new_conv_button = self.page.locator('[data-testid="new-conversation-button"]')
            LOGGER.debug("Waiting for new conversation button to be visible")
            new_conv_button.wait_for(state="visible")
            LOGGER.debug("Clicking new conversation button")
            new_conv_button.click()
            
            # 等待对话框出现 - 使用更通用的选择器
            LOGGER.debug("Waiting for dialog to appear")
            # 使用多种选择器尝试定位对话框
            dialog_selectors = [
                '[data-testid="bot-selection-dialog"]',
                'div[role="dialog"]',
                '.fixed.inset-0',
                '.dialog-content'
            ]
            
            dialog_found = False
            for selector in dialog_selectors:
                LOGGER.debug(f"Trying to find dialog with selector: {selector}")
                if self.page.locator(selector).count() > 0:
                    LOGGER.debug(f"Dialog found with selector: {selector}")
                    dialog_found = True
                    break
            
            if not dialog_found:
                LOGGER.warning("Dialog not found with any selector, taking screenshot")
                self.page.screenshot(path=f"{RUN_DIR}/screenshots/dialog-not-found.png")
                
            # 等待一小段时间确保对话框完全显示
            LOGGER.debug("Waiting for dialog animation to complete")
            time.sleep(1)
            
            # 选择机器人类型 - 只有在非默认类型时才选择
            if bot_type != "customer_service":  # 默认已经选择了customer_service
                LOGGER.debug(f"Selecting bot type: {bot_type}")
                try:
                    # 尝试选择机器人类型
                    selector = self.page.locator('[data-testid="bot-type-selector"]')
                    if selector.count() > 0:
                        selector.click()
                        time.sleep(0.5)  # 等待下拉菜单打开
                        
                        # 选择对应的选项
                        option_selector = f'[data-value="{bot_type}"]'
                        option = self.page.locator(option_selector)
                        if option.count() > 0:
                            option.click()
                            LOGGER.debug(f"Selected bot type: {bot_type}")
                        else:
                            LOGGER.warning(f"Bot type option not found: {bot_type}")
                    else:
                        LOGGER.warning("Bot type selector not found")
                except Exception as e:
                    LOGGER.warning(f"Error selecting bot type: {str(e)}")
                    LOGGER.debug("Skipping bot type selection due to UI interaction issues")
            
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
            
        except Exception as e:
            error_msg = f"Error creating new conversation: {str(e)}"
            LOGGER.error(error_msg)
            LOGGER.error(traceback.format_exc())
            # 捕获当前页面截图以便调试
            screenshot_path = f"{RUN_DIR}/screenshots/create-conversation-error.png"
            LOGGER.debug(f"Taking error screenshot: {screenshot_path}")
            self.page.screenshot(path=screenshot_path)
            raise
        
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
