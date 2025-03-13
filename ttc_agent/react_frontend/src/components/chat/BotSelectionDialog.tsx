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

import { BotService } from '../../services';
import { Bot } from '../../types/chat';
import { useToast } from '../../hooks/use-toast';
import { Badge } from '../ui/badge';

interface BotSelectionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreateBot: (roleType: string, botName: string, botId?: string) => void;
  currentBotType?: string;
}

const BotSelectionDialog = ({ 
  open, 
  onOpenChange, 
  onCreateBot,
  currentBotType
}: BotSelectionDialogProps) => {
  const [selectedBot, setSelectedBot] = useState<Bot | null>(null);
  const [bots, setBots] = useState<Bot[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Fetch bots when dialog opens
  useEffect(() => {
    if (open) {
      fetchBots();
    }
  }, [open]);

  const fetchBots = async () => {
    setLoading(true);
    try {
      const botsList = await BotService.getBots();
      setBots(botsList);
      // Select default bot if available
      const defaultBot = botsList.find(bot => bot.is_default);
      if (defaultBot) {
        setSelectedBot(defaultBot);
      }
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to fetch bots'
      });
    } finally {
      setLoading(false);
    }
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
