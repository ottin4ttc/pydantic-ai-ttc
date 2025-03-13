import pytest
import time
from playwright.sync_api import Page

class ConversationPage:
    """Page object for conversation interactions"""
    def __init__(self, page: Page):
        self.page = page
        
    def create_new_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        # 查找包含"新对话"文本的按钮
        new_conv_button = self.page.get_by_role("button").filter(has_text="新对话")
        if new_conv_button.count() == 0:
            # 尝试英文按钮
            new_conv_button = self.page.get_by_role("button").filter(has_text="New")
        
        # 确保按钮可见并可点击
        new_conv_button.wait_for(state="visible")
        new_conv_button.click()
        
        # 等待网络请求完成
        self.page.wait_for_load_state("networkidle")
        # 等待一小段时间确保UI更新
        time.sleep(1)
        
        # 返回当前对话ID（如果能找到）
        return self.get_current_conversation_id() or ""
        
    def send_message(self, message: str):
        """Send a message in the current conversation"""
        # 查找输入框
        input_box = self.page.get_by_role("textbox")
        input_box.wait_for(state="visible")
        input_box.fill(message)
        
        # 查找发送按钮
        send_button = self.page.get_by_role("button").filter(has_text="Send")
        if send_button.count() == 0:
            # 尝试查找包含发送图标的按钮
            send_button = self.page.locator('button[type="submit"]')
        
        send_button.wait_for(state="visible")
        send_button.click()
        
        # 等待消息发送
        self.page.wait_for_load_state("networkidle")
        
    def wait_for_response(self, timeout=60000):
        """Wait for and verify the assistant's response"""
        try:
            # 等待页面上出现新消息
            start_time = time.time()
            while time.time() - start_time < timeout / 1000:
                # 检查是否有新消息出现
                messages = self.page.locator('.bg-muted, .message, .assistant-message')
                if messages.count() > 0:
                    # 找到消息后等待网络请求完成
                    self.page.wait_for_load_state("networkidle")
                    time.sleep(1)  # 额外等待以确保响应完全加载
                    return
                time.sleep(0.5)  # 短暂等待后再次检查
                
            # 如果超时，截图并抛出异常
            self.page.screenshot(path="timeout-waiting-for-response.png")
            raise TimeoutError("Timed out waiting for assistant response")
                
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
            # 尝试查找对话列表中的项目
            conversations = self.page.locator('.conversation, [role="button"]').all()
            for conv in conversations:
                # 点击第一个非活跃的对话
                if "active" not in (conv.get_attribute("class") or ""):
                    conv.click()
                    break
                    
            # 等待网络请求完成
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Error switching conversation: {e}")
            # 捕获当前页面截图以便调试
            self.page.screenshot(path="switch-error.png")
            raise
        
    def get_current_conversation_id(self) -> str:
        """Get the ID of the current conversation"""
        try:
            # 尝试查找活跃的对话
            active_conv = self.page.locator('.conversation.active, [data-is-current="true"]')
            if active_conv.count() > 0:
                return active_conv.get_attribute("data-conversation-id") or ""
                
            # 如果找不到，返回空字符串
            return ""
        except Exception as e:
            print(f"Error getting current conversation ID: {e}")
            return ""
        
    def get_last_message(self) -> str:
        """Get the text of the last message in the conversation"""
        try:
            # 查找所有消息元素
            messages = self.page.locator('.message, .bg-muted')
            if messages.count() == 0:
                print("Warning: No messages found")
                return ""
                
            # 获取最后一条消息的文本
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
    
    # 等待页面上出现任何内容
    page.wait_for_selector('body > *')
    
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