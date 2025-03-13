import { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { BotService } from '../../services';
import { Bot } from '../../types/chat';
import { useToast } from '../../hooks/use-toast';

interface BotSelectionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreateBot: (roleType: string, botName: string, botId?: string) => void;
}

const BotSelectionDialog = ({ 
  open, 
  onOpenChange, 
  onCreateBot
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

  const handleSubmit = () => {
    if (selectedBot) {
      onCreateBot(selectedBot.role_type, selectedBot.name, selectedBot.id);
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange} data-testid="bot-selection-dialog">
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Select Bot</DialogTitle>
          <DialogDescription>
            Choose a bot for your new conversation
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          {loading ? (
            <div className="text-center py-4">Loading bots...</div>
          ) : (
            <div className="space-y-4">
              {bots.map((bot) => (
                <div
                  key={bot.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedBot?.id === bot.id ? 'border-primary bg-primary/5' : 'hover:bg-accent'
                  }`}
                  onClick={() => setSelectedBot(bot)}
                  data-testid={`bot-option-${bot.id}`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium">{bot.name}</h4>
                      <p className="text-sm text-muted-foreground">{bot.role_type}</p>
                    </div>
                    {bot.is_default && (
                      <Badge variant="secondary">Default</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <DialogFooter>
          <Button 
            onClick={handleSubmit}
            disabled={!selectedBot || loading}
            data-testid="create-bot-button"
          >
            Create Conversation
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default BotSelectionDialog;
