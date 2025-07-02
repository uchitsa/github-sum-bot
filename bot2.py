import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправьте /github <username>, чтобы увидеть статистику профиля.")

async def github_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text('Используйте команду следующим образом: /github username')
        return

    username = context.args[0]
    try:
        response = requests.get(f'https://api.github.com/users/{username}')
        
        if response.status_code == 200:
            user_data = response.json()
            
            message = f"""
Имя пользователя: {user_data['login']}
Профиль: https://github.com/{user_data['login']}
Репозитории: {user_data['public_repos']} 📁
Подписчики: {user_data['followers']} ⭐️
Подписки: {user_data['following']} ✨
Регистрация: {user_data['created_at'].split('T')[0]} 🗓️
"""
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(f"Пользователь '{username}' не найден!")
    
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Что-то пошло не так...")

def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("github", github_info))

    application.run_polling()

if __name__ == '__main__':
    main()
