import React, { useState, useEffect } from 'react';
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from '../ui/dialog';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Label } from '../ui/label';
import { Switch } from '../ui/switch';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Pencil, Trash, Plus } from 'lucide-react';
import { Bot } from '../../types/chat';
import { BotService } from '../../services';
import { useToast } from '../../hooks/use-toast';

interface BotManagementDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const BotManagementDialog = ({ 
  open, 
  onOpenChange
}: BotManagementDialogProps) => {
  const [bots, setBots] = useState<Bot[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingBot, setEditingBot] = useState<Bot | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [name, setName] = useState('');
  const [roleType, setRoleType] = useState('custom');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [isDefault, setIsDefault] = useState(false);
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

  const handleCreateBot = () => {
    setEditingBot(null);
    setName('');
    setRoleType('custom');
    setSystemPrompt('');
    setIsDefault(false);
    setIsCreating(true);
  };

  const handleEditBot = (bot: Bot) => {
    setEditingBot(bot);
    setName(bot.name);
    setRoleType(bot.role_type);
    setSystemPrompt(bot.system_prompt);
    setIsDefault(bot.is_default);
    setIsCreating(true);
  };

  const handleDeleteBot = async (bot: Bot) => {
    if (bot.is_default) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Cannot delete the default bot'
      });
      return;
    }

    if (confirm(`Are you sure you want to delete the bot "${bot.name}"?`)) {
      setLoading(true);
      try {
        const success = await BotService.deleteBot(bot.id);
        if (success) {
          toast({
            title: 'Success',
            description: `Bot "${bot.name}" deleted successfully`
          });
          fetchBots();
        } else {
          toast({
            variant: 'destructive',
            title: 'Error',
            description: 'Failed to delete bot'
          });
        }
      } catch (error) {
        toast({
          variant: 'destructive',
          title: 'Error',
          description: 'Failed to delete bot'
        });
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSaveBot = async () => {
    if (!name.trim() || !systemPrompt.trim()) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Bot name and system prompt are required'
      });
      return;
    }

    setLoading(true);
    try {
      if (editingBot) {
        // Update existing bot
        const updatedBot = await BotService.updateBot(
          editingBot.id,
          name,
          roleType,
          systemPrompt,
          isDefault
        );
        if (updatedBot) {
          toast({
            title: 'Success',
            description: `Bot "${name}" updated successfully`
          });
        }
      } else {
        // Create new bot
        const newBot = await BotService.createBot(
          name,
          roleType,
          systemPrompt,
          isDefault
        );
        if (newBot) {
          toast({
            title: 'Success',
            description: `Bot "${name}" created successfully`
          });
        }
      }
      setIsCreating(false);
      fetchBots();
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Error',
        description: 'Failed to save bot'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setIsCreating(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange} data-testid="bot-management-dialog">
      <DialogContent className="sm:max-w-[700px]">
        <DialogHeader>
          <DialogTitle>Bot Management</DialogTitle>
          <DialogDescription>
            Create and manage bots with custom system prompts
          </DialogDescription>
        </DialogHeader>
        
        {isCreating ? (
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="bot-name" className="text-right">
                Bot Name
              </Label>
              <Input
                id="bot-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="col-span-3"
                placeholder="Enter bot name"
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="role-type" className="text-right">
                Role Type
              </Label>
              <Input
                id="role-type"
                value={roleType}
                onChange={(e) => setRoleType(e.target.value)}
                className="col-span-3"
                placeholder="Enter role type (e.g., custom, customer_service)"
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="system-prompt" className="text-right">
                System Prompt
              </Label>
              <Textarea
                id="system-prompt"
                value={systemPrompt}
                onChange={(e) => setSystemPrompt(e.target.value)}
                className="col-span-3"
                placeholder="Enter system prompt"
                rows={6}
              />
            </div>
            
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="is-default" className="text-right">
                Default Bot
              </Label>
              <div className="flex items-center space-x-2 col-span-3">
                <Switch
                  id="is-default"
                  checked={isDefault}
                  onCheckedChange={setIsDefault}
                />
                <Label htmlFor="is-default">
                  {isDefault ? 'Yes' : 'No'}
                </Label>
              </div>
            </div>
            
            <DialogFooter>
              <Button variant="outline" onClick={handleCancel} disabled={loading}>
                Cancel
              </Button>
              <Button onClick={handleSaveBot} disabled={loading}>
                {editingBot ? 'Update' : 'Create'}
              </Button>
            </DialogFooter>
          </div>
        ) : (
          <>
            <div className="flex justify-end mb-4">
              <Button onClick={handleCreateBot} disabled={loading}>
                <Plus className="h-4 w-4 mr-2" />
                New Bot
              </Button>
            </div>
            
            <div className="border rounded-md">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Role Type</TableHead>
                    <TableHead>Default</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {bots.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-4">
                        {loading ? 'Loading...' : 'No bots found. Create your first bot!'}
                      </TableCell>
                    </TableRow>
                  ) : (
                    bots.map((bot) => (
                      <TableRow key={bot.id}>
                        <TableCell className="font-medium">{bot.name}</TableCell>
                        <TableCell>{bot.role_type}</TableCell>
                        <TableCell>{bot.is_default ? 'Yes' : 'No'}</TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end space-x-2">
                            <Button
                              variant="outline"
                              size="icon"
                              onClick={() => handleEditBot(bot)}
                              disabled={loading}
                            >
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="icon"
                              onClick={() => handleDeleteBot(bot)}
                              disabled={loading || bot.is_default}
                            >
                              <Trash className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default BotManagementDialog;
