# Automated Cryptocurrency Alerts Bot

This project is a Python-based Selenium bot that monitors new token listings on [NeoBullX](https://neo.bullx.io/), evaluates the social credibility of the associated Twitter (X) account, and sends alerts via Telegram for coins meeting specific hype indicators (e.g., high follower count, recent tweet mentioning the contract address).

## Features

- Scrapes new token listings from NeoBullX  
- Extracts associated Twitter/X profile  
- Verifies:
  - Follower count exceeds 10K  
  - Contract address is mentioned in recent tweets  
- Pulls real-time market cap and liquidity data  
- Sends formatted alerts to a Telegram channel  
- Avoids duplicates via local JSON storage  
- Handles navigation timeouts and dynamic Twitter content

## Why Web Scraping?

Instead of relying on expensive or rate-limited APIs (like Twitter/X, CoinGecko, or Solana RPC), this bot uses Selenium-based browser automation to gather all data directly from the rendered web pages.

Advantages:
- Bypasses API authentication and rate limits  
- Works for small-cap tokens not listed on major aggregators  
- Reduces cost by avoiding paid API tiers

## Setup

### 1. Install Required Python Packages

```bash
pip install selenium requests
```

### 2. Install Chrome and ChromeDriver

- Download and install [Google Chrome](https://www.google.com/chrome/)
- Download [ChromeDriver](https://chromedriver.chromium.org/downloads) matching your Chrome version

Ensure your system path points to the correct versions.

### 3. Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Run `/newbot` and follow the prompts
3. Copy the bot API token

### 4. Create a Telegram Channel

1. Create a new Telegram channel
2. Add your bot as an admin of the channel
3. Retrieve your channel ID:
   - For public channels, use `@your_channel_username`
   - For private channels, use `chat_id` (e.g., `-100XXXXXXXXXX`)

### 5. Configure the Script

Edit the script to reflect your setup:

```python
chrome_driver_path = r"PATH\TO\chromedriver.exe"
chrome_binary_path = r"PATH\TO\chrome.exe"
user_data_dir = r"PATH\TO\chrome-user-data"

api_token = "YOUR_TELEGRAM_BOT_API_TOKEN"
channel_id = "@yourchannel"  # or "-1001234567890" for private
```

## Running the Bot

```bash
python bot_script.py
```

The bot will:
- Launch a Chrome window using your saved session (important for Twitter access)
- Scrape tokens listed on NeoBullX
- Visit each Twitter account and perform validation checks
- Extract real-time market cap and liquidity
- Send a Telegram alert if all checks pass

## Telegram Alert Format

```
$TICKER | Token Name
MC: $45.23K | L: $10.05K
NeoBullX Coin Link: https://neo.bullx.io/...
Twitter Link: https://x.com/tokenproject
TrenchBot Held Percentage: Not Checked
```

## File Structure

```
crypto-alerts/
├── bot_script.py
├── processed_coins.json
├── chromedriver.exe
├── chrome.exe
└── chrome-user-data/
```

## Notes

- You must be logged into Twitter/X in the Chrome profile being used
- Dynamic content on NeoBullX and Twitter means XPath selectors may need updates
- If you're running this at scale, consider session monitoring or rotating IPs

## Customization Ideas

- Filter by specific chains (e.g., only Solana)
- Detect anti-bot measures or honeypots using external sources
- Schedule regular refresh intervals and summaries

## License

MIT License.  
Use this project at your own discretion. Be respectful of platform terms of service.
