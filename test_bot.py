import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bot import start, github_info, format_user_info

@pytest.mark.asyncio
async def test_start_command():
    update = AsyncMock()
    context = MagicMock()
    await start(update, context)
    update.message.reply_text.assert_called_once()

@pytest.mark.asyncio
async def test_github_info_no_username():
    update = AsyncMock()
    context = MagicMock()
    context.args = []
    await github_info(update, context)
    update.message.reply_text.assert_called_with("Использование: /github <username>")

@pytest.mark.asyncio
@patch('bot.requests.get')
async def test_github_info_user_found(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'login': 'testuser',
        'name': 'Test User',
        'html_url': 'https://github.com/testuser',
        'public_repos': 15,
        'followers': 100,
        'following': 50,
        'created_at': '2020-01-01T00:00:00Z'
    }
    mock_get.return_value = mock_response

    update = AsyncMock()
    context = MagicMock()
    context.args = ['testuser']
    
    await github_info(update, context)
    update.message.reply_text.assert_called()

@pytest.mark.asyncio
@patch('bot.requests.get')
async def test_github_info_user_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    update = AsyncMock()
    context = MagicMock()
    context.args = ['unknownuser']
    
    await github_info(update, context)
    update.message.reply_text.assert_called_with("⚠️ Пользователь 'unknownuser' не найден")

def test_format_user_info():
    user_data = {
        'login': 'testuser',
        'name': 'Test User',
        'html_url': 'https://github.com/testuser',
        'public_repos': 15,
        'followers': 100,
        'following': 50,
        'created_at': '2020-01-01T00:00:00Z'
    }
    formatted = format_user_info(user_data)
    assert "👤 Test User" in formatted
    assert "📂 Репозитории: 15" in formatted
    assert "⭐ Подписчики: 100" in formatted
