import React, { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from '../ui/dialog';
import { 
  Select, 
  SelectContent, 
  SelectItem, 
  SelectTrigger, 
  SelectValue 
} from '../ui/select';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Button } from '../ui/button';
import { Label } from '../ui/label';

// Define predefined bot types
const PREDEFINED_BOTS = [
  { 
    name: 'Customer Service', 
    role_type: 'customer_service',
    system_prompt: 'You are a helpful customer service representative. You are patient, friendly, and always try to help customers solve their problems. You communicate clearly and professionally.'
  },
  { 
    name: 'Technical Support', 
    role_type: 'technical_support',
    system_prompt: 'You are a technical support specialist. You have deep knowledge of our products and can help users solve technical issues. You explain technical concepts clearly and provide step-by-step solutions.'
  },
  { 
    name: 'Custom Bot', 
    role_type: 'custom',
    system_prompt: ''
  }
];

interface BotSelectionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreateBot: (roleType: string, botName: string) => void;
  currentBotType?: string;
}

const BotSelectionDialog = ({ 
  open, 
  onOpenChange, 
  onCreateBot,
  currentBotType = 'customer_service'
}: BotSelectionDialogProps) => {
  const [selectedBotType, setSelectedBotType] = useState(currentBotType);
  const [customBotName, setCustomBotName] = useState('');
  const [customSystemPrompt, setCustomSystemPrompt] = useState('');
  const [isCustomBot, setIsCustomBot] = useState(false);

  // Reset form when dialog opens
  useEffect(() => {
    if (open) {
      setSelectedBotType(currentBotType);
      setCustomBotName('');
      setCustomSystemPrompt('');
      setIsCustomBot(false);
    }
  }, [open, currentBotType]);

  // Handle bot type selection
  const handleBotTypeChange = (value: string) => {
    setSelectedBotType(value);
    setIsCustomBot(value === 'custom');
    
    // If selecting a predefined bot, reset custom fields
    if (value !== 'custom') {
      const selectedBot = PREDEFINED_BOTS.find(bot => bot.role_type === value);
      if (selectedBot) {
        setCustomBotName(selectedBot.name);
        setCustomSystemPrompt(selectedBot.system_prompt);
      }
    }
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isCustomBot && (!customBotName.trim() || !customSystemPrompt.trim())) {
      // Show validation error
      return;
    }
    
    const botName = isCustomBot ? customBotName : 
      PREDEFINED_BOTS.find(bot => bot.role_type === selectedBotType)?.name || 'Assistant';
    
    onCreateBot(selectedBotType, botName);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange} data-testid="bot-selection-dialog">
      <DialogContent className="sm:max-w-[425px]">
        <form onSubmit={handleSubmit} data-testid="bot-selection-form">
          <DialogHeader>
            <DialogTitle>创建新对话</DialogTitle>
            <DialogDescription>
              选择或创建一个Bot来开始新的对话
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="bot-type" className="text-right">
                Bot类型
              </Label>
              <Select
                value={selectedBotType}
                onValueChange={handleBotTypeChange}
                data-testid="bot-type-selector"
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="选择Bot类型" />
                </SelectTrigger>
                <SelectContent>
                  {PREDEFINED_BOTS.map((bot) => (
                    <SelectItem key={bot.role_type} value={bot.role_type}>
                      {bot.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            {isCustomBot && (
              <>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="bot-name" className="text-right">
                    Bot名称
                  </Label>
                  <Input
                    id="bot-name"
                    value={customBotName}
                    onChange={(e) => setCustomBotName(e.target.value)}
                    className="col-span-3"
                    placeholder="输入Bot名称"
                  />
                </div>
                
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="system-prompt" className="text-right">
                    系统提示词
                  </Label>
                  <Textarea
                    id="system-prompt"
                    value={customSystemPrompt}
                    onChange={(e) => setCustomSystemPrompt(e.target.value)}
                    className="col-span-3"
                    placeholder="输入系统提示词"
                    rows={4}
                  />
                </div>
              </>
            )}
          </div>
          
          <DialogFooter>
            <Button type="submit" data-testid="create-bot-button">创建</Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default BotSelectionDialog;
