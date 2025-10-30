# 🚀 SLS1 Organizational Platform - Деплой версия

## 📖 О проекте

Full-stack веб-приложение для управления проектами, инвентарём и оборудованием.

**Технологии:**
- 🎨 Frontend: React + Tailwind CSS
- ⚙️ Backend: FastAPI (Python)
- 💾 Database: MongoDB
- 📸 Photo Storage: Telegram Bot (бесплатно и неограниченно!)

---

## 🌍 Развертывание (для пользователей из России)

### ✅ Рекомендуемый стек: PythonAnywhere + Telegram + MongoDB Atlas

**Полностью бесплатно! Работает из России без VPN!**

### 📚 Инструкции по развертыванию:

1. **[PYTHONANYWHERE_DEPLOY_GUIDE.md](./PYTHONANYWHERE_DEPLOY_GUIDE.md)** - Полная подробная инструкция (1-2 часа)
2. **[DEPLOY_QUICK_GUIDE.md](./DEPLOY_QUICK_GUIDE.md)** - Краткая шпаргалка (для опытных)
3. **[TELEGRAM_STORAGE_GUIDE.md](./TELEGRAM_STORAGE_GUIDE.md)** - Как работает хранение фото в Telegram

### 🎯 Быстрый старт:

```bash
# 1. Создать Telegram бота (@BotFather)
# 2. Создать MongoDB Atlas кластер (бесплатно)
# 3. Сохранить проект в GitHub
# 4. Развернуть на PythonAnywhere

# Подробности в PYTHONANYWHERE_DEPLOY_GUIDE.md
```

---

## 🏗️ Локальная разработка

### Требования:

- Python 3.10+
- Node.js 16+
- MongoDB
- Yarn

### Установка:

```bash
# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # Настроить переменные окружения

# Frontend
cd frontend
yarn install
cp .env.example .env  # Настроить REACT_APP_BACKEND_URL
```

### Запуск:

```bash
# Backend (из папки backend)
uvicorn server:app --reload --port 8001

# Frontend (из папки frontend)
yarn start
```

Откройте: http://localhost:3000

---

## ⚙️ Настройка хранилища фотографий

### Режимы хранения:

Файл: `backend/google_sheets_config.json`

```json
{
  "storage_mode": "local"  // или "telegram" или "google_sheets"
}
```

### 1. Локальное хранилище (по умолчанию)

```json
{
  "storage_mode": "local",
  "local_storage": {
    "upload_dir": "/app/uploads",
    "max_file_size_mb": 10
  }
}
```

✅ Просто  
⚠️ Ограничено местом на сервере  
⚠️ Не подходит для production на PythonAnywhere (512 МБ лимит)

### 2. Telegram Bot (рекомендуется для production)

```json
{
  "storage_mode": "telegram",
  "telegram_storage": {
    "enabled": true
  }
}
```

**Переменные окружения:**
```bash
TELEGRAM_BOT_TOKEN=1234567890:ABC...
TELEGRAM_CHAT_ID=-1001234567890
```

✅ Бесплатно и неограниченно  
✅ Быстрый CDN  
✅ Работает из России  
⚠️ Зависимость от Telegram API  

**Инструкция:** [TELEGRAM_STORAGE_GUIDE.md](./TELEGRAM_STORAGE_GUIDE.md)

### 3. Google Sheets + Drive (будущее)

```json
{
  "storage_mode": "google_sheets"
}
```

**Инструкция:** [GOOGLE_SHEETS_INTEGRATION.md](./GOOGLE_SHEETS_INTEGRATION.md)

---

## 🗂️ Структура проекта

```
/app/
├── backend/                        # FastAPI бэкенд
│   ├── server.py                  # Главный файл с API endpoints
│   ├── models.py                  # Pydantic модели
│   ├── auth.py                    # Аутентификация и авторизация
│   ├── storage_service.py         # Сервис хранения фото
│   ├── telegram_storage.py        # Telegram интеграция
│   ├── requirements.txt           # Python зависимости
│   ├── .env                       # Переменные окружения
│   └── google_sheets_config.json  # Конфигурация хранилищ
│
├── frontend/                       # React фронтенд
│   ├── src/
│   │   ├── App.js                # Главный компонент
│   │   ├── components/           # React компоненты
│   │   └── ...
│   ├── package.json              # Node.js зависимости
│   ├── .env                      # Переменные окружения
│   └── tailwind.config.js        # Tailwind CSS конфиг
│
├── PYTHONANYWHERE_DEPLOY_GUIDE.md  # 📖 Инструкция по деплою
├── DEPLOY_QUICK_GUIDE.md           # ⚡ Краткая шпаргалка
├── TELEGRAM_STORAGE_GUIDE.md       # 📸 Гайд по Telegram хранилищу
├── GOOGLE_SHEETS_INTEGRATION.md    # 📊 Гайд по Google Sheets
└── README.md                       # Этот файл
```

---

## 🔐 Переменные окружения

### Backend (.env):

```bash
# MongoDB
MONGO_URL=mongodb+srv://user:password@cluster.mongodb.net/
DB_NAME=sls1_db

# JWT
SECRET_KEY=ваш-секретный-ключ-минимум-32-символа

# Telegram Storage (опционально)
TELEGRAM_BOT_TOKEN=1234567890:ABC...
TELEGRAM_CHAT_ID=-1001234567890
```

