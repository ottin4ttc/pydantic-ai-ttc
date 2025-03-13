// UI mockup component for reference
import { Card } from '../ui/card';
import { ScrollArea } from '../ui/scroll-area';
import { Separator } from '../ui/separator';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Send } from 'lucide-react';

// This is a UI mockup for the chat interface
const ChatInterface = () => {
  return (
    <div className="flex flex-col h-[80vh] max-w-4xl mx-auto" data-testid="chat-interface">
      <Card className="flex flex-col h-full border shadow-md">
        <div className="p-4 bg-primary/5" data-testid="chat-header">
          <h1 className="text-2xl font-bold text-center">TTC Agent Chat</h1>
          <p className="text-center text-muted-foreground">Ask me anything about TTC services</p>
        </div>
        
        <Separator />
        
        <ScrollArea className="flex-1 p-4" data-testid="chat-messages">
          {/* User Message Example */}
          <div className="flex justify-end mb-4" data-testid="user-message">
            <div className="bg-primary text-primary-foreground p-3 rounded-lg max-w-[80%]">
              <p>Hello, I need help with understanding how to use the TTC agent.</p>
              <div className="text-xs opacity-70 text-right mt-1">12:30 PM</div>
            </div>
          </div>
          
          {/* AI Response Example */}
          <div className="flex mb-4" data-testid="assistant-message">
            <div className="bg-muted p-3 rounded-lg max-w-[80%]">
              <p>Hi there! I'm the TTC Agent, designed to help you with various tasks. You can ask me questions about:</p>
              <ul className="list-disc pl-5 mt-2">
                <li>How to use the TTC services</li>
                <li>Information about specific features</li>
                <li>Troubleshooting common issues</li>
                <li>Best practices and recommendations</li>
              </ul>
              <p className="mt-2">What specific aspect would you like to know more about?</p>
              <div className="text-xs opacity-70 mt-1">12:31 PM</div>
            </div>
          </div>
          
          {/* Another User Message Example */}
          <div className="flex justify-end mb-4">
            <div className="bg-primary text-primary-foreground p-3 rounded-lg max-w-[80%]">
              <p>Can you explain how the chat streaming works?</p>
              <div className="text-xs opacity-70 text-right mt-1">12:32 PM</div>
            </div>
          </div>
          
          {/* Another AI Response Example */}
          <div className="flex mb-4">
            <div className="bg-muted p-3 rounded-lg max-w-[80%]">
              <p>Certainly! The chat streaming functionality works like this:</p>
              <ol className="list-decimal pl-5 mt-2">
                <li>When you send a message, it's sent to the server via a POST request</li>
                <li>The server processes your request and starts generating a response</li>
                <li>Instead of waiting for the complete response, the server sends chunks of the response as they're generated</li>
                <li>The frontend receives these chunks in real-time and displays them progressively</li>
                <li>This creates a more interactive experience as you can see the response being built word by word</li>
              </ol>
              <p className="mt-2">This streaming approach reduces perceived latency and provides a more engaging user experience!</p>
              <div className="text-xs opacity-70 mt-1">12:33 PM</div>
            </div>
          </div>
          
          {/* Loading State Example */}
          <div className="flex mb-4" data-testid="message-loading">
            <div className="bg-muted p-3 rounded-lg max-w-[80%] animate-pulse">
              <div className="h-4 bg-muted-foreground/20 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-muted-foreground/20 rounded w-1/2"></div>
            </div>
          </div>
        </ScrollArea>
        
        <Separator />
        
        <div className="p-4" data-testid="chat-input-container">
          <form className="flex gap-2" data-testid="chat-form">
            <Input 
              placeholder="Type your message here..." 
              className="flex-1"
              data-testid="chat-input"
            />
            <Button type="submit" data-testid="send-button">
              <Send className="h-4 w-4 mr-2" />
              Send
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
};

export default ChatInterface;
