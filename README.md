# SLS1 - Организационная платформа студии

Полнофункциональное веб-приложение для управления проектами, инвентарем и пользователями студии.

## 🚀 Возможности

### ✅ Система аутентификации
- **JWT токены** для безопасной аутентификации
- **4 роли пользователей**:
  - **Администратор** - полный доступ ко всем функциям
  - **Ведущий декоратор** - создание и управление проектами
  - **Куратор студии** - редактирование финальных списков, управление инвентарем
  - **Флорист** - создание предварительных списков

### 📊 Управление проектами
- Создание и редактирование проектов
- **Статусы проектов**:
  - Создан
  - На согласовании
  - Согласован
  - Сбор проекта
  - Монтаж
  - Демонтаж
  - Разбор
- **Трехфазный процесс работы** (в разработке):
  - Предварительный список
  - Финальный список
  - Список демонтажа

### 📦 Управление инвентарем
- Категоризация предметов
- Отслеживание количества
- Визуальные маркеры (emoji)
- Описания предметов

### 👥 Админ-панель
- Управление пользователями
- Создание и удаление пользователей
- Просмотр активности (логи)

### 🎨 Современный UI
- **shadcn/ui компоненты**
- Адаптивный дизайн
- Темная/светлая тема (готово к использованию)

## 🛠️ Технологии

### Backend
- **FastAPI** - современный Python веб-фреймворк
- **MongoDB** с Motor (async драйвер)
- **JWT Authentication** (python-jose + passlib)
- **Pydantic** для валидации данных

### Frontend
- **React 19**
- **React Router** для навигации
- **shadcn/ui** компоненты
- **Tailwind CSS**
- **Axios** для API запросов
- **date-fns** для работы с датами

## 📋 Установка и запуск

### Предварительные требования
- Python 3.8+
- Node.js 18+
- MongoDB

### Backend
```bash
cd /app/backend
pip install -r requirements.txt
```

### Frontend
```bash
cd /app/frontend
yarn install
```

### Запуск
Оба сервиса управляются через Supervisor:
```bash
sudo supervisorctl restart all
sudo supervisorctl status
```

## 🔑 Первый запуск

### Инициализация базы данных
```bash
curl -X POST http://localhost:8001/api/init
```

Это создаст:
- Администратора по умолчанию
- Примеры инвентаря

### Учетные данные администратора
```
Email: admin@sls1.com
Пароль: admin123
```

## 📚 API Документация

### Аутентификация

#### Вход в систему
```bash
POST /api/auth/login
{
  "email": "admin@sls1.com",
  "password": "admin123"
}
```

#### Получение текущего пользователя
```bash
GET /api/auth/me
Authorization: Bearer <token>
```

### Проекты

#### Получить все проекты
```bash
GET /api/projects
Authorization: Bearer <token>
```

#### Создать проект
```bash
POST /api/projects
Authorization: Bearer <token>
{
  "title": "Свадьба Иванов",
  "lead_decorator": "Иван Иванов",
  "project_date": "2025-12-31T18:00:00Z",
  "full_details": {}
}
```

#### Обновить проект
```bash
PATCH /api/projects/{project_id}
Authorization: Bearer <token>
{
  "status": "Согласован"
}
```

### Инвентарь

#### Получить весь инвентарь
```bash
GET /api/inventory
Authorization: Bearer <token>
```

#### Создать предмет инвентаря (Куратор/Админ)
```bash
POST /api/inventory
Authorization: Bearer <token>
{
  "category": "Вазы",
  "name": "Ваза стеклянная большая",
  "total_quantity": 10,
  "visual_marker": "🔴"
}
```

### Пользователи (только Админ)

#### Получить всех пользователей
```bash
GET /api/users
Authorization: Bearer <token>
```

#### Создать пользователя
```bash
POST /api/auth/register
Authorization: Bearer <token>
{
  "name": "Мария Петрова",
  "email": "maria@sls1.com",
  "password": "password123",
  "role": "Флорист"
}
```

## 🔄 Структура базы данных

### Collections

#### users
```json
{
  "id": "uuid",
  "name": "string",
  "email": "string",
  "password_hash": "string",
  "role": "enum: Администратор | Ведущий декоратор | Флорист | Куратор студии",
  "is_active": "boolean",
  "created_at": "datetime",
  "last_login": "datetime"
}
```

#### projects
```json
{
  "id": "uuid",
  "title": "string",
  "lead_decorator": "string",
  "project_date": "datetime",
  "status": "enum: Создан | На согласовании | ...",
  "preliminary_list": "object",
  "final_list": "object",
  "dismantling_list": "object",
  "curator_agreement": "boolean",
  "decorator_agreement": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime",
  "created_by": "string"
}
```

#### inventory
```json
{
  "id": "uuid",
  "category": "string",
  "name": "string",
  "total_quantity": "number",
  "visual_marker": "string",
  "description": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

#### logs
```json
{
  "id": "uuid",
  "user_id": "string",
  "user_name": "string",
  "action": "string",
  "entity_type": "string",
  "entity_id": "string",
  "details": "object",
  "timestamp": "datetime"
}
```

## 🧪 Тестирование

### Backend
```bash
# Тест базового API
curl http://localhost:8001/api/

# Тест инициализации
curl -X POST http://localhost:8001/api/init

# Тест входа
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sls1.com","password":"admin123"}'
```

### Frontend
Откройте браузер по адресу: `http://localhost:3000`

## 📝 Концепции из Android-приложения

Приложение основано на следующих концепциях из оригинального Android-приложения:
- ✅ Система ролей и аутентификации
- ✅ Управление проектами с статусами
- ✅ Управление инвентарем с категориями
- ✅ Админ-панель для управления пользователями
- ⏳ Трехфазный процесс работы с проектами (в разработке)
- ⏳ Система согласований между куратором и декоратором (в разработке)
- ⏳ Работа с фотографиями (в разработке)
- ⏳ Интеграция с Google Sheets (заменено на MongoDB)

## 🔐 Безопасность

- JWT токены с истечением
- Bcrypt для хеширования паролей
- Ролевой доступ (RBAC)
- CORS настроен
- Валидация данных через Pydantic

## 📱 UI Компоненты

Использованы следующие компоненты shadcn/ui:
- Button
- Card
- Dialog
- Input
- Label
- Select
- Badge
- Avatar
- Dropdown Menu
- Toast (уведомления)
- и многие другие...

## 🚀 Развертывание

### Переменные окружения

#### Backend (.env)
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=sls1_db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
```

#### Frontend (.env)
```env
REACT_APP_BACKEND_URL=http://localhost:8001
```

## 🔜 Roadmap

- [ ] Детальная страница проекта
- [ ] Трехфазный процесс работы с проектами
- [ ] Система согласований
- [ ] Загрузка и просмотр фотографий
- [ ] Страница логов для админа
- [ ] Фильтрация и поиск
- [ ] Экспорт данных
- [ ] Уведомления в реальном времени
- [ ] Темная/светлая тема переключатель

## 📞 Поддержка

При возникновении проблем проверьте:
1. Запущены ли все сервисы: `sudo supervisorctl status`
2. Логи backend: `tail -f /var/log/supervisor/backend.*.log`
3. Логи frontend: `tail -f /var/log/supervisor/frontend.*.log`
4. Инициализирована ли база данных: `curl -X POST http://localhost:8001/api/init`

## 📄 Лицензия

Внутренний проект студии. Все права защищены.

---

**Разработано на основе концепций Android-приложения SLS1**
