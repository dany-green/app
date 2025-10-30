import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectsAPI, inventoryAPI, equipmentAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ArrowLeft, Plus, Loader2, Calendar, User, Package, ListChecks } from 'lucide-react';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { useToast } from '@/hooks/use-toast';

export default function ProjectDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAdmin } = useAuth();
  const { toast } = useToast();

  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentList, setCurrentList] = useState('preliminary'); // preliminary, final, dismantling
  const [addMode, setAddMode] = useState('select'); // select or manual
  
  // Для выбора из существующих
  const [inventory, setInventory] = useState([]);
  const [equipment, setEquipment] = useState([]);
  const [selectedSource, setSelectedSource] = useState('inventory'); // inventory or equipment
  const [selectedItem, setSelectedItem] = useState('');
  const [quantity, setQuantity] = useState(1);

  // Для ручного ввода
  const [manualData, setManualData] = useState({
    name: '',
    category: '',
    quantity: 1,
    notes: ''
  });

  useEffect(() => {
    loadProject();
    loadInventory();
    loadEquipment();
  }, [id]);

  const loadProject = async () => {
    try {
      const data = await projectsAPI.getById(id);
      setProject(data);
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить проект',
        variant: 'destructive',
      });
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const loadInventory = async () => {
    try {
      const data = await inventoryAPI.getAll();
      setInventory(data);
    } catch (error) {
      console.error('Failed to load inventory:', error);
    }
  };

  const loadEquipment = async () => {
    try {
      const data = await equipmentAPI.getAll();
      setEquipment(data);
    } catch (error) {
      console.error('Failed to load equipment:', error);
    }
  };

  const openAddDialog = (listType) => {
    setCurrentList(listType);
    setDialogOpen(true);
    resetForm();
  };

  const resetForm = () => {
    setAddMode('select');
    setSelectedSource('inventory');
    setSelectedItem('');
    setQuantity(1);
    setManualData({
      name: '',
      category: '',
      quantity: 1,
      notes: ''
    });
  };

  const handleAddItem = async () => {
    try {
      let itemData;

      if (addMode === 'select') {
        const source = selectedSource === 'inventory' ? inventory : equipment;
        const item = source.find(i => i.id === selectedItem);
        
        if (!item) {
          toast({
            title: 'Ошибка',
            description: 'Выберите элемент',
            variant: 'destructive',
          });
          return;
        }

        itemData = {
          id: item.id,
          name: item.name,
          category: item.category,
          quantity: quantity,
          source: selectedSource
        };
      } else {
        if (!manualData.name) {
          toast({
            title: 'Ошибка',
            description: 'Введите название',
            variant: 'destructive',
          });
          return;
        }

        itemData = {
          ...manualData,
          source: 'manual'
        };
      }

      // Определяем поле для обновления
      const listField = currentList === 'preliminary' ? 'preliminary_list' 
                      : currentList === 'final' ? 'final_list' 
                      : 'dismantling_list';

      // Получаем текущий список
      const currentListData = project[listField] || { items: [] };
      const updatedItems = [...(currentListData.items || []), itemData];

      // Обновляем проект
      const updateData = {
        [listField]: { items: updatedItems }
      };

      await projectsAPI.update(id, updateData);
      
      toast({
        title: 'Успешно',
        description: 'Элемент добавлен в список',
      });

      setDialogOpen(false);
      loadProject();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error.response?.data?.detail || 'Не удалось добавить элемент',
        variant: 'destructive',
      });
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Создан':
        return 'bg-blue-500';
      case 'На согласовании':
        return 'bg-yellow-500';
      case 'Согласован':
        return 'bg-green-500';
      case 'Сбор проекта':
        return 'bg-purple-500';
      case 'Монтаж':
        return 'bg-orange-500';
      case 'Демонтаж':
        return 'bg-red-500';
      case 'Разбор':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  const renderList = (listType, listData) => {
    const items = listData?.items || [];
    const listTitle = listType === 'preliminary' ? 'Предварительный список'
                    : listType === 'final' ? 'Финальный список'
                    : 'Список демонтажа';

    return (
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>{listTitle}</CardTitle>
              <CardDescription>
                {items.length === 0 ? 'Список пуст' : `Элементов в списке: ${items.length}`}
              </CardDescription>
            </div>
            {isAdmin() && (
              <Button onClick={() => openAddDialog(listType)}>
                <Plus className="mr-2 h-4 w-4" />
                Добавить элемент
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {items.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <ListChecks className="h-16 w-16 mx-auto mb-4 opacity-50" />
              <p>Элементы не добавлены</p>
            </div>
          ) : (
            <div className="space-y-2">
              {items.map((item, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <Package className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="font-medium">{item.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {item.category && `${item.category} • `}
                          Количество: {item.quantity}
                          {item.notes && ` • ${item.notes}`}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          Источник: {item.source === 'inventory' ? 'Инвентарь' 
                                   : item.source === 'equipment' ? 'Оборудование/декор' 
                                   : 'Ручной ввод'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!project) {
    return null;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => navigate('/')}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight">{project.title}</h1>
          <p className="text-muted-foreground">Детальная информация о проекте</p>
        </div>
        <Badge className={getStatusColor(project.status)}>
          {project.status}
        </Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Информация о проекте</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-2">
          <div className="flex items-center gap-2">
            <User className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-sm text-muted-foreground">Ведущий декоратор</p>
              <p className="font-medium">{project.lead_decorator}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-sm text-muted-foreground">Дата мероприятия</p>
              <p className="font-medium">
                {format(new Date(project.project_date), 'dd MMMM yyyy, HH:mm', { locale: ru })}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="preliminary" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="preliminary">Предварительный список</TabsTrigger>
          <TabsTrigger value="final">Финальный список</TabsTrigger>
          <TabsTrigger value="dismantling">Список демонтажа</TabsTrigger>
        </TabsList>

        <TabsContent value="preliminary">
          {renderList('preliminary', project.preliminary_list)}
        </TabsContent>

        <TabsContent value="final">
          {renderList('final', project.final_list)}
        </TabsContent>

        <TabsContent value="dismantling">
          {renderList('dismantling', project.dismantling_list)}
        </TabsContent>
      </Tabs>

      {/* Диалог добавления элемента */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Добавить элемент в список</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label>Способ добавления</Label>
              <Select value={addMode} onValueChange={setAddMode}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="select">Выбрать из существующих</SelectItem>
                  <SelectItem value="manual">Ручной ввод</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {addMode === 'select' ? (
              <>
                <div>
                  <Label>Источник</Label>
                  <Select value={selectedSource} onValueChange={setSelectedSource}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="inventory">Инвентарь</SelectItem>
                      <SelectItem value="equipment">Оборудование/декор</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Элемент</Label>
                  <Select value={selectedItem} onValueChange={setSelectedItem}>
                    <SelectTrigger>
                      <SelectValue placeholder="Выберите элемент" />
                    </SelectTrigger>
                    <SelectContent>
                      {(selectedSource === 'inventory' ? inventory : equipment).map((item) => (
                        <SelectItem key={item.id} value={item.id}>
                          {item.name} - {item.category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label>Количество</Label>
                  <Input
                    type="number"
                    min="1"
                    value={quantity}
                    onChange={(e) => setQuantity(parseInt(e.target.value))}
                  />
                </div>
              </>
            ) : (
              <>
                <div>
                  <Label>Название</Label>
                  <Input
                    value={manualData.name}
                    onChange={(e) => setManualData({ ...manualData, name: e.target.value })}
                    placeholder="Введите название"
                  />
                </div>

                <div>
                  <Label>Категория</Label>
                  <Input
                    value={manualData.category}
                    onChange={(e) => setManualData({ ...manualData, category: e.target.value })}
                    placeholder="Введите категорию"
                  />
                </div>

                <div>
                  <Label>Количество</Label>
                  <Input
                    type="number"
                    min="1"
                    value={manualData.quantity}
                    onChange={(e) => setManualData({ ...manualData, quantity: parseInt(e.target.value) })}
                  />
                </div>

                <div>
                  <Label>Примечания</Label>
                  <Input
                    value={manualData.notes}
                    onChange={(e) => setManualData({ ...manualData, notes: e.target.value })}
                    placeholder="Дополнительная информация"
                  />
                </div>
              </>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogOpen(false)}>
              Отмена
            </Button>
            <Button onClick={handleAddItem}>
              Добавить
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
