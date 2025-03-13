import { ChatMessage, Conversation } from '../types/chat';

/**
 * Service for interacting with the chat API
 */
class ChatService {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  async createConversation(roleType: string = 'default', botName: string = 'Assistant', botId?: string): Promise<Conversation> {
    try {
      // Send role_type, bot_name, and optional bot_id in the request body
      console.log('Creating new conversation with bot:', botName, botId ? `(ID: ${botId})` : '');
      const response = await fetch(`${this.baseUrl}/api/new_conversation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          role_type: roleType,
          bot_name: botName,
          bot_id: botId
        })
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
      // Use direct API endpoint for conversations
      const response = await fetch(`${this.baseUrl}/api/chat/conversations`);

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
      // Use direct API endpoint for conversation
      const response = await fetch(`${this.baseUrl}/api/chat/conversation/${id}`);

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
      const response = await fetch(`${this.baseUrl}/api/chat/${conversationId}/history`);

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
      const response = await fetch(`${this.baseUrl}/api/chat/${conversationId}`, {
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
