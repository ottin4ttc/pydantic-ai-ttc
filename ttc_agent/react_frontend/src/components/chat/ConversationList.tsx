import React from 'react';
import { Button } from '@/components/ui/button';
import { PlusCircle } from 'lucide-react';
import { Conversation } from '@/types/chat';
import { cn } from '@/lib/utils';

interface ConversationListProps {
  conversations: Conversation[];
  currentConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
}

export function ConversationList({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
}: ConversationListProps) {
  return (
    <div className="w-64 h-full bg-gray-100 p-4 flex flex-col gap-2" data-testid="conversation-list">
      <Button
        variant="outline"
        className="w-full flex items-center gap-2"
        onClick={onNewConversation}
        data-testid="new-conversation-button"
      >
        <PlusCircle className="h-4 w-4" />
        新对话
      </Button>
      
      <div className="flex flex-col gap-1 overflow-y-auto" data-testid="conversations-container">
        {conversations.map((conversation) => (
          <Button
            key={conversation.id}
            variant="ghost"
            className={cn(
              "w-full justify-start text-left font-normal",
              currentConversationId === conversation.id && "bg-gray-200"
            )}
            onClick={() => onSelectConversation(conversation.id)}
            data-testid={`conversation-${conversation.id}`}
            data-conversation-id={conversation.id}
            data-is-current={currentConversationId === conversation.id}
          >
            {new Date(conversation.created_at).toLocaleString()}
          </Button>
        ))}
      </div>
    </div>
  );
} 