# 📸 Как работает хранение фото в Telegram

## Архитектура

```
Пользователь загружает фото → FastAPI бэкенд → Telegram Bot API → Telegram CDN
                                      ↓
                               MongoDB сохраняет:
                               telegram:ABC123xyz...
```

## Как это работает?

### 1. Загрузка фото

Когда пользователь загружает фото через UI:

1. **Фронтенд** отправляет файл на `POST /api/equipment/{item_id}/images`
2. **Бэкенд** вызывает `storage_service.save_image()`:
   - Оптимизирует изображение (сжатие, размер)
   - Загружает в Telegram через Bot API
   - Получает `file_id` от Telegram
3. **В MongoDB** сохраняется строка: `telegram:ABC123xyz...`
4. **Фронтенд** получает эту строку как `image_url`

### 2. Отображение фото

Когда нужно показать фото в UI:

**Вариант А: Прямой URL (рекомендуется)**
```javascript
// Фронтенд получил: "telegram:ABC123xyz..."
const fileId = imageUrl.replace('telegram:', '');
const directUrl = `/api/telegram/image/${fileId}`;

<img src={directUrl} alt="Photo" />
// Бэкенд редиректит на Telegram CDN
```

**Вариант Б: Получить URL заранее**
```javascript
const response = await fetch(`/api/telegram/image/${fileId}`);
const telegramUrl = response.url; // https://api.telegram.org/file/bot.../photo.jpg
<img src={telegramUrl} alt="Photo" />
```

## Преимущества Telegram хранилища

✅ **Бесплатно и неограниченно**
- Никаких лимитов на количество фото
- Никаких лимитов на размер хранилища

✅ **Быстрая CDN Telegram**
- Глобальная сеть доставки контента
- Быстрая загрузка из любой точки мира

✅ **Надёжность**
- Telegram хранит файлы постоянно
- Резервное копирование на стороне Telegram

✅ **Работает из России**
- Telegram не заблокирован в РФ
- Не требует VPN

## Недостатки

⚠️ **Сложность удаления**
- Telegram не даёт удалять файлы по file_id
- Нужен message_id (можно сохранять при загрузке)
- Файлы остаются в канале при "удалении"

⚠️ **Зависимость от Telegram**
- Если Telegram API недоступен - фото не загружаются
- Требуется стабильный интернет

## Примеры использования

### В backend:

```python
# Загрузка
image_url = await storage_service.save_image(
    file_content=file_bytes,
    filename="photo.jpg",
    item_id="item-123"
)
# Результат: "telegram:AgACAgIAAxkBAAI..."

# Получение прямой ссылки
file_id = image_url.replace('telegram:', '')
direct_url = await storage_service.get_telegram_file_url(file_id)
# Результат: "https://api.telegram.org/file/bot.../photos/file_1.jpg"
```

### Во frontend:

```javascript
// React компонент
function PhotoGallery({ images }) {
  return (
    <div>
      {images.map(imageUrl => {
        // imageUrl = "telegram:AgACAgIAAxkBAAI..."
        const isTeleg ram = imageUrl.startsWith('telegram:');
        const displayUrl = isTelegram
          ? `/api/telegram/image/${imageUrl.replace('telegram:', '')}`
          : imageUrl; // Для локальных файлов
        
        return <img src={displayUrl} key={imageUrl} />;
      })}
    </div>
  );
}
```

## Переключение между хранилищами

### Локальное → Telegram

1. Изменить `storage_mode` в `google_sheets_config.json`:
```json
"storage_mode": "telegram"
```

2. Установить переменные окружения:
```bash
export TELEGRAM_BOT_TOKEN="..."
export TELEGRAM_CHAT_ID="..."
```

3. Перезапустить бэкенд

### Telegram → Локальное

1. Изменить обратно:
```json
"storage_mode": "local"
```

2. Перезапустить бэкенд

**Внимание:** Старые фото останутся в формате `telegram:...`, новые будут `/api/uploads/...`

## Миграция существующих фото

Если у вас уже есть фото в локальном хранилище, можно мигрировать в Telegram:

```python
# Скрипт миграции (создать отдельно)
async def migrate_local_to_telegram():
    items = await db.equipment.find({"images": {"$exists": True}}).to_list(1000)
    
    for item in items:
        new_images = []
        for image_url in item['images']:
            if image_url.startswith('/api/uploads/'):
                # Прочитать локальный файл
                file_path = Path(image_url.replace('/api/uploads/', '/app/uploads/'))
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Загрузить в Telegram
                telegram_url = await storage_service._save_telegram(
                    file_content, 
                    file_path.name, 
                    item['id']
                )
                new_images.append(telegram_url)
            else:
                new_images.append(image_url)
        
        # Обновить в БД
        await db.equipment.update_one(
            {"id": item['id']},
            {"$set": {"images": new_images}}
        )
```

## FAQ

**Q: Можно ли использовать публичный канал?**
A: Да, но приватный безопаснее. В публичном канале фото смогут видеть все.

**Q: Сколько фото можно загрузить?**
A: Неограниченно. Telegram не имеет лимитов на хранилище.

**Q: Какой максимальный размер фото?**
A: Telegram API поддерживает до 10 МБ для фото. Но мы оптимизируем их перед загрузкой.

**Q: Что если бот перестанет работать?**
A: Фото останутся в Telegram. Создайте нового бота и измените токен.

**Q: Безопасно ли хранить конфиденциальные фото?**
A: Да, если канал приватный и бот имеет доступ только к нему. Telegram шифрует данные.

**Q: Можно ли скачать все фото из Telegram?**
A: Да, через Telegram Bot API можно получить все file_id и скачать файлы.
