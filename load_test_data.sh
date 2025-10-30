#!/bin/bash

# Скрипт для загрузки тестовых данных из testprevyou.json

BACKEND_URL="${REACT_APP_BACKEND_URL:-http://localhost:8001}"
API_URL="${BACKEND_URL}/api"

echo "🔄 Загрузка тестовых данных из testprevyou.json..."
echo "📡 Backend URL: $API_URL"
echo ""

# Загрузка тестовых данных
response=$(curl -s -X POST "${API_URL}/load-test-data" \
  -H "Content-Type: application/json")

# Проверка ответа
if echo "$response" | grep -q "Test data loaded successfully"; then
    echo "✅ Тестовые данные успешно загружены!"
    echo ""
    echo "📊 Статистика:"
    echo "$response" | jq -r '.stats | to_entries | .[] | "  \(.key): \(.value)"' 2>/dev/null || echo "$response" | grep -o '"stats":[^}]*}' 
    echo ""
    echo "🔑 Учетные данные для входа:"
    echo "  Администратор:  admin@sls1.com / admin123"
    echo "  Декоратор:      maria@sls1.com / maria123"
    echo "  Флорист:        anna@sls1.com / anna123"
    echo "  Куратор:        elena@sls1.com / elena123"
else
    echo "❌ Ошибка при загрузке данных:"
    echo "$response"
    exit 1
fi
