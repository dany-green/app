# ⚡ Краткая шпаргалка: PythonAnywhere + Telegram

## 1️⃣ Telegram Bot (5 минут)

```
1. @BotFather → /newbot → получить ТОКЕН
2. Создать приватный канал
3. Добавить бота в админы канала
4. @getidsbot → переслать сообщение → получить CHAT_ID
```

**Сохраните:**
- `TELEGRAM_BOT_TOKEN`: `1234567890:ABC...`
- `TELEGRAM_CHAT_ID`: `-1001234567890`

---

## 2️⃣ MongoDB Atlas (5 минут)

```
1. mongodb.com/cloud/atlas/register → зарегистрироваться
2. Создать M0 Free кластер
3. Database Access → создать пользователя
4. Network Access → Allow 0.0.0.0/0
5. Connect → скопировать строку подключения
```

**Сохраните:**
- `MONGO_URL`: `mongodb+srv://admin:пароль@cluster0...`

---

## 3️⃣ GitHub (2 минуты)

```
В Emergent чате:
"Сохрани проект в GitHub"
```

**Сохраните URL репозитория**

---

## 4️⃣ PythonAnywhere (30 минут)

### Регистрация:
```
pythonanywhere.com → Beginner account (бесплатно)
```

### Bash консоль:
```bash
git clone https://github.com/username/repo.git
cd repo/backend
pip3.10 install --user -r requirements.txt

# Изменить конфиг на telegram
nano google_sheets_config.json
# Изменить "storage_mode": "telegram"
# Ctrl+O, Enter, Ctrl+X
```

### Web → Add new web app:
- Manual configuration
- Python 3.10

### WSGI файл (заменить ВСЁ):
```python
import sys, os

USERNAME = "ваш-логин"
REPO_NAME = "название-репо"

path = f'/home/{USERNAME}/{REPO_NAME}/backend'
sys.path.append(path)

os.environ['MONGO_URL'] = "mongodb+srv://..."
os.environ['DB_NAME'] = 'sls1_db'
os.environ['SECRET_KEY'] = "любая-строка-32-символа"
os.environ['TELEGRAM_BOT_TOKEN'] = "токен-из-шага-1"
os.environ['TELEGRAM_CHAT_ID'] = "chat-id-из-шага-1"

from server import app
application = app
```

### Фронтенд (Bash):
```bash
cd ~/repo/frontend
echo "REACT_APP_BACKEND_URL=https://username.pythonanywhere.com/api" > .env
npm install -g yarn
yarn install
yarn build
```

### Static Files (Web):
```
URL: /static/
Directory: /home/username/repo/frontend/build/static/

URL: /
Directory: /home/username/repo/frontend/build/
```

### Перезапуск:
```
Web → Reload
```

---

## ✅ Готово!

Сайт: `https://username.pythonanywhere.com`

---

## 🔄 Обновление:

```bash
cd ~/repo
git pull
cd backend && pip3.10 install --user -r requirements.txt
cd ../frontend && yarn build
```

Web → Reload
