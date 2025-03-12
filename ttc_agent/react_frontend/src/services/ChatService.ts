import { ChatMessage, Conversation } from '../types/chat';

/**
 * Service for interacting with the chat API
 */
class ChatService {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  async createConversation(roleType: string = 'default'): Promise<Conversation> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ role_type: roleType }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create conversation: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  }

  async getConversations(): Promise<Conversation[]> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations`);

      if (!response.ok) {
        throw new Error(`Failed to fetch conversations: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching conversations:', error);
      return [];
    }
  }

  async getConversation(id: string): Promise<Conversation | null> {
    try {
      const response = await fetch(`${this.baseUrl}/conversations/${id}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch conversation: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching conversation:', error);
      return null;
    }
  }

  async getChatHistory(conversationId: string): Promise<ChatMessage[]> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/${conversationId}/history`);

      if (!response.ok) {
        throw new Error(`Failed to fetch chat history: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching chat history:', error);
      return [];
    }
  }

  async sendMessage(content: string, conversationId: string, roleType: string = 'default'): Promise<Response> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/${conversationId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          role_type: roleType,
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.status}`);
      }

      return response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }
}

export default new ChatService();
