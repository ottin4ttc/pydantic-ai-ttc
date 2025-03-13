import pytest
from playwright.sync_api import Page, expect

class ConversationPage:
    """Page object for conversation interactions"""
    def __init__(self, page: Page):
        self.page = page
        
    def create_new_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        # TODO: Implement based on actual UI
        new_conv_button = self.page.get_by_role("button", name="New Conversation")
        new_conv_button.click()
        # Wait for the new conversation to be created
        self.page.wait_for_load_state("networkidle")
        return self.get_current_conversation_id()
        
    def send_message(self, message: str):
        """Send a message in the current conversation"""
        # TODO: Implement based on actual UI
        input_box = self.page.get_by_role("textbox")
        input_box.fill(message)
        input_box.press("Enter")
        
    def wait_for_response(self):
        """Wait for and verify the assistant's response"""
        # TODO: Implement based on actual UI
        # Wait for response to appear
        self.page.wait_for_selector(".assistant-message", state="visible")
        # Wait for response to complete
        self.page.wait_for_load_state("networkidle")
        
    def switch_to_conversation(self, conversation_id: str):
        """Switch to a specific conversation"""
        # TODO: Implement based on actual UI
        conv_selector = f'[data-conversation-id="{conversation_id}"]'
        self.page.click(conv_selector)
        self.page.wait_for_load_state("networkidle")
        
    def get_current_conversation_id(self) -> str:
        """Get the ID of the current conversation"""
        # TODO: Implement based on actual UI
        current_conv = self.page.locator(".conversation.active")
        return current_conv.get_attribute("data-conversation-id")
        
    def get_last_message(self) -> str:
        """Get the text of the last message in the conversation"""
        # TODO: Implement based on actual UI
        messages = self.page.locator(".message")
        last_message = messages.last
        return last_message.text_content()

@pytest.fixture
def conversation_page(page: Page) -> ConversationPage:
    """Fixture to provide a ConversationPage instance"""
    # TODO: Update URL based on actual application
    page.goto("http://localhost:3000")
    return ConversationPage(page)

def test_multiple_conversations(conversation_page: ConversationPage):
    """
    Test creating multiple conversations and switching between them.
    
    Steps:
    1. Create first conversation and send a message
    2. Create second conversation and send a message
    3. Switch back to first conversation and send another message
    """
    # First conversation
    conv1_id = conversation_page.create_new_conversation()
    conversation_page.send_message("Hello in first conversation")
    conversation_page.wait_for_response()
    first_response = conversation_page.get_last_message()
    
    # Second conversation
    conv2_id = conversation_page.create_new_conversation()
    conversation_page.send_message("Hello in second conversation")
    conversation_page.wait_for_response()
    second_response = conversation_page.get_last_message()
    
    # Verify responses are different
    assert first_response != second_response
    
    # Switch back to first conversation
    conversation_page.switch_to_conversation(conv1_id)
    conversation_page.send_message("Back to first conversation")
    conversation_page.wait_for_response()
    new_response = conversation_page.get_last_message()
    
    # Verify we got a new response
    assert new_response != first_response
    assert new_response != second_response 