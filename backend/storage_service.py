"""
Storage Service - Абстрактный слой для работы с хранилищем фотографий
Поддерживает:
- Локальное хранилище
- Telegram Bot (неограниченное облачное хранилище)
- Google Sheets (будущая интеграция)
"""

import os
import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import uuid
from PIL import Image
import io
from telegram_storage import TelegramStorage

# Загрузка конфигурации
CONFIG_PATH = Path(__file__).parent / 'google_sheets_config.json'
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

STORAGE_MODE = CONFIG.get('storage_mode', 'local')
UPLOAD_DIR = Path(CONFIG['local_storage']['upload_dir'])
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)


class StorageService:
    """Сервис для работы с хранилищем фотографий"""
    
    def __init__(self):
        self.mode = STORAGE_MODE
        self.upload_dir = UPLOAD_DIR
        self.config = CONFIG
        self.telegram_storage = None
        
        # Инициализировать Telegram хранилище если включено
        if self.mode == 'telegram':
            telegram_config = CONFIG.get('telegram_storage', {})
            bot_token = os.environ.get('TELEGRAM_BOT_TOKEN', telegram_config.get('bot_token', ''))
            chat_id = os.environ.get('TELEGRAM_CHAT_ID', telegram_config.get('chat_id', ''))
            
            if bot_token and chat_id:
                self.telegram_storage = TelegramStorage(bot_token, chat_id)
            else:
                raise ValueError(
                    "Telegram storage enabled but credentials not provided. "
                    "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables."
                )
        
    async def save_image(self, file_content: bytes, filename: str, item_id: str) -> str:
        """
        Сохранить изображение
        
        Args:
            file_content: Содержимое файла
            filename: Оригинальное имя файла
            item_id: ID элемента инвентаря
            
        Returns:
            URL или путь к сохраненному изображению
        """
        if self.mode == 'local':
            return await self._save_local(file_content, filename, item_id)
        elif self.mode == 'google_sheets':
            return await self._save_google_drive(file_content, filename, item_id)
        else:
            raise ValueError(f"Unknown storage mode: {self.mode}")
    
    async def _save_local(self, file_content: bytes, filename: str, item_id: str) -> str:
        """Сохранить файл локально"""
        # Создать папку для элемента
        item_dir = self.upload_dir / item_id
        item_dir.mkdir(exist_ok=True, parents=True)
        
        # Генерировать уникальное имя файла
        ext = Path(filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{ext}"
        file_path = item_dir / unique_filename
        
        # Оптимизировать изображение если включено
        if self.config['local_storage']['image_optimization']['enabled']:
            file_content = self._optimize_image(file_content)
        
        # Сохранить файл
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Вернуть относительный путь
        return f"/api/uploads/{item_id}/{unique_filename}"
    
    async def _save_google_drive(self, file_content: bytes, filename: str, item_id: str) -> str:
        """
        Сохранить файл в Google Drive (будущая реализация)
        
        TODO: Реализовать после настройки Google Drive API
        - Аутентификация через service account
        - Загрузка файла в указанную папку
        - Получение публичной ссылки
        - Сохранение ссылки в Google Sheets
        """
        raise NotImplementedError(
            "Google Drive integration not implemented yet. "
            "See GOOGLE_SHEETS_INTEGRATION.md for setup instructions."
        )
    
    def _optimize_image(self, file_content: bytes) -> bytes:
        """Оптимизировать изображение (сжатие и изменение размера)"""
        opt_config = self.config['local_storage']['image_optimization']
        
        try:
            # Открыть изображение
            img = Image.open(io.BytesIO(file_content))
            
            # Конвертировать RGBA в RGB если необходимо
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Изменить размер если превышает максимальный
            max_width = opt_config['max_width']
            max_height = opt_config['max_height']
            
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Сохранить в буфер с оптимизацией
            output = io.BytesIO()
            img.save(
                output, 
                format='JPEG', 
                quality=opt_config['quality'],
                optimize=True
            )
            return output.getvalue()
            
        except Exception as e:
            # Если оптимизация не удалась, вернуть оригинал
            print(f"Image optimization failed: {e}")
            return file_content
    
    async def delete_image(self, image_url: str) -> bool:
        """
        Удалить изображение
        
        Args:
            image_url: URL или путь к изображению
            
        Returns:
            True если удаление успешно
        """
        if self.mode == 'local':
            return await self._delete_local(image_url)
        elif self.mode == 'google_sheets':
            return await self._delete_google_drive(image_url)
        else:
            return False
    
    async def _delete_local(self, image_url: str) -> bool:
        """Удалить локальный файл"""
        try:
            # Извлечь путь из URL
            # /api/uploads/{item_id}/{filename}
            parts = image_url.split('/')
            if len(parts) >= 4 and parts[1] == 'api' and parts[2] == 'uploads':
                item_id = parts[3]
                filename = parts[4]
                file_path = self.upload_dir / item_id / filename
                
                if file_path.exists():
                    file_path.unlink()
                    return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    async def _delete_google_drive(self, image_url: str) -> bool:
        """
        Удалить файл из Google Drive (будущая реализация)
        
        TODO: Реализовать после настройки Google Drive API
        """
        raise NotImplementedError("Google Drive integration not implemented yet")
    
    async def get_item_images(self, item_id: str) -> List[str]:
        """
        Получить все изображения для элемента
        
        Args:
            item_id: ID элемента инвентаря
            
        Returns:
            Список URL изображений
        """
        if self.mode == 'local':
            return await self._get_local_images(item_id)
        elif self.mode == 'google_sheets':
            return await self._get_google_sheets_images(item_id)
        else:
            return []
    
    async def _get_local_images(self, item_id: str) -> List[str]:
        """Получить локальные изображения"""
        item_dir = self.upload_dir / item_id
        if not item_dir.exists():
            return []
        
        images = []
        for file_path in item_dir.iterdir():
            if file_path.is_file():
                images.append(f"/api/uploads/{item_id}/{file_path.name}")
        
        return sorted(images)
    
    async def _get_google_sheets_images(self, item_id: str) -> List[str]:
        """
        Получить изображения из Google Sheets (будущая реализация)
        
        TODO: Реализовать после настройки Google Sheets API
        - Запросить строки из таблицы "Фотографии"
        - Отфильтровать по item_id
        - Вернуть список URL
        """
        raise NotImplementedError("Google Sheets integration not implemented yet")


# Глобальный экземпляр сервиса
storage_service = StorageService()
