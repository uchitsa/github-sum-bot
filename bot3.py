import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any

import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not TG_TOKEN or not GITHUB_TOKEN:
    raise ValueError("Missing required environment variables: TG_TOKEN and GITHUB_TOKEN")

HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
GITHUB_API_URL = "https://api.github.com/graphql"
ONE_YEAR_AGO = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    pass


async def start(upd: Update, ctx: CallbackContext) -> None:
    """Send welcome message with instructions"""
    welcome_message = (
        "👋 Welcome to GitHub Stats Bot!\n\n"
        "Send me a GitHub username (with or without @) to get their activity report.\n\n"
        "Example: `torvalds` or `@torvalds`"
    )
    await upd.message.reply_text(welcome_message, parse_mode="Markdown")


def build_graphql_query(username: str) -> str:
    """Construct the GraphQL query for GitHub user data"""
    return f"""
    {{
        user(login: "{username}") {{
            name
            login
            avatarUrl
            bio
            contributionsCollection(from: "{ONE_YEAR_AGO}") {{
                totalCommitContributions
                totalIssueContributions
                totalPullRequestContributions
                totalPullRequestReviewContributions
                totalRepositoriesWithContributedCommits
                commitContributionsByRepository(maxRepositories: 5) {{
                    repository {{
                        nameWithOwner
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
            starredRepositories(first: 10) {{
                totalCount
            }}
            followers {{
                totalCount
            }}
            following {{
                totalCount
            }}
        }}
    }}
    """


async def fetch_github_data(username: str) -> Dict[str, Any]:
    """Fetch GitHub user data from the API"""
    query = build_graphql_query(username)

    try:
        response = requests.post(
            GITHUB_API_URL,
            json={"query": query},
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            error_messages = [e["message"] for e in data["errors"]]
            raise GitHubAPIError(f"GraphQL Error: {', '.join(error_messages)}")

        if not data.get("data", {}).get("user"):
            raise GitHubAPIError("User not found or no data available")

        return data["data"]["user"]

    except requests.exceptions.RequestException as e:
        logger.error(f"GitHub API request failed: {e}")
        raise GitHubAPIError("Failed to fetch data from GitHub. Please try again later.")


def format_report(user_data: Dict[str, Any]) -> str:
    """Format the GitHub user data into a readable report"""
    username = user_data.get("login", "N/A")
    name = user_data.get("name", username)
    bio = user_data.get("bio", "No bio available")
    stars = user_data.get("starredRepositories", {}).get("totalCount", 0)
    followers = user_data.get("followers", {}).get("totalCount", 0)
    following = user_data.get("following", {}).get("totalCount", 0)

    contributions = user_data.get("contributionsCollection", {})
    commits = contributions.get("totalCommitContributions", 0)
    issues = contributions.get("totalIssueContributions", 0)
    prs = contributions.get("totalPullRequestContributions", 0)
    reviews = contributions.get("totalPullRequestReviewContributions", 0)
    repos_contributed = contributions.get("totalRepositoriesWithContributedCommits", 0)

    top_repos = []
    for repo_data in contributions.get("commitContributionsByRepository", [])[:3]:
        repo = repo_data["repository"]
        contributions = repo_data["contributions"]["totalCount"]
        top_repos.append(f"• {repo['nameWithOwner']} (⭐ {repo['stargazerCount']}, commits: {contributions})")

    report = f"""
<b>{name}'s GitHub Report</b> (@{username})
{bio}

📊 <b>Activity (last year)</b>
Commits: <code>{commits}</code>
Issues: <code>{issues}</code>
PRs: <code>{prs}</code>
Reviews: <code>{reviews}</code>
Repos contributed to: <code>{repos_contributed}</code>

🌟 <b>Stars given</b>: <code>{stars}</code>
👥 <b>Followers</b>: <code>{followers}</code> | <b>Following</b>: <code>{following}</code>

<b>Top Contributed Repos</b>
{"".join(top_repos) if top_repos else "No recent contributions"}

<i>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>
"""
    return report.strip()


async def handle_username(upd: Update, ctx: CallbackContext) -> None:
    """Handle incoming GitHub username"""
    username = upd.message.text.strip('@')

    try:
        await upd.message.reply_chat_action("typing")
        user_data = await fetch_github_data(username)
        report = format_report(user_data)

        reply_markup = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔗 Share Report",
                                 url=f"https://t.me/share/url?url=Check out @{username}'s GitHub stats!")
        ]])

        await upd.message.reply_html(report, reply_markup=reply_markup)

    except GitHubAPIError as e:
        await upd.message.reply_text(f"❌ Error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await upd.message.reply_text("❌ An unexpected error occurred. Please try again later.")


async def error_handler(upd: Update, ctx: CallbackContext) -> None:
    """Log errors and notify user"""
    logger.error(f"Update {upd} caused error: {ctx.error}")

    if upd.message:
        await upd.message.reply_text("❌ An error occurred. Please try again later.")


def main() -> None:
    """Start the bot"""
    application = Application.builder().token(TG_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_username))

    application.add_error_handler(error_handler)

    logger.info("Bot is running...")
    application.run_polling()


if __name__ == '__main__':
    main()
