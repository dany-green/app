"""
Telegram Storage Service - Хранение фотографий через Telegram Bot
Использует Telegram как бесплатное неограниченное хранилище для изображений
"""

import os
import io
import uuid
import logging
import aiohttp
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TelegramStorage:
    """Сервис для работы с Telegram Bot API для хранения изображений"""
    
    def __init__(self, bot_token: str, chat_id: str):
        """
        Инициализация Telegram хранилища
        
        Args:
            bot_token: Токен Telegram бота (получить через @BotFather)
            chat_id: ID чата/канала для загрузки файлов
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        
    async def upload_photo(self, file_content: bytes, caption: str = "") -> Optional[str]:
        """
        Загрузить фото в Telegram
        
        Args:
            file_content: Содержимое файла
            caption: Подпись к фото (опционально)
            
        Returns:
            file_id фотографии в Telegram или None при ошибке
        """
        try:
            url = f"{self.api_url}/sendPhoto"
            
            # Создать multipart форму
            form_data = aiohttp.FormData()
            form_data.add_field('chat_id', self.chat_id)
            form_data.add_field('photo', file_content, filename='photo.jpg', content_type='image/jpeg')
            if caption:
                form_data.add_field('caption', caption)
            
            # Отправить запрос
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=form_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('ok'):
                            # Получить file_id самого большого размера фото
                            photos = result['result']['photo']
                            largest_photo = max(photos, key=lambda p: p['file_size'])
                            file_id = largest_photo['file_id']
                            logger.info(f"Photo uploaded to Telegram: {file_id}")
                            return file_id
                    
                    error_text = await response.text()
                    logger.error(f"Failed to upload photo to Telegram: {error_text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error uploading photo to Telegram: {e}")
            return None
    
    async def get_file_url(self, file_id: str) -> Optional[str]:
        """
        Получить прямую ссылку на файл
        
        Args:
            file_id: ID файла в Telegram
            
        Returns:
            Прямая ссылка на файл или None при ошибке
        """
        try:
            url = f"{self.api_url}/getFile"
            params = {'file_id': file_id}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('ok'):
                            file_path = result['result']['file_path']
                            file_url = f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
                            return file_url
                    
                    logger.error(f"Failed to get file URL from Telegram: {await response.text()}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting file URL from Telegram: {e}")
            return None
    
    async def delete_photo(self, file_id: str, message_id: Optional[int] = None) -> bool:
        """
        Удалить фото из Telegram (удаляет сообщение)
        
        Args:
            file_id: ID файла в Telegram
            message_id: ID сообщения (если известен)
            
        Returns:
            True если удаление успешно
            
        Note:
            Telegram API не позволяет удалить файл по file_id напрямую.
            Нужен message_id для удаления сообщения.
            Если message_id неизвестен, файл останется в чате.
        """
        if not message_id:
            logger.warning(f"Cannot delete photo {file_id}: message_id not provided")
            return False
            
        try:
            url = f"{self.api_url}/deleteMessage"
            params = {
                'chat_id': self.chat_id,
                'message_id': message_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=params) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('ok'):
                            logger.info(f"Photo {file_id} deleted from Telegram")
                            return True
                    
                    logger.error(f"Failed to delete photo from Telegram: {await response.text()}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error deleting photo from Telegram: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Проверить подключение к Telegram Bot API
        
        Returns:
            True если подключение успешно
        """
        try:
            url = f"{self.api_url}/getMe"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('ok'):
                            bot_info = result['result']
                            logger.info(f"Connected to Telegram bot: @{bot_info['username']}")
                            return True
                    
                    logger.error(f"Failed to connect to Telegram: {await response.text()}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error testing Telegram connection: {e}")
            return False
