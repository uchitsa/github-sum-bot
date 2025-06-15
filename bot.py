from datetime import datetime

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters


async def start(upd: Update, ctx: CallbackContext):
    await upd.message.reply_text("Send me a Github username")


def get_github_data(username: str):
    year_ago = (datetime.date.today() - datetime.timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    # graphql query for core metrics
    query = f"""
    {{
        user(login: "{username}") {{
            name
            starredRepositories(first: 1, since: {year_ago}) {{
                totalCount
            }}
        }}
    }}
    """


async def handle_username(upd: Update, ctx: CallbackContext):
    username = upd.message.text.strip('@')
    summary = await get_github_data(username)
    await upd.message.reply_html(summary, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Share report")]]))


app = Application.builder().token("TG_TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
app.run_polling()
