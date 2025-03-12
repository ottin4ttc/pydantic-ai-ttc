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
import { ConversationList } from './ConversationList';
import ChatService from '../../services/ChatService';
import { ChatMessage, Conversation } from '../../types/chat';

const ChatContainer = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const sentMessageRef = useRef<string | null>(null);
  const { toast } = useToast();
  
  // Fetch conversations on component mount
  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const conversations = await ChatService.getConversations();
        setConversations(conversations);
        
        // If there are conversations, select the first one
        if (conversations.length > 0) {
          setCurrentConversationId(conversations[0].id);
        } else {
          // If no conversations exist, create a new one
          handleNewConversation();
        }
      } catch (error) {
        console.error('Failed to load conversations:', error);
        toast({
          variant: 'destructive',
          title: 'Error',
          description: 'Failed to load conversations',
        });
      }
    };
    
    fetchConversations();
  }, []);
  
  // Fetch chat history when conversation changes
  useEffect(() => {
    const fetchChatHistory = async () => {
      if (!currentConversationId) return;
      
      try {
        setIsLoading(true);
        const history = await ChatService.getChatHistory(currentConversationId);
        setMessages(history);
      } catch (error) {
        console.error('Failed to load chat history:', error);
        setMessages([]);
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
  }, [currentConversationId]);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);
  
  const handleNewConversation = async () => {
    try {
      setIsLoading(true);
      const newConversation = await ChatService.createConversation();
      setConversations(prev => [newConversation, ...prev]);
      setCurrentConversationId(newConversation.id);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create conversation:', error);
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to create new conversation',
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading || !currentConversationId) return;
    
    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    sentMessageRef.current = userMessage.content;
    setInputValue('');
    setIsLoading(true);
    setError(null);
    
    try {
      setIsStreaming(true);
      const response = await ChatService.sendMessage(
        userMessage.content,
        currentConversationId
      );
      
      if (response.body) {
        const reader = response.body.getReader();
        const processedLines = new Set<string>();
        
        while (true) {
          const { done, value } = await reader.read();
          
          if (done) break;
          
          const chunk = new TextDecoder().decode(value);
          const lines = chunk.split('\n');
          const validLines = lines.filter(line => line.trim().length > 0);
          
          for (const line of validLines) {
            if (processedLines.has(line)) continue;
            processedLines.add(line);
            
            try {
              if (line.trim().startsWith('{') && line.trim().endsWith('}')) {
                const message = JSON.parse(line) as ChatMessage;
                
                if (message.role === 'user' && message.content === sentMessageRef.current) {
                  continue;
                }
                
                if (message.role === 'model') {
                  setMessages(prev => {
                    const existingIndex = prev.findIndex(m => 
                      m.role === 'model' && m.timestamp === message.timestamp
                    );
                    
                    if (existingIndex >= 0) {
                      const newMessages = [...prev];
                      newMessages[existingIndex] = message;
                      return newMessages;
                    } else {
                      return [...prev, message];
                    }
                  });
                } else if (message.role !== 'user') {
                  setMessages(prev => [...prev, message]);
                }
              }
            } catch (parseError) {
              console.error('Error parsing message line:', parseError);
            }
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
      setIsStreaming(false);
    }
  };
  
  return (
    <div className="flex h-[80vh] max-w-6xl mx-auto">
      <ConversationList
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={setCurrentConversationId}
        onNewConversation={handleNewConversation}
      />
      
      <Card className="flex flex-col h-full border shadow-md flex-1">
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
            messages.map((message) => (
              <MessageItem
                key={`${message.role}-${message.timestamp}`}
                message={message}
              />
            ))
          )}
          
          {isLoading && !isStreaming && (
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
              disabled={isLoading || !currentConversationId}
            />
            <Button 
              type="submit" 
              disabled={isLoading || !inputValue.trim() || !currentConversationId}
            >
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
