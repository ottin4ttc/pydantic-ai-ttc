import pytest
import time
from playwright.sync_api import Page

class ConversationPage:
    """Page object for conversation interactions"""
    def __init__(self, page: Page):
        self.page = page
        
    def create_new_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        # 使用 data-testid 定位新建对话按钮
        new_conv_button = self.page.locator('[data-testid="new-conversation-button"]')
        new_conv_button.wait_for(state="visible")
        new_conv_button.click()
        
        # 等待网络请求完成
        self.page.wait_for_load_state("networkidle")
        # 等待一小段时间确保UI更新
        time.sleep(1)
        
        # 获取当前对话ID
        return self.get_current_conversation_id() or ""
        
    def send_message(self, message: str):
        """Send a message in the current conversation"""
        # 使用 data-testid 定位消息输入框
        input_box = self.page.locator('[data-testid="message-input"]')
        input_box.wait_for(state="visible")
        input_box.fill(message)
        
        # 使用 data-testid 定位发送按钮
        send_button = self.page.locator('[data-testid="send-button"]')
        send_button.wait_for(state="visible")
        send_button.click()
        
        # 等待消息发送
        self.page.wait_for_load_state("networkidle")
        
    def wait_for_response(self, timeout: int = 60000):
        """Wait for and verify the assistant's response"""
        try:
            # 等待加载指示器出现
            loading = self.page.locator('[data-testid="loading-indicator"]')
            if loading.count() > 0:
                # 如果加载指示器出现，等待它消失
                loading.wait_for(state="hidden", timeout=timeout)
            
            # 等待消息内容出现
            self.page.locator('[data-testid="message-content"]').last.wait_for(
                state="visible", 
                timeout=timeout
            )
            
            # 等待网络请求完成
            self.page.wait_for_load_state("networkidle")
            
            # 额外等待以确保响应完全加载
            time.sleep(1)
        except Exception as e:
            print(f"Error waiting for response: {e}")
            # 捕获当前页面截图以便调试
            self.page.screenshot(path="error-screenshot.png")
            raise
        
    def switch_to_conversation(self, conversation_id: str):
        """Switch to a specific conversation"""
        if not conversation_id:
            print("Warning: Attempting to switch to conversation with empty ID")
            return
            
        try:
            # 使用 data-testid 定位特定对话
            conv_selector = f'[data-testid="conversation-{conversation_id}"]'
            self.page.locator(conv_selector).wait_for(state="visible")
            self.page.locator(conv_selector).click()
            
            # 等待网络请求完成
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Error switching to conversation {conversation_id}: {e}")
            # 捕获当前页面截图以便调试
            self.page.screenshot(path=f"switch-error-{conversation_id}.png")
            raise
        
    def get_current_conversation_id(self) -> str:
        """Get the ID of the current conversation"""
        try:
            # 使用 data-is-current 属性找到当前活跃的对话
            current_conv = self.page.locator('[data-is-current="true"]')
            if current_conv.count() == 0:
                print("Warning: No active conversation found")
                return ""
            return current_conv.get_attribute("data-conversation-id") or ""
        except Exception as e:
            print(f"Error getting current conversation ID: {e}")
            return ""
        
    def get_last_message(self) -> str:
        """Get the text of the last message in the conversation"""
        try:
            # 使用 data-testid 定位消息文本
            messages = self.page.locator('[data-testid="message-text"]')
            if messages.count() == 0:
                print("Warning: No messages found")
                return ""
            last_message = messages.last
            return last_message.text_content() or ""
        except Exception as e:
            print(f"Error getting last message: {e}")
            return ""

@pytest.fixture
def conversation_page(page: Page) -> ConversationPage:
    """Fixture to provide a ConversationPage instance"""
    # 设置更长的超时时间
    page.set_default_timeout(60000)
    
    # 访问应用
    page.goto("http://localhost:5173")
    
    # 等待页面加载完成
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("networkidle")
    
    # 等待聊天容器出现
    page.wait_for_selector('[data-testid="chat-container"]', state="visible")
    
    # 截图以便调试
    page.screenshot(path="page-loaded.png")
    
    return ConversationPage(page)

def test_multiple_conversations(conversation_page: ConversationPage):
    """
    Test creating multiple conversations and switching between them.
    
    Steps:
    1. Create first conversation and send a message
    2. Create second conversation and send a message
    3. Switch back to first conversation and send another message
    """
    # 截图以便调试
    conversation_page.page.screenshot(path="test-start.png")
    
    # First conversation
    print("Creating first conversation...")
    conv1_id = conversation_page.create_new_conversation()
    print(f"First conversation ID: {conv1_id}")
    
    print("Sending message in first conversation...")
    conversation_page.send_message("Hello in first conversation")
    
    print("Waiting for response in first conversation...")
    conversation_page.wait_for_response()
    
    first_response = conversation_page.get_last_message()
    print(f"First response: {first_response}")
    
    # 截图以便调试
    conversation_page.page.screenshot(path="after-first-conversation.png")
    
    # Second conversation
    print("Creating second conversation...")
    second_id = conversation_page.create_new_conversation()
    print(f"Second conversation ID: {second_id}")
    
    print("Sending message in second conversation...")
    conversation_page.send_message("Hello in second conversation")
    
    print("Waiting for response in second conversation...")
    conversation_page.wait_for_response()
    
    second_response = conversation_page.get_last_message()
    print(f"Second response: {second_response}")
    
    # 截图以便调试
    conversation_page.page.screenshot(path="after-second-conversation.png")
    
    # Verify responses are different
    assert first_response != second_response, "First and second responses should be different"
    
    # Switch back to first conversation
    print(f"Switching back to first conversation: {conv1_id}")
    conversation_page.switch_to_conversation(conv1_id)
    
    print("Sending another message in first conversation...")
    conversation_page.send_message("Back to first conversation")
    
    print("Waiting for response...")
    conversation_page.wait_for_response()
    
    new_response = conversation_page.get_last_message()
    print(f"New response: {new_response}")
    
    # 截图以便调试
    conversation_page.page.screenshot(path="final-state.png")
    
    # Verify we got a new response
    assert new_response != first_response, "New response should be different from first response"
    assert new_response != second_response, "New response should be different from second response"
    
    print("Test completed successfully!") 