# Reddit Telegram Bot

A powerful Telegram bot that allows users to post content directly to Reddit, supporting multiple media types and subreddit-specific features.

## Features

- 🔐 OAuth2 Authentication with Reddit
- 📝 Create text posts
- 🖼️ Upload images and videos
- 🔗 Share URLs
- 🏷️ Support for subreddit flairs
- 💬 Custom post titles and descriptions
- 📱 Intuitive conversation-based interface
- 🔄 Persistent user sessions
- 🎯 Subreddit-specific posting requirements

## Prerequisites

- Python 3.7+
- MongoDB instance
- Reddit API credentials
- Telegram Bot Token

## Installation

1. Clone the repository:
```bash
git clone https://github.com/viperadnan-git/reddit-telegram-bot.git
cd reddit-telegram-bot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following variables:
```bash
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
MONGO_URI=your_mongodb_connection_string
TEMP_DIR=tmp  # Optional, defaults to 'tmp'
```

## Configuration

### Reddit API Setup

1. Go to [Reddit's App Preferences](https://www.reddit.com/prefs/apps)
2. Create a new application
3. Select "web" as the application type
4. Set the redirect URI to your OAuth callback URL
5. Note down the client ID and client secret

### Telegram Bot Setup

1. Talk to [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot using `/newbot`
3. Copy the provided bot token

## Usage

1. Start the bot:
```bash
python -m src
```

2. In Telegram, start a conversation with your bot

3. Available commands:
- `/start` - Initialize the bot
- `/login` - Authenticate with Reddit
- Send any text, image, or video to start creating a post

## Project Structure

The project follows a modular architecture:

```
src/
├── __init__.py          # Logger configuration
├── __main__.py          # Application entry point
├── config.py            # Environment configuration
├── constant.py          # Conversation states
├── database.py          # MongoDB interface
├── enums.py            # Media type enums
├── handlers/           # Command handlers
│   ├── login.py       # Authentication handlers
│   └── post.py        # Posting handlers
├── models/            # Data models
│   └── reddit_post.py # Post structure
├── modules/           # Core functionality
│   ├── bot_context.py    # Bot context
│   ├── decorators.py     # Auth decorators
│   └── reddit_manager.py # Reddit API wrapper
└── utils.py           # Helper functions
```

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram Bot API wrapper
- [PRAW](https://github.com/praw-dev/praw) for the Reddit API wrapper
- [pymongo](https://github.com/mongodb/mongo-python-driver) for MongoDB integration

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/viperadnan-git/reddit-telegram-bot/issues).