import React, { useState } from 'react';
import { authAPI } from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Database, Users, Package, Wrench, FolderOpen, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

export default function TestDataPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const { toast } = useToast();

  const loadTestData = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await authAPI.loadTestData();
      setResult({
        success: true,
        data: response
      });

      toast({
        title: 'Успешно!',
        description: 'Тестовые данные загружены',
      });
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.detail || error.message
      });

      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить тестовые данные',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Тестовые данные</h1>
        <p className="text-muted-foreground mt-2">
          Быстрая загрузка тестовых данных для разработки и тестирования
        </p>
      </div>

      <Alert>
        <Database className="h-4 w-4" />
        <AlertDescription>
          ⚠️ <strong>Внимание:</strong> При загрузке тестовых данных все текущие данные в базе будут удалены!
        </AlertDescription>
      </Alert>

      <Card>
        <CardHeader>
          <CardTitle>Загрузить тестовые данные</CardTitle>
          <CardDescription>
            Файл testprevyou.json содержит готовые данные для быстрого старта
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3">
              <Users className="h-5 w-5 text-blue-500 mt-1" />
              <div>
                <p className="font-medium">4 пользователя</p>
                <p className="text-sm text-muted-foreground">
                  Администратор, декоратор, флорист, куратор
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <FolderOpen className="h-5 w-5 text-green-500 mt-1" />
              <div>
                <p className="font-medium">3 проекта</p>
                <p className="text-sm text-muted-foreground">
                  С разными статусами и заполненными списками
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Package className="h-5 w-5 text-purple-500 mt-1" />
              <div>
                <p className="font-medium">8 элементов инвентаря</p>
                <p className="text-sm text-muted-foreground">
                  Вазы, текстиль, декор, посуда
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Wrench className="h-5 w-5 text-orange-500 mt-1" />
              <div>
                <p className="font-medium">8 элементов оборудования</p>
                <p className="text-sm text-muted-foreground">
                  Техника, мебель, освещение
                </p>
              </div>
            </div>
          </div>

          <Button 
            onClick={loadTestData} 
            disabled={loading}
            className="w-full"
            size="lg"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Загрузка данных...
              </>
            ) : (
              <>
                <Database className="mr-2 h-4 w-4" />
                Загрузить тестовые данные
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <Card className={result.success ? 'border-green-500' : 'border-red-500'}>
          <CardHeader>
            <div className="flex items-center gap-2">
              {result.success ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <XCircle className="h-5 w-5 text-red-500" />
              )}
              <CardTitle>
                {result.success ? 'Данные загружены' : 'Ошибка загрузки'}
              </CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            {result.success ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-2xl font-bold text-blue-600">
                      {result.data.stats.users}
                    </p>
                    <p className="text-sm text-muted-foreground">Пользователей</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-2xl font-bold text-green-600">
                      {result.data.stats.projects}
                    </p>
                    <p className="text-sm text-muted-foreground">Проектов</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <p className="text-2xl font-bold text-purple-600">
                      {result.data.stats.inventory}
                    </p>
                    <p className="text-sm text-muted-foreground">Инвентарь</p>
                  </div>
                  <div className="text-center p-4 bg-orange-50 rounded-lg">
                    <p className="text-2xl font-bold text-orange-600">
                      {result.data.stats.equipment}
                    </p>
                    <p className="text-sm text-muted-foreground">Оборудование</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <p className="font-medium">Учетные данные для входа:</p>
                  <div className="grid gap-2 font-mono text-sm">
                    <div className="p-3 bg-gray-50 rounded">
                      <span className="text-blue-600 font-semibold">Администратор:</span>{' '}
                      {result.data.credentials.admin.email} / {result.data.credentials.admin.password}
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <span className="text-green-600 font-semibold">Декоратор:</span>{' '}
                      {result.data.credentials.decorator.email} / {result.data.credentials.decorator.password}
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <span className="text-purple-600 font-semibold">Флорист:</span>{' '}
                      {result.data.credentials.florist.email} / {result.data.credentials.florist.password}
                    </div>
                    <div className="p-3 bg-gray-50 rounded">
                      <span className="text-orange-600 font-semibold">Куратор:</span>{' '}
                      {result.data.credentials.curator.email} / {result.data.credentials.curator.password}
                    </div>
                  </div>
                </div>

                <Alert>
                  <AlertDescription>
                    💡 Данные успешно загружены! Вы можете войти в систему используя любую учетную запись выше.
                  </AlertDescription>
                </Alert>
              </div>
            ) : (
              <div className="text-red-600">
                <p className="font-medium">Ошибка:</p>
                <p className="text-sm mt-1">{result.error}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Дополнительная информация</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="font-medium mb-2">Структура тестовых данных:</p>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground ml-4">
              <li>Проект "Свадьба в усадьбе" - статус "Создан", с предварительным списком</li>
              <li>Проект "Корпоратив IT компании" - статус "На согласовании", с предварительным и финальным списками</li>
              <li>Проект "День рождения в ресторане" - статус "Согласован", все списки заполнены</li>
            </ul>
          </div>

          <div>
            <p className="font-medium mb-2">Альтернативные способы загрузки:</p>
            <div className="bg-gray-900 text-gray-100 p-4 rounded font-mono text-xs overflow-x-auto">
              <p className="text-green-400"># Через bash скрипт</p>
              <p>./load_test_data.sh</p>
              <br />
              <p className="text-green-400"># Через curl</p>
              <p>curl -X POST http://localhost:8001/api/load-test-data</p>
            </div>
          </div>

          <Alert>
            <AlertDescription>
              📄 Подробная документация доступна в файле <code className="text-xs bg-gray-200 px-1 py-0.5 rounded">TESTDATA_GUIDE.md</code>
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    </div>
  );
}
