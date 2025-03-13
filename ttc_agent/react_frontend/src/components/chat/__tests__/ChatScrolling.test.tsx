import { render, screen, fireEvent, act } from '@testing-library/react';
import { vi } from 'vitest';
import ChatContainer from '../ChatContainer';
import ChatService from '../../../services/ChatService';

// Mock the ChatService
vi.mock('../../../services/ChatService', () => ({
  default: {
    getConversations: vi.fn(),
    getChatHistory: vi.fn(),
    createConversation: vi.fn(),
    sendMessage: vi.fn(),
  },
}));

// Mock the scroll behavior
Element.prototype.scrollIntoView = vi.fn();

describe('Chat Window Scrolling', () => {
  beforeEach(() => {
    // Reset mocks
    vi.clearAllMocks();
    
    // Setup mock data
    ChatService.getConversations.mockResolvedValue([
      { id: 'conv1', role_type: 'assistant', bot_name: 'Test Bot', created_at: '2023-01-01', updated_at: '2023-01-01' }
    ]);
    
    ChatService.getChatHistory.mockResolvedValue([
      { role: 'user', content: 'Hello', timestamp: '2023-01-01T12:00:00Z', id: 'msg1' },
      { role: 'model', content: 'Hi there', timestamp: '2023-01-01T12:01:00Z', id: 'msg2' }
    ]);
  });
  
  test('should automatically scroll to bottom when new messages arrive', async () => {
    // Render the component
    render(<ChatContainer />);
    
    // Wait for initial messages to load
    await screen.findByTestId('message-msg1');
    
    // Verify scrollIntoView was called
    expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth' });
    
    // Simulate sending a new message
    const input = screen.getByTestId('message-input');
    const sendButton = screen.getByTestId('send-button');
    
    fireEvent.change(input, { target: { value: 'New message' } });
    fireEvent.click(sendButton);
    
    // Verify scrollIntoView was called again
    expect(Element.prototype.scrollIntoView).toHaveBeenCalledTimes(2);
  });
  
  test('should not auto-scroll when user has manually scrolled up', async () => {
    // Render the component
    render(<ChatContainer />);
    
    // Wait for initial messages to load
    await screen.findByTestId('message-msg1');
    
    // Simulate user scrolling up
    const scrollArea = screen.getByTestId('messages-scroll-area');
    fireEvent.scroll(scrollArea, { target: { scrollTop: 0, scrollHeight: 500, clientHeight: 300 } });
    
    // Reset the mock to check if it's called again
    Element.prototype.scrollIntoView.mockClear();
    
    // Simulate receiving a new message
    act(() => {
      // Update messages state to simulate new message
      const newMessages = [
        { role: 'user', content: 'Hello', timestamp: '2023-01-01T12:00:00Z', id: 'msg1' },
        { role: 'model', content: 'Hi there', timestamp: '2023-01-01T12:01:00Z', id: 'msg2' },
        { role: 'user', content: 'New message', timestamp: '2023-01-01T12:02:00Z', id: 'msg3' }
      ];
      ChatService.getChatHistory.mockResolvedValue(newMessages);
    });
    
    // Verify scrollIntoView was not called again
    expect(Element.prototype.scrollIntoView).not.toHaveBeenCalled();
    
    // Verify scroll-to-bottom button appears
    const scrollButton = await screen.findByTestId('scroll-to-bottom');
    expect(scrollButton).toBeInTheDocument();
    
    // Click the scroll-to-bottom button
    fireEvent.click(scrollButton);
    
    // Verify scrollIntoView was called
    expect(Element.prototype.scrollIntoView).toHaveBeenCalledWith({ behavior: 'smooth' });
  });
});
