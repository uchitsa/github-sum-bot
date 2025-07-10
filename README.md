# GitHub Summary Telegram Bot

Github profile information telegram bot.

## ⚙️ Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/github-telegram-bot.git
cd github-telegram-bot
```

Install dependencies:

```bash

pip install -r requirements.txt
```
Create bot with BotFather telegram account and get a token

Run the bot:

```bash

export TELEGRAM_BOT_TOKEN="ваш_токен"
python bot.py
```

🚀 Usage

    /start - Welcome message

    /github <username> - Github profile info

Example:
```text
/github torvalds
```

🧪 Testing
```bash

pytest
```

🔄 CI/CD

    Automatic tests run on every commit with Github Actions

🌟 Features

    Info about repositories, subscribers and registration date

    Handling connection errors

    Formatted messages with emoji

