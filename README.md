# OLX Bot

This project is an OLX bot designed to scrape specific car ads from the OLX website and send notifications via Telegram. The bot runs every 5 minutes using APScheduler.

## Features

- Scrapes specific car ads from OLX
- Filters ads based on user data
- Sends notifications via Telegram
- Runs every 5 minutes

## Setup

### Prerequisites

- Python 3.8+
- A Telegram bot token. You can get one by creating a bot with [BotFather](https://core.telegram.org/bots#botfather).

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/olx-bot.git
    cd olx-bot
    ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    Create a `.env` file in the root directory of the project and add the following variables:

    ```ini
    BOT_TOKEN=your-telegram-bot-token
    CHAT_ID=your-telegram-chat-id
    API_URL=your-olx-api-url
    ```

### Running the Bot Locally

1. Run the bot:

    ```sh
    python notify_ads.py
    ```

### Deploying with GitHub Actions

1. Ensure your repository has a `main` branch.

2. Add your secrets to the GitHub repository:

    - `BOT_TOKEN`
    - `CHAT_ID`
    - `API_URL`

3. Create a `.github/workflows/deploy.yml` file with the following content:

    ```yaml
    name: Notify Ads Bot

    on:
        schedule:
            - cron: "*/5 * * * *"
            
    jobs:
        notify_ads:
            runs-on: ubuntu-latest

        steps:
            - name: Checkout repository
              uses: actions/checkout@v3

            - name: Set up Python
              uses: actions/setup-python@v4
              with:
                  python-version: "3.9"

            - name: Install dependencies
              run: |
                  python -m pip install --upgrade pip
                  pip install requests apscheduler python-telegram-bot

            - name: Run the script
              env:
                  BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
                  CHAT_ID: ${{ secrets.CHAT_ID }}
                  API_URL: ${{ secrets.API_URL }}
              run: |
                  python -u notify_ads.py
                  git config user.name github-actions
                  git config user.email github-actions@github.com
                  git add .
                  git commit -m "crongenerated" || exit 0
                  git push
    ```

## How It Works

1. The bot fetches car ads from the specified OLX API URL.
2. It filters the ads based on user data (e.g., dealer, business, phone visibility).
3. It sends notifications for new ads to the specified Telegram chat.
4. It stores notified ad IDs in a pickle file to avoid duplicate notifications.
5. The bot runs every 5 minutes using APScheduler.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Python Telegram Bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [APScheduler](https://apscheduler.readthedocs.io/en/stable/)

---

Feel free to contribute to this project and enhance its functionality!

For any issues or questions, please open an issue on the GitHub repository.
