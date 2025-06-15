from datetime import datetime

import os
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

TG_TOKEN = os.getenv("TG_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization":f"{GITHUB_TOKEN}"}

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
    resp = requests.post("https://api.github.com/graphql", json={"query":query}, headers=HEADERS)
    data = resp.json().get("data", {}.get("user"))
    if not data:
        raise ValueError("USer not found or no data exist")
    stars = data["starredRepositories"]["totalCount"]

    return summary_result()


def summary_result(username: str, name: str, stars: int):
    return f"""
    <b>{name}'s github report</b> (@{username})
    Stars: <code>{stars}</code>
    {datetime.now().strftime('%Y-%m-%d')}
    """


async def handle_username(upd: Update, ctx: CallbackContext):
    username = upd.message.text.strip('@')
    summary = await get_github_data(username)
    await upd.message.reply_html(summary, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Share report")]]))


if __name__ == '__main__':
    app = Application.builder().token("TG_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    app.run_polling()
