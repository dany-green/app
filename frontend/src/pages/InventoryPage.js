import React, { useState, useEffect } from 'react';
import { inventoryAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, Loader2, Package as PackageIcon, Pencil, Trash2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

export default function InventoryPage() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const { canManageInventory } = useAuth();
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    category: '',
    name: '',
    total_quantity: 0,
    visual_marker: '',
    description: '',
  });

  useEffect(() => {
    loadInventory();
  }, []);

  const loadInventory = async () => {
    try {
      const data = await inventoryAPI.getAll();
      setInventory(data);
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить инвентарь',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      if (editingItem) {
        await inventoryAPI.update(editingItem.id, formData);
        toast({ title: 'Инвентарь обновлён' });
      } else {
        await inventoryAPI.create(formData);
        toast({ title: 'Предмет добавлен' });
      }
      setDialogOpen(false);
      resetForm();
      loadInventory();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error.response?.data?.detail || 'Ошибка сохранения',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить этот предмет?')) return;
    
    try {
      await inventoryAPI.delete(id);
      toast({ title: 'Предмет удалён' });
      loadInventory();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось удалить предмет',
        variant: 'destructive',
      });
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setFormData({
      category: item.category,
      name: item.name,
      total_quantity: item.total_quantity,
      visual_marker: item.visual_marker || '',
      description: item.description || '',
    });
    setDialogOpen(true);
  };

  const resetForm = () => {
    setFormData({
      category: '',
      name: '',
      total_quantity: 0,
      visual_marker: '',
      description: '',
    });
    setEditingItem(null);
  };

  const groupByCategory = () => {
    const grouped = {};
    inventory.forEach((item) => {
      if (!grouped[item.category]) {
        grouped[item.category] = [];
      }
      grouped[item.category].push(item);
    });
    return grouped;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  const grouped = groupByCategory();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight" data-testid="inventory-page-title">Инвентарь</h1>
          <p className="text-muted-foreground">Управление оборудованием и материалами</p>
        </div>
        {canManageInventory() && (
          <Dialog open={dialogOpen} onOpenChange={(open) => {
            setDialogOpen(open);
            if (!open) resetForm();
          }}>
            <DialogTrigger asChild>
              <Button data-testid="add-inventory-button">
                <Plus className="mr-2 h-4 w-4" />
                Добавить предмет
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingItem ? 'Редактировать' : 'Добавить'} предмет</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="category">Категория</Label>
                  <Input
                    id="category"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    placeholder="Вазы"
                  />
                </div>
                <div>
                  <Label htmlFor="name">Название</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Ваза стеклянная"
                  />
                </div>
                <div>
                  <Label htmlFor="quantity">Количество</Label>
                  <Input
                    id="quantity"
                    type="number"
                    value={formData.total_quantity}
                    onChange={(e) => setFormData({ ...formData, total_quantity: parseInt(e.target.value) || 0 })}
                  />
                </div>
                <div>
                  <Label htmlFor="marker">Визуальная метка (emoji)</Label>
                  <Input
                    id="marker"
                    value={formData.visual_marker}
                    onChange={(e) => setFormData({ ...formData, visual_marker: e.target.value })}
                    placeholder="🔴"
                  />
                </div>
                <div>
                  <Label htmlFor="description">Описание</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Дополнительная информация"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button onClick={handleSave}>Сохранить</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>

      {inventory.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <PackageIcon className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Инвентарь пуст</h3>
            <p className="text-sm text-muted-foreground">Добавьте первый предмет</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {Object.keys(grouped).map((category) => (
            <div key={category}>
              <h2 className="text-xl font-semibold mb-3">{category}</h2>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {grouped[category].map((item) => (
                  <Card key={item.id} data-testid={`inventory-item-${item.id}`}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          {item.visual_marker && <span className="text-2xl">{item.visual_marker}</span>}
                          <div>
                            <CardTitle className="text-lg">{item.name}</CardTitle>
                            {item.description && <CardDescription className="mt-1">{item.description}</CardDescription>}
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <Badge variant="secondary" className="text-base">
                          Кол-во: {item.total_quantity}
                        </Badge>
                        {canManageInventory() && (
                          <div className="flex gap-2">
                            <Button size="sm" variant="outline" onClick={() => handleEdit(item)} data-testid={`edit-inventory-${item.id}`}>
                              <Pencil className="h-4 w-4" />
                            </Button>
                            <Button size="sm" variant="outline" onClick={() => handleDelete(item.id)} data-testid={`delete-inventory-${item.id}`}>
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
