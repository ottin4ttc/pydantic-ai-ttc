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
  const formattedTime = new Date(timestamp).toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
  
  return (
    <div className={cn(
      "flex gap-3 mb-4",
      isUser ? "justify-end" : "justify-start"
    )}>
      {!isUser && (
        <Avatar className="h-8 w-8 bg-primary/20">
          <Bot className="h-4 w-4" />
        </Avatar>
      )}
      
      <div className={cn(
        "p-3 rounded-lg max-w-[80%]",
        isUser 
          ? "bg-primary text-primary-foreground" 
          : "bg-muted"
      )}>
        <div className="prose prose-sm dark:prose-invert">
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
        <div className="text-xs opacity-70 mt-1 text-right">
          {formattedTime}
        </div>
      </div>
      
      {isUser && (
        <Avatar className="h-8 w-8 bg-primary">
          <User className="h-4 w-4" />
        </Avatar>
      )}
    </div>
  );
};

export default MessageItem;
