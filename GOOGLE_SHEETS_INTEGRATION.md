# 📊 Интеграция с Google Sheets - Полная инструкция

## 🎯 Обзор

Эта система поддерживает два режима хранения фотографий:
1. **Локальное хранилище** (текущая реализация) - файлы хранятся на сервере
2. **Google Sheets + Google Drive** (будущая интеграция) - синхронизация с облаком

## 📋 Содержание

1. [Текущая архитектура](#текущая-архитектура)
2. [Подготовка к интеграции с Google Sheets](#подготовка-к-интеграции-с-google-sheets)
3. [Создание Google Cloud проекта](#создание-google-cloud-проекта)
4. [Настройка Google Sheets API](#настройка-google-sheets-api)
5. [Настройка Google Drive API](#настройка-google-drive-api)
6. [Структура таблиц](#структура-таблиц)
7. [Конфигурация](#конфигурация)
8. [Миграция данных](#миграция-данных)
9. [FAQ](#faq)

---

## 🏗️ Текущая архитектура

### Компоненты системы:

```
/app/backend/
├── storage_service.py          # Абстрактный слой хранилища
├── google_sheets_config.json   # Конфигурация
├── server.py                    # API endpoints
└── /uploads/                    # Локальное хранилище (создается автоматически)
    └── {item_id}/               # Папка для каждого элемента
        ├── image1.jpg
        ├── image2.png
        └── ...
```

### Текущий режим: `local`

**Что работает сейчас:**
- ✅ Загрузка изображений через API
- ✅ Автоматическое сжатие и оптимизация
- ✅ Хранение на сервере в `/app/uploads`
- ✅ Поддержка нескольких изображений на элемент
- ✅ Удаление изображений

---

## 🚀 Подготовка к интеграции с Google Sheets

### Зачем это нужно?

Google Sheets интеграция позволит:
- 📊 Управлять инвентарем через привычный интерфейс Google Sheets
- ☁️ Хранить фотографии в Google Drive (неограниченное место)
- 🔄 Автоматическая синхронизация данных
- 👥 Совместная работа с таблицей
- 📱 Доступ с любого устройства
- 💾 Резервное копирование в облаке

---

## 🛠️ Создание Google Cloud проекта

### Шаг 1: Создать проект

1. Откройте [Google Cloud Console](https://console.cloud.google.com/)
2. Нажмите **"Select a project"** → **"New Project"**
3. Введите название проекта: `SLS1-Inventory`
4. Нажмите **"Create"**

### Шаг 2: Включить необходимые API

1. Перейдите в **"APIs & Services"** → **"Library"**
2. Найдите и включите:
   - **Google Sheets API**
   - **Google Drive API**

### Шаг 3: Создать Service Account

1. Перейдите в **"APIs & Services"** → **"Credentials"**
2. Нажмите **"Create Credentials"** → **"Service Account"**
3. Введите данные:
   - **Service account name**: `sls1-inventory-service`
   - **Service account ID**: `sls1-inventory-service`
   - **Description**: `Service account for SLS1 inventory management`
4. Нажмите **"Create and Continue"**
5. Выберите роль: **Editor** (или создайте custom роль с минимальными правами)
6. Нажмите **"Continue"** → **"Done"**

### Шаг 4: Создать и скачать ключ

1. Найдите созданный Service Account в списке
2. Нажмите на него → перейдите на вкладку **"Keys"**
3. Нажмите **"Add Key"** → **"Create new key"**
4. Выберите тип: **JSON**
5. Нажмите **"Create"**
6. Файл `credentials.json` будет скачан автоматически

### Шаг 5: Установить credentials

```bash
# Скопируйте файл в директорию backend
cp ~/Downloads/credentials.json /app/backend/credentials.json

# Установите правильные права доступа
chmod 600 /app/backend/credentials.json
```

---

## 📊 Настройка Google Sheets API

### Шаг 1: Создать таблицу

1. Откройте [Google Sheets](https://sheets.google.com/)
2. Создайте новую таблицу: **"SLS1 Инвентарь"**
3. Скопируйте ID таблицы из URL:
   ```
   https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit
   ```

### Шаг 2: Создать листы

#### Лист 1: "Инвентарь"

Создайте заголовки в первой строке:

| id | category | name | total_quantity | visual_marker | description | created_at | updated_at |
|----|----------|------|----------------|---------------|-------------|------------|------------|

**Описание полей:**
- `id` - уникальный UUID элемента
- `category` - категория (Вазы, Свечи, и т.д.)
- `name` - название элемента
- `total_quantity` - количество
- `visual_marker` - emoji маркер
- `description` - описание
- `created_at` - дата создания (ISO 8601)
- `updated_at` - дата обновления (ISO 8601)

#### Лист 2: "Фотографии"

Создайте заголовки в первой строке:

| id | item_id | image_url | drive_file_id | filename | uploaded_at | uploaded_by |
|----|---------|-----------|---------------|----------|-------------|-------------|

**Описание полей:**
- `id` - уникальный UUID записи
- `item_id` - ID элемента инвентаря (связь с листом "Инвентарь")
- `image_url` - публичная ссылка на изображение в Google Drive
- `drive_file_id` - ID файла в Google Drive
- `filename` - оригинальное имя файла
- `uploaded_at` - дата загрузки (ISO 8601)
- `uploaded_by` - email пользователя

### Шаг 3: Предоставить доступ Service Account

1. Откройте созданную таблицу
2. Нажмите **"Share"** (Поделиться)
3. Вставьте email вашего Service Account:
   ```
   sls1-inventory-service@{PROJECT_ID}.iam.gserviceaccount.com
   ```
   (найдите этот email в файле `credentials.json`, поле `client_email`)
4. Установите права: **Editor**
5. Снимите галочку **"Notify people"**
6. Нажмите **"Share"**

---

## 📁 Настройка Google Drive API

### Шаг 1: Создать папку для фотографий

1. Откройте [Google Drive](https://drive.google.com/)
2. Создайте папку: **"SLS1 Inventory Images"**
3. Скопируйте ID папки из URL:
   ```
   https://drive.google.com/drive/folders/{FOLDER_ID}
   ```

### Шаг 2: Предоставить доступ Service Account

1. Откройте созданную папку
2. Нажмите правой кнопкой → **"Share"**
3. Вставьте email вашего Service Account
4. Установите права: **Editor**
5. Нажмите **"Share"**

### Шаг 3: Настроить публичный доступ (опционально)

Если хотите, чтобы изображения были доступны по прямым ссылкам:

1. Откройте папку → правой кнопкой → **"Get link"**
2. Выберите **"Anyone with the link"** → **Viewer**
3. Нажмите **"Copy link"**

---

## ⚙️ Конфигурация

### Редактирование `google_sheets_config.json`

```bash
nano /app/backend/google_sheets_config.json
```

### Заполните параметры:

```json
{
  "storage_mode": "google_sheets",
  
  "google_sheets": {
    "enabled": true,
    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
    
    "sheets": {
      "inventory": {
        "sheet_name": "Инвентарь",
        "sheet_id": 0
      },
      "images": {
        "sheet_name": "Фотографии",
        "sheet_id": 1
      }
    },
    
    "credentials": {
      "type": "service_account",
      "credentials_file": "credentials.json"
    },
    
    "sync": {
      "auto_sync": true,
      "sync_interval_minutes": 30
    },
    
    "google_drive": {
      "enabled": true,
      "folder_id": "1a2b3c4d5e6f7g8h9i0j"
    }
  }
}
```

### Параметры:

- `storage_mode`: `"local"` или `"google_sheets"`
- `spreadsheet_id`: ID вашей таблицы Google Sheets
- `sheet_name`: название листа (должно совпадать с таблицей)
- `sheet_id`: порядковый номер листа (0 - первый лист)
- `credentials_file`: путь к файлу credentials.json
- `auto_sync`: автоматическая синхронизация (true/false)
- `sync_interval_minutes`: интервал синхронизации в минутах
- `folder_id`: ID папки в Google Drive для фотографий

---

## 🔄 Миграция данных

### Экспорт локальных данных в Google Sheets

После настройки Google Sheets создайте скрипт миграции:

```bash
# Создать скрипт миграции
nano /app/backend/migrate_to_sheets.py
```

```python
"""
Скрипт миграции данных из локальной БД в Google Sheets
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
import json

# Загрузить конфигурацию
with open('google_sheets_config.json', 'r') as f:
    config = json.load(f)

# Подключиться к MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'sls1_db')]

# Настроить Google Sheets API
creds = Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file']
)
sheets_service = build('sheets', 'v4', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

async def migrate():
    print("Начало миграции...")
    
    # Получить все элементы инвентаря
    items = await db.inventory.find({}, {"_id": 0}).to_list(1000)
    print(f"Найдено элементов: {len(items)}")
    
    # Подготовить данные для Google Sheets
    values = [
        ['id', 'category', 'name', 'total_quantity', 'visual_marker', 
         'description', 'created_at', 'updated_at']
    ]
    
    for item in items:
        values.append([
            item.get('id', ''),
            item.get('category', ''),
            item.get('name', ''),
            item.get('total_quantity', 0),
            item.get('visual_marker', ''),
            item.get('description', ''),
            item.get('created_at', ''),
            item.get('updated_at', '')
        ])
    
    # Записать в Google Sheets
    spreadsheet_id = config['google_sheets']['spreadsheet_id']
    sheet_name = config['google_sheets']['sheets']['inventory']['sheet_name']
    
    body = {'values': values}
    result = sheets_service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f'{sheet_name}!A1',
        valueInputOption='RAW',
        body=body
    ).execute()
    
    print(f"Обновлено ячеек: {result.get('updatedCells')}")
    print("Миграция завершена!")

if __name__ == '__main__':
    asyncio.run(migrate())
```

### Запустить миграцию:

```bash
cd /app/backend
python migrate_to_sheets.py
```

---

## 📚 Установка библиотек для Google Sheets

Добавьте в `requirements.txt`:

```txt
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
google-api-python-client>=2.100.0
```

Установите:

```bash
cd /app/backend
pip install -r requirements.txt
```

---

## 🔧 Реализация Google Sheets методов

После настройки, реализуйте методы в `storage_service.py`:

```python
async def _save_google_drive(self, file_content: bytes, filename: str, item_id: str) -> str:
    """Сохранить файл в Google Drive"""
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaInMemoryUpload
    
    # Аутентификация
    creds = Credentials.from_service_account_file(
        'credentials.json',
        scopes=['https://www.googleapis.com/auth/drive.file']
    )
    service = build('drive', 'v3', credentials=creds)
    
    # Метаданные файла
    file_metadata = {
        'name': filename,
        'parents': [self.config['google_sheets']['google_drive']['folder_id']]
    }
    
    # Загрузить файл
    media = MediaInMemoryUpload(file_content, mimetype='image/jpeg')
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink, webContentLink'
    ).execute()
    
    # Получить публичную ссылку
    file_id = file.get('id')
    
    # Сделать файл публичным
    service.permissions().create(
        fileId=file_id,
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    
    # Получить прямую ссылку
    direct_link = f"https://drive.google.com/uc?export=view&id={file_id}"
    
    # Сохранить в Google Sheets (лист "Фотографии")
    # TODO: добавить запись в Google Sheets
    
    return direct_link
```

---

## ❓ FAQ

### Q: Как переключиться между локальным и Google Sheets хранилищем?

**A:** Измените параметр `storage_mode` в `google_sheets_config.json`:
- `"local"` - локальное хранилище
- `"google_sheets"` - Google Sheets + Drive

### Q: Будут ли потеряны данные при переключении?

**A:** Нет, если используете скрипт миграции. Данные будут скопированы, а не перемещены.

### Q: Как часто происходит синхронизация?

**A:** Интервал настраивается в `sync_interval_minutes`. По умолчанию - 30 минут.

### Q: Можно ли использовать оба режима одновременно?

**A:** Не рекомендуется. Выберите один основной режим. Можно настроить backup в другой режим.

### Q: Сколько стоит Google Cloud?

**A:** Google Sheets и Drive API имеют бесплатный квотный лимит, которого достаточно для малого/среднего бизнеса. Подробнее: [Google Cloud Pricing](https://cloud.google.com/pricing)

### Q: Как мониторить использование квот?

**A:** Откройте [Google Cloud Console](https://console.cloud.google.com/) → **APIs & Services** → **Dashboard**

---

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `tail -f /var/log/supervisor/backend.err.log`
2. Убедитесь, что Service Account имеет доступ к таблице и папке
3. Проверьте, что API включены в Google Cloud Console
4. Проверьте формат `credentials.json`

---

## 🎉 Готово!

После выполнения всех шагов:
1. Перезапустите backend: `sudo supervisorctl restart backend`
2. Проверьте логи на ошибки
3. Протестируйте загрузку изображения через UI

**Ваша система готова к работе с Google Sheets!** 🚀
