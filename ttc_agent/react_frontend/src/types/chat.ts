export interface ChatMessage {
  role: string;
  content: string;
  timestamp?: string;
}

export interface Conversation {
  id: string;
  role_type: string;
  bot_name: string;  // Add bot_name field
  created_at: string;
  updated_at: string;
}

export interface ConversationState {
  conversations: Conversation[];
  currentConversationId: string | null;
  loading: boolean;
  error: string | null;
}
