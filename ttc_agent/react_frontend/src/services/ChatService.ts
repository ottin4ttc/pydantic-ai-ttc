import { ChatMessage } from '../types/chat';

/**
 * Service for interacting with the chat API
 */
class ChatService {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  /**
   * Fetches chat history from the API
   * @returns Promise with array of chat messages
   */
  async getChatHistory(): Promise<ChatMessage[]> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/`, {
        method: 'GET',
        headers: {
          'Accept': 'text/plain',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch chat history: ${response.status}`);
      }

      const text = await response.text();
      
      // Check if the response is HTML (error page) instead of JSON
      if (text.trim().startsWith('<!DOCTYPE') || text.trim().startsWith('<html')) {
        console.warn('Received HTML instead of JSON from chat history endpoint');
        return [];
      }
      
      // Parse newline-delimited JSON
      try {
        const messages: ChatMessage[] = text
          .split('\n')
          .filter((line: string) => line.trim().length > 0)
          .map((line: string) => JSON.parse(line));
        
        return messages;
      } catch (parseError) {
        console.error('Error parsing chat history:', parseError);
        return [];
      }
    } catch (error) {
      console.error('Error fetching chat history:', error);
      return [];
    }
  }

  /**
   * Sends a message to the API and returns a readable stream of the response
   * @param prompt The message to send
   * @returns Promise with a Response object
   */
  async sendMessage(prompt: string): Promise<Response> {
    try {
      const formData = new FormData();
      formData.append('prompt', prompt);
      
      const response = await fetch(`${this.baseUrl}/chat/`, {
        method: 'POST',
        body: formData,
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
