import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Plus, Palette } from 'lucide-react';

export default function EquipmentPage() {
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
        <Button className="bg-blue-600 hover:bg-blue-700" data-testid="add-equipment-button">
          <Plus className="mr-2 h-4 w-4" />
          Добавить
        </Button>
      </div>

      {/* Empty State */}
      <Card className="border-gray-200">
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
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="mr-2 h-4 w-4" />
            Добавить первый элемент
          </Button>
        </CardContent>
      </Card>

      {/* Info Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg">Категории</CardTitle>
            <CardDescription>Организуйте по категориям</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">0</div>
            <p className="text-sm text-gray-600 mt-1">Категорий создано</p>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg">Всего единиц</CardTitle>
            <CardDescription>Оборудование в наличии</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">0</div>
            <p className="text-sm text-gray-600 mt-1">Единиц оборудования</p>
          </CardContent>
        </Card>

        <Card className="border-gray-200">
          <CardHeader>
            <CardTitle className="text-lg">В использовании</CardTitle>
            <CardDescription>Активно используется</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">0</div>
            <p className="text-sm text-gray-600 mt-1">Единиц в проектах</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
