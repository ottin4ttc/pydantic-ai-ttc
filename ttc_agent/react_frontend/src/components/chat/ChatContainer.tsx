import { useState, useEffect, useRef } from 'react';
import { Card } from '../ui/card';
import { ScrollArea } from '../ui/scroll-area';
import { Separator } from '../ui/separator';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Send, AlertCircle } from 'lucide-react';
import { Alert, AlertDescription } from '../ui/alert';
import { useToast } from '../../hooks/use-toast';
import MessageItem from './MessageItem';
import ChatService from '../../services/ChatService';
import { ChatMessage } from '../../types/chat';

const ChatContainer = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();
  
  // Fetch chat history on component mount
  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        setIsLoading(true);
        const history = await ChatService.getChatHistory();
        setMessages(history);
      } catch (error) {
        console.error('Failed to load chat history:', error);
        setError('Failed to load chat history. Please try again.');
        toast({
          variant: 'destructive',
          title: 'Error',
          description: 'Failed to load chat history',
        });
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchChatHistory();
  }, [toast]);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    };
    
    // Add user message immediately for better UX
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);
    
    try {
      // Send message to API
      const response = await ChatService.sendMessage(userMessage.content);
      
      if (response.body) {
        const reader = response.body.getReader();
        let receivedText = '';
        
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          // Decode and process the chunk
          const chunk = new TextDecoder().decode(value);
          receivedText += chunk;
          
          // Parse and update messages
          const lines = receivedText.split('\n');
          const validLines = lines.filter(line => line.trim().length > 0);
          
          try {
            const newMessages = validLines.map(line => JSON.parse(line) as ChatMessage);
            setMessages(prev => {
              // Filter out duplicates based on timestamp
              const timestamps = new Set(newMessages.map(m => m.timestamp));
              return [...prev.filter(m => !timestamps.has(m.timestamp) || m.role === 'user'), ...newMessages];
            });
          } catch (e) {
            console.error('Error parsing message chunk:', e);
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Failed to send message. Please try again.');
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to send message',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="flex flex-col h-[80vh] max-w-4xl mx-auto">
      <Card className="flex flex-col h-full border shadow-md">
        <div className="p-4 bg-primary/5">
          <h1 className="text-2xl font-bold text-center">TTC Agent Chat</h1>
          <p className="text-center text-muted-foreground">Ask me anything about TTC services</p>
        </div>
        
        <Separator />
        
        {error && (
          <Alert variant="destructive" className="m-2">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}
        
        <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
          {messages.length === 0 && !isLoading ? (
            <div className="text-center text-muted-foreground py-8">
              No messages yet. Start a conversation!
            </div>
          ) : (
            messages.map((message, index) => (
              <MessageItem
                key={`${message.timestamp}-${index}`}
                message={message}
              />
            ))
          )}
          
          {isLoading && (
            <div className="flex mb-4">
              <div className="bg-muted p-3 rounded-lg max-w-[80%] animate-pulse">
                <div className="h-4 bg-muted-foreground/20 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-muted-foreground/20 rounded w-1/2"></div>
              </div>
            </div>
          )}
        </ScrollArea>
        
        <Separator />
        
        <div className="p-4">
          <form className="flex gap-2" onSubmit={handleSubmit}>
            <Input 
              placeholder="Type your message here..." 
              className="flex-1"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
            />
            <Button type="submit" disabled={isLoading || !inputValue.trim()}>
              <Send className="h-4 w-4 mr-2" />
              Send
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
};

export default ChatContainer;
