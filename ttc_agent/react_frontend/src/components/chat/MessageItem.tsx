import { cn } from '../../lib/utils';
import { Avatar } from '../ui/avatar';
import { User, Bot } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { ChatMessage } from '../../types/chat';

interface MessageItemProps {
  message: ChatMessage;
}

const MessageItem = ({ message }: MessageItemProps) => {
  const { role, content, timestamp } = message;
  const isUser = role === 'user';
  const messageId = message.id || `${role}-${timestamp}`;
  const formattedTime = timestamp ? new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  }) : '';
  
  return (
    <div 
      className={cn(
        "flex gap-3 mb-4",
        isUser ? "justify-end" : "justify-start"
      )}
      data-testid={`message-${messageId}`}
      data-message-role={role}
      data-message-id={messageId}
    >
      {!isUser && (
        <Avatar className="h-8 w-8 bg-primary/20" data-testid="assistant-avatar">
          <Bot className="h-4 w-4" />
        </Avatar>
      )}
      
      <div 
        className={cn(
          "p-3 rounded-lg max-w-[80%]",
          isUser 
            ? "bg-primary text-primary-foreground" 
            : "bg-muted"
        )}
        data-testid="message-content"
      >
        <div className="prose prose-sm dark:prose-invert" data-testid="message-text">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
        <div className="text-xs opacity-70 mt-1 text-right" data-testid="message-timestamp">
          {formattedTime}
        </div>
      </div>
      
      {isUser && (
        <Avatar className="h-8 w-8 bg-primary" data-testid="user-avatar">
          <User className="h-4 w-4" />
        </Avatar>
      )}
    </div>
  );
};

export default MessageItem;
