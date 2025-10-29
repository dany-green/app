import React, { useState, useEffect } from 'react';
import { equipmentAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, Loader2, Palette, Pencil, Trash2, Image as ImageIcon, Eye } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ImageGallery from '@/components/ImageGallery';

export default function EquipmentPage() {
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [viewingItem, setViewingItem] = useState(null);
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
    loadEquipment();
  }, []);

  const loadEquipment = async () => {
    try {
      const data = await equipmentAPI.getAll();
      setEquipment(data);
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить оборудование',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      if (editingItem) {
        await equipmentAPI.update(editingItem.id, formData);
        toast({ title: 'Оборудование обновлено' });
      } else {
        await equipmentAPI.create(formData);
        toast({ title: 'Оборудование добавлено' });
      }
      setDialogOpen(false);
      resetForm();
      loadEquipment();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error.response?.data?.detail || 'Ошибка сохранения',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить этот элемент оборудования?')) return;
    
    try {
      await equipmentAPI.delete(id);
      toast({ title: 'Элемент удалён' });
      loadEquipment();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось удалить элемент',
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

  const handleViewDetails = (item) => {
    setViewingItem(item);
    setDetailsDialogOpen(true);
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
    equipment.forEach((item) => {
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
  const totalItems = equipment.length;
  const totalQuantity = equipment.reduce((sum, item) => sum + item.total_quantity, 0);
  const categoriesCount = Object.keys(grouped).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900" data-testid="equipment-page-title">
            Оборудование/декор
          </h1>
          <p className="text-gray-600 mt-1">
            Управление оборудованием и декоративными элементами
          </p>
        </div>
        {canManageInventory() && (
          <Dialog open={dialogOpen} onOpenChange={(open) => {
            setDialogOpen(open);
            if (!open) resetForm();
          }}>
            <DialogTrigger asChild>
              <Button className="bg-blue-600 hover:bg-blue-700" data-testid="add-equipment-button">
                <Plus className="mr-2 h-4 w-4" />
                Добавить
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>{editingItem ? 'Редактировать' : 'Добавить'} оборудование</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="category">Категория</Label>
                  <Input
                    id="category"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                    placeholder="Декор"
                  />
                </div>
                <div>
                  <Label htmlFor="name">Название</Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="Название элемента"
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
                    placeholder="🎨"
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

      {/* Info Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg">Категории</CardTitle>
            <CardDescription>Организуйте по категориям</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">{categoriesCount}</div>
            <p className="text-sm text-gray-600 mt-1">Категорий создано</p>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg">Всего единиц</CardTitle>
            <CardDescription>Оборудование в наличии</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">{totalQuantity}</div>
            <p className="text-sm text-gray-600 mt-1">Единиц оборудования</p>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg">Элементов</CardTitle>
            <CardDescription>Различных типов</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">{totalItems}</div>
            <p className="text-sm text-gray-600 mt-1">Типов оборудования</p>
          </CardContent>
        </Card>
      </div>

      {/* Equipment List */}
      {equipment.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <Palette className="h-10 w-10 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold mb-2 text-gray-900">
              Оборудование пока не добавлено
            </h3>
            <p className="text-sm text-gray-600 mb-4 text-center max-w-md">
              Начните добавлять оборудование и декоративные элементы для ваших проектов
            </p>
            {canManageInventory() && (
              <Button className="bg-blue-600 hover:bg-blue-700" onClick={() => setDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Добавить первый элемент
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-6">
          {Object.keys(grouped).map((category) => (
            <div key={category}>
              <h2 className="text-xl font-semibold mb-3">{category}</h2>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {grouped[category].map((item) => (
                  <Card key={item.id} data-testid={`equipment-item-${item.id}`} className="overflow-hidden">
                    {/* Image Preview */}
                    {item.images && item.images.length > 0 && (
                      <div 
                        className="relative h-48 bg-gray-100 cursor-pointer hover:opacity-90 transition-opacity"
                        onClick={() => handleViewDetails(item)}
                      >
                        <img
                          src={`${process.env.REACT_APP_BACKEND_URL}${item.images[0]}`}
                          alt={item.name}
                          className="w-full h-full object-cover"
                        />
                        {item.images.length > 1 && (
                          <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs flex items-center gap-1">
                            <ImageIcon className="h-3 w-3" />
                            +{item.images.length - 1}
                          </div>
                        )}
                      </div>
                    )}
                    
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2 flex-1">
                          {item.visual_marker && <span className="text-2xl">{item.visual_marker}</span>}
                          <div className="flex-1">
                            <CardTitle className="text-lg">{item.name}</CardTitle>
                            {item.description && <CardDescription className="mt-1 line-clamp-2">{item.description}</CardDescription>}
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <Badge variant="secondary" className="text-base">
                          Кол-во: {item.total_quantity}
                        </Badge>
                        
                        <div className="flex gap-2">
                          <Button 
                            size="sm" 
                            variant="outline" 
                            className="flex-1"
                            onClick={() => handleViewDetails(item)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            Детали
                          </Button>
                          {canManageInventory() && (
                            <>
                              <Button size="sm" variant="outline" onClick={() => handleEdit(item)} data-testid={`edit-equipment-${item.id}`}>
                                <Pencil className="h-4 w-4" />
                              </Button>
                              <Button size="sm" variant="outline" onClick={() => handleDelete(item.id)} data-testid={`delete-equipment-${item.id}`}>
                                <Trash2 className="h-4 w-4 text-destructive" />
                              </Button>
                            </>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Details Dialog with Images */}
      <Dialog open={detailsDialogOpen} onOpenChange={setDetailsDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl flex items-center gap-2">
              {viewingItem?.visual_marker && <span className="text-3xl">{viewingItem.visual_marker}</span>}
              {viewingItem?.name}
            </DialogTitle>
            <DialogDescription>
              {viewingItem?.category} • Количество: {viewingItem?.total_quantity}
            </DialogDescription>
          </DialogHeader>
          
          {viewingItem && (
            <Tabs defaultValue="info" className="mt-4">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="info">Информация</TabsTrigger>
                <TabsTrigger value="photos">
                  Фотографии
                  {viewingItem.images && viewingItem.images.length > 0 && (
                    <Badge variant="secondary" className="ml-2">{viewingItem.images.length}</Badge>
                  )}
                </TabsTrigger>
              </TabsList>
              
              <TabsContent value="info" className="space-y-4 mt-4">
                <div>
                  <Label className="text-sm font-semibold">Название</Label>
                  <p className="mt-1 text-base">{viewingItem.name}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-semibold">Категория</Label>
                  <p className="mt-1 text-base">{viewingItem.category}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-semibold">Количество</Label>
                  <p className="mt-1 text-base">{viewingItem.total_quantity} ед.</p>
                </div>
                
                {viewingItem.visual_marker && (
                  <div>
                    <Label className="text-sm font-semibold">Визуальная метка</Label>
                    <p className="mt-1 text-3xl">{viewingItem.visual_marker}</p>
                  </div>
                )}
                
                {viewingItem.description && (
                  <div>
                    <Label className="text-sm font-semibold">Описание</Label>
                    <p className="mt-1 text-base">{viewingItem.description}</p>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="photos" className="mt-4">
                <ImageGallery
                  itemId={viewingItem.id}
                  images={viewingItem.images || []}
                  onImagesChange={loadEquipment}
                  canEdit={canManageInventory()}
                  apiService={equipmentAPI}
                />
              </TabsContent>
            </Tabs>
          )}
          
          <DialogFooter className="mt-4">
            {canManageInventory() && (
              <Button onClick={() => {
                setDetailsDialogOpen(false);
                setTimeout(() => handleEdit(viewingItem), 100);
              }}>
                <Pencil className="h-4 w-4 mr-2" />
                Редактировать
              </Button>
            )}
            <Button variant="outline" onClick={() => setDetailsDialogOpen(false)}>
              Закрыть
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
