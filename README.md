# GitHub Summary Telegram Bot

Бот для получения информации о профиле GitHub через Telegram.

## ⚙️ Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/github-telegram-bot.git
cd github-telegram-bot

    Установите зависимости:

bash

pip install -r requirements.txt

    Создайте бота в BotFather и получите токен

    Запустите бота:

bash

export TELEGRAM_BOT_TOKEN="ваш_токен"
python bot.py

🚀 Использование

    /start - Приветственное сообщение

    /github <username> - Информация о пользователе GitHub

Пример:
text

/github torvalds

🧪 Тестирование
bash

pytest

🔄 CI/CD

Автоматические тесты запускаются при каждом коммите с помощью GitHub Actions
🌟 Особенности

    Информация о репозиториях, подписчиках и дате регистрации

    Форматированные сообщения с эмодзи

    Обработка ошибок подключения
