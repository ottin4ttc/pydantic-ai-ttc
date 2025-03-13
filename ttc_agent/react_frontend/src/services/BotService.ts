import { Bot } from '../types/chat';

/**
 * Service for interacting with the bot management API
 */
class BotService {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  async createBot(name: string, roleType: string, systemPrompt: string, isDefault: boolean = false): Promise<Bot> {
    try {
      const response = await fetch(`${this.baseUrl}/api/bots`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          role_type: roleType,
          system_prompt: systemPrompt,
          is_default: isDefault
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to create bot: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating bot:', error);
      throw error;
    }
  }

  async getBots(): Promise<Bot[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/bots`);

      if (!response.ok) {
        throw new Error(`Failed to fetch bots: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching bots:', error);
      return [];
    }
  }

  async getBot(id: string): Promise<Bot | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/bots/${id}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch bot: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching bot:', error);
      return null;
    }
  }

  async getDefaultBot(): Promise<Bot | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/bots/default`);

      if (!response.ok) {
        throw new Error(`Failed to fetch default bot: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching default bot:', error);
      return null;
    }
  }

  async updateBot(id: string, name: string, roleType: string, systemPrompt: string, isDefault: boolean = false): Promise<Bot | null> {
    try {
      const response = await fetch(`${this.baseUrl}/api/bots/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name,
          role_type: roleType,
          system_prompt: systemPrompt,
          is_default: isDefault
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to update bot: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating bot:', error);
      return null;
    }
  }

  async deleteBot(id: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/bots/${id}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`Failed to delete bot: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error deleting bot:', error);
      return false;
    }
  }

  async generateWelcomeMessage(id: string): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/api/bots/${id}/welcome`);

      if (!response.ok) {
        throw new Error(`Failed to generate welcome message: ${response.status}`);
      }

      const data = await response.json();
      return data.content;
    } catch (error) {
      console.error('Error generating welcome message:', error);
      return "Welcome! How can I assist you today?";
    }
  }
}

export default new BotService();
