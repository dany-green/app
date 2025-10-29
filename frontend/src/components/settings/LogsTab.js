import React, { useState, useEffect } from 'react';
import { logsAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, FileText, Trash2, RefreshCw, AlertCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { Alert, AlertDescription } from '@/components/ui/alert';

export default function LogsTab() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cleaningUp, setCleaningUp] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    setLoading(true);
    try {
      const data = await logsAPI.getAll(500); // Последние 500 записей
      setLogs(data);
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить логи',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCleanup = async () => {
    if (!window.confirm('Удалить все логи старше 30 дней?')) return;
    
    setCleaningUp(true);
    try {
      const response = await logsAPI.cleanup();
      toast({
        title: 'Успешно',
        description: `Удалено записей: ${response.deleted_count}`,
      });
      loadLogs();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось очистить логи',
        variant: 'destructive',
      });
    } finally {
      setCleaningUp(false);
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'CREATE':
        return 'bg-green-500';
      case 'UPDATE':
        return 'bg-blue-500';
      case 'DELETE':
        return 'bg-red-500';
      case 'UPLOAD_IMAGE':
        return 'bg-purple-500';
      case 'DELETE_IMAGE':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getActionText = (action) => {
    switch (action) {
      case 'CREATE':
        return 'Создание';
      case 'UPDATE':
        return 'Обновление';
      case 'DELETE':
        return 'Удаление';
      case 'UPLOAD_IMAGE':
        return 'Загрузка фото';
      case 'DELETE_IMAGE':
        return 'Удаление фото';
      default:
        return action;
    }
  };

  const getEntityTypeText = (entityType) => {
    switch (entityType) {
      case 'USER':
        return 'Пользователь';
      case 'PROJECT':
        return 'Проект';
      case 'INVENTORY':
        return 'Инвентарь';
      case 'EQUIPMENT':
        return 'Оборудование';
      default:
        return entityType;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Логи активности</CardTitle>
            <CardDescription>История всех действий пользователей в системе</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={loadLogs} disabled={loading}>
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Обновить
            </Button>
            <Button
              variant="outline"
              onClick={handleCleanup}
              disabled={cleaningUp}
            >
              {cleaningUp ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Очистка...
                </>
              ) : (
                <>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Очистить старые
                </>
              )}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Alert className="mb-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Логи автоматически удаляются через 30 дней с момента создания.
          </AlertDescription>
        </Alert>

        {logs.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">Нет записей в логах</p>
          </div>
        ) : (
          <div className="space-y-2">
            {logs.map((log) => (
              <div
                key={log.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center gap-4 flex-1">
                  <Badge className={`${getActionColor(log.action)} text-white`}>
                    {getActionText(log.action)}
                  </Badge>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{log.user_name}</span>
                      <span className="text-muted-foreground">•</span>
                      <span className="text-sm text-muted-foreground">
                        {getEntityTypeText(log.entity_type)}
                      </span>
                    </div>
                    
                    {log.details && Object.keys(log.details).length > 0 && (
                      <div className="text-sm text-muted-foreground mt-1">
                        {log.details.name && <span>Название: {log.details.name}</span>}
                        {log.details.category && <span> • Категория: {log.details.category}</span>}
                        {log.details.filename && <span> • Файл: {log.details.filename}</span>}
                        {log.details.user_name && <span> • Пользователь: {log.details.user_name}</span>}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="text-sm text-muted-foreground text-right">
                  <div>{format(new Date(log.timestamp), 'dd MMM yyyy', { locale: ru })}</div>
                  <div className="text-xs">{format(new Date(log.timestamp), 'HH:mm:ss', { locale: ru })}</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {logs.length > 0 && (
          <div className="mt-4 text-sm text-muted-foreground text-center">
            Показано {logs.length} записей
          </div>
        )}
      </CardContent>
    </Card>
  );
}
