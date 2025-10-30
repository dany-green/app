# Инструкция по использованию testprevyou.json

## Описание

Файл `testprevyou.json` содержит тестовые данные для быстрого наполнения базы данных приложения SLS1 Organizational Platform.

## Содержимое файла

### Пользователи (4 пользователя)
- **Администратор**: `admin@sls1.com` / `admin123`
- **Декоратор**: `maria@sls1.com` / `maria123`
- **Флорист**: `anna@sls1.com` / `anna123`
- **Куратор**: `elena@sls1.com` / `elena123`

### Проекты (3 проекта)
1. **Свадьба в усадьбе** - статус "Создан", с предварительным списком
2. **Корпоратив IT компании** - статус "На согласовании", с предварительным и финальным списками
3. **День рождения в ресторане** - статус "Согласован", все списки заполнены (preliminary, final, dismantling)

### Инвентарь (8 элементов)
- Вазы (стеклянные, керамические, хрустальные)
- Текстиль (скатерти, салфетки)
- Декор (свечи, подсвечники)
- Посуда (тарелки)

### Оборудование (8 элементов)
- Техника (проекторы, звук, микрофоны)
- Мебель (столы, стулья)
- Освещение (LED прожекторы, гирлянды)
- Декор (арки)

---

## Способы загрузки данных

### Способ 1: Через bash скрипт (рекомендуется)

```bash
./load_test_data.sh
```

Скрипт автоматически:
- Очистит текущую базу данных
- Загрузит все данные из `testprevyou.json`
- Выведет статистику и учетные данные

---

### Способ 2: Через curl

```bash
curl -X POST http://localhost:8001/api/load-test-data \
  -H "Content-Type: application/json"
```

Или для production:
```bash
curl -X POST $REACT_APP_BACKEND_URL/api/load-test-data \
  -H "Content-Type: application/json"
```

---

### Способ 3: Через Python

```python
import requests

backend_url = "http://localhost:8001"  # или ваш URL
response = requests.post(f"{backend_url}/api/load-test-data")
print(response.json())
```

---

## API Endpoint

**Endpoint:** `POST /api/load-test-data`

**Описание:** Загружает тестовые данные из файла `testprevyou.json`

**Response:**
```json
{
  "message": "Test data loaded successfully",
  "stats": {
    "users": 4,
    "projects": 3,
    "inventory": 8,
    "equipment": 8
  },
  "credentials": {
    "admin": {"email": "admin@sls1.com", "password": "admin123"},
    "decorator": {"email": "maria@sls1.com", "password": "maria123"},
    "florist": {"email": "anna@sls1.com", "password": "anna123"},
    "curator": {"email": "elena@sls1.com", "password": "elena123"}
  }
}
```

---

## Важные замечания

⚠️ **ВНИМАНИЕ:**
- При загрузке данных **все существующие данные будут удалены**
- Загрузка затрагивает коллекции: users, projects, inventory, equipment, logs
- Убедитесь, что у вас есть резервная копия важных данных перед загрузкой

---

## Редактирование testprevyou.json

Вы можете редактировать файл `testprevyou.json` для добавления своих тестовых данных:

### Структура пользователя:
```json
{
  "id": "unique-id",
  "name": "Имя Фамилия",
  "email": "email@sls1.com",
  "password": "password123",
  "role": "Администратор|Ведущий декоратор|Флорист|Куратор студии",
  "is_active": true
}
```

### Структура проекта:
```json
{
  "id": "unique-id",
  "title": "Название проекта",
  "lead_decorator": "Имя декоратора",
  "project_date": "2025-08-15T14:00:00Z",
  "status": "Создан|На согласовании|Согласован|Сбор проекта|Монтаж|Демонтаж|Разбор",
  "preliminary_list": {"items": []},
  "final_list": {"items": []},
  "dismantling_list": {"items": []},
  "curator_agreement": false,
  "decorator_agreement": false,
  "full_details": {},
  "created_by": "user-id"
}
```

### Структура элемента списка проекта:
```json
{
  "id": "inv-001",
  "name": "Название элемента",
  "category": "Категория",
  "quantity": 10,
  "source": "inventory|equipment|manual",
  "notes": "Примечания (опционально)"
}
```

---

## Автоматическая загрузка при старте (опционально)

Если вы хотите автоматически загружать тестовые данные при каждом старте приложения:

1. Откройте файл `/app/backend/server.py`
2. Найдите событие `@app.on_event("startup")`
3. Добавьте вызов функции загрузки

Пример:
```python
@app.on_event("startup")
async def startup_event():
    # Проверяем, пуста ли база
    user_count = await db.users.count_documents({})
    if user_count == 0:
        await load_test_data()
```

---

## Проверка загруженных данных

После загрузки вы можете проверить данные через:

### MongoDB Shell:
```bash
mongosh sls1_db --eval "db.projects.find().pretty()"
```

### API:
```bash
# Получить JWT токен
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sls1.com","password":"admin123"}' \
  | jq -r '.access_token')

# Получить проекты
curl -X GET http://localhost:8001/api/projects \
  -H "Authorization: Bearer $TOKEN"
```

---

## Troubleshooting

### Ошибка: "Test data file not found"
- Убедитесь, что файл `testprevyou.json` находится в корневой папке `/app/`

### Ошибка: "Failed to load test data"
- Проверьте синтаксис JSON в файле `testprevyou.json`
- Используйте валидатор JSON: https://jsonlint.com/

### Backend не отвечает
- Проверьте статус backend: `sudo supervisorctl status backend`
- Перезапустите: `sudo supervisorctl restart backend`
- Проверьте логи: `tail -f /var/log/supervisor/backend.err.log`

---

## Сохранение текущих данных в файл

Если вы хотите сохранить текущие данные из MongoDB обратно в JSON файл:

```bash
# Экспортировать проекты
mongosh sls1_db --eval "JSON.stringify(db.projects.find().toArray())" --quiet > projects_backup.json

# Экспортировать весь дамп
mongodump --db=sls1_db --out=/app/backup/
```

---

## Быстрый старт для новых разработчиков

```bash
# 1. Загрузить тестовые данные
./load_test_data.sh

# 2. Войти в систему как администратор
# Email: admin@sls1.com
# Password: admin123

# 3. Начать работу с проектами!
```
