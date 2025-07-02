from datetime import datetime, timedelta

import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

TG_TOKEN = os.getenv("TG_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {"Authorization": "Bearer {GITHUB_TOKEN}"}


async def start(upd: Update, ctx: CallbackContext):
    await upd.message.reply_text("Send me a Github username")


def get_github_data(username: str):
    one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')

    # GraphQL query for core metrics
    query = f"""
    {{
        user(login:"{username}") {{
        name
        contributionsCollection(from: "{one_year_ago}") {{
          totalCommitContributions
          totalIssueContributions
          totalPullRequestContributions
          totalPullRequestReviewContributions
          totalRepositoriesWithContributedCommits
          commitContributionsByRepository(maxRepositories: 10) {{
            repository {{
              name
              stargazerCount
            }}
            contributions(first: 100) {{
              totalCount
            }}
          }}
        }}
        repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {{
          totalCount
        }}
        starredRepositories(first: 1, since: "{one_year_ago}") {{
          totalCount
        }}
      }}
    }}
    """

    name = ""
    stars = 0
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query},
            headers=HEADERS
        )
        response.raise_for_status()  # Raises an HTTPError for bad responses
        data = response.json()

        if "errors" in data:
            raise ValueError(f"GraphQL Error: {data['errors']}")

        user_data = data.get("data", {}).get("user")
        if not user_data:
            raise ValueError("User not found or no data exists")

        print(user_data)
        name = user_data["name"]
        stars = user_data["starredRepositories"]["totalCount"]


    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return summary_result(username, name, stars)


def summary_result(username: str, name: str, stars: int):
    return f"""
    <b>{name}'s github report</b> (@{username})
    Stars: <code>{stars}</code>
    {datetime.now().strftime('%Y-%m-%d')}
    """


async def handle_username(upd: Update, ctx: CallbackContext):
    username = upd.message.text.strip('@')
    summary = get_github_data(username)
    await upd.message.reply_html(summary, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Share report")]]))


if __name__ == '__main__':
    app = Application.builder().token(TG_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))
    app.run_polling()