### Frontend (.env):

```bash
# Backend URL
REACT_APP_BACKEND_URL=http://localhost:8001
# Или для production:
# REACT_APP_BACKEND_URL=https://username.pythonanywhere.com/api
```

---

## 📡 API Endpoints

### Аутентификация:
- `POST /api/auth/register` - Регистрация (Admin only)
- `POST /api/auth/login` - Вход
- `GET /api/auth/me` - Текущий пользователь

### Проекты:
- `GET /api/projects` - Список проектов
- `POST /api/projects` - Создать проект
- `GET /api/projects/{id}` - Получить проект
- `PATCH /api/projects/{id}` - Обновить проект
- `DELETE /api/projects/{id}` - Удалить проект

### Инвентарь:
- `GET /api/inventory` - Список инвентаря
- `POST /api/inventory` - Создать элемент
- `PATCH /api/inventory/{id}` - Обновить элемент
- `POST /api/inventory/{id}/images` - Загрузить фото
- `DELETE /api/inventory/{id}/images` - Удалить фото

### Оборудование:
- `GET /api/equipment` - Список оборудования
- `POST /api/equipment` - Создать элемент
- `PATCH /api/equipment/{id}` - Обновить элемент
- `POST /api/equipment/{id}/images` - Загрузить фото
- `DELETE /api/equipment/{id}/images` - Удалить фото

### Изображения:
- `GET /api/uploads/{item_id}/{filename}` - Локальное изображение
- `GET /api/telegram/image/{file_id}` - Telegram изображение (редирект)

### Логи:
- `GET /api/logs` - История действий

---

## 👥 Роли пользователей

- **Admin** - Полный доступ ко всем функциям
- **Curator** - Создание и редактирование проектов, инвентаря
- **Member** - Просмотр проектов

---

## 🔧 Полезные команды

### Backend:

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn server:app --reload --port 8001

# Тесты
pytest

# Линтинг
ruff check .
```

### Frontend:

```bash
# Установка зависимостей
yarn install

# Разработка
yarn start

# Сборка для production
yarn build

# Тесты
yarn test
```

---

## 📦 Зависимости

### Backend (Python):
- FastAPI - Web фреймворк
- Motor - Async MongoDB драйвер
- Pydantic - Валидация данных
- PyJWT - JWT токены
- Pillow - Обработка изображений
- aiohttp - Async HTTP клиент (для Telegram)

### Frontend (Node.js):
- React - UI библиотека
- Tailwind CSS - CSS фреймворк
- Axios - HTTP клиент

---

## 🚀 Альтернативные варианты развертывания

### 1. Emergent Deploy (Самый простой)
- Нажмите "Deploy" в интерфейсе Emergent
- Стоимость: 50 кредитов/месяц
- Всё настроено автоматически

### 2. Railway.app
- Поддержка full-stack
- Автоматические деплои из GitHub
- От $5/месяц

### 3. Render.com
- Есть бесплатный тариф
- Full-stack поддержка
- Интеграция с GitHub

### 4. Yandex Cloud (Россия)
- Российский сервис
- Первые 60 дней бесплатно
- Требуется российская карта

### 5. VK Cloud (Россия)
- Российский сервис
- Тестовый период
- Требуется верификация

---

## 📖 Дополнительная документация

- **[PYTHONANYWHERE_DEPLOY_GUIDE.md](./PYTHONANYWHERE_DEPLOY_GUIDE.md)** - Подробная инструкция по развертыванию на PythonAnywhere (для России)
- **[DEPLOY_QUICK_GUIDE.md](./DEPLOY_QUICK_GUIDE.md)** - Краткая шпаргалка по деплою
- **[TELEGRAM_STORAGE_GUIDE.md](./TELEGRAM_STORAGE_GUIDE.md)** - Руководство по хранению фото в Telegram
- **[GOOGLE_SHEETS_INTEGRATION.md](./GOOGLE_SHEETS_INTEGRATION.md)** - Интеграция с Google Sheets
- **[PHOTOS_GUIDE.md](./PHOTOS_GUIDE.md)** - Руководство по работе с фотографиями
- **[TESTDATA_GUIDE.md](./TESTDATA_GUIDE.md)** - Инструкция по загрузке тестовых данных

---

## 🤝 Поддержка

Если возникли вопросы или проблемы:

1. Проверьте документацию в соответствующих .md файлах
2. Проверьте логи:
   - Backend: `tail -f /var/log/supervisor/backend.err.log`
   - PythonAnywhere: вкладка "Log files" → "Error log"
3. Убедитесь что все переменные окружения установлены правильно
4. Проверьте что сервисы запущены

---

## 📝 Лицензия

Proprietary - Все права защищены

---

## 🎉 Готово к использованию!

Следуйте инструкциям в **[PYTHONANYWHERE_DEPLOY_GUIDE.md](./PYTHONANYWHERE_DEPLOY_GUIDE.md)** для развертывания вашего приложения!

**Ваше приложение будет доступно по адресу:**
`https://ваш-username.pythonanywhere.com`

**Удачи! 🚀**
