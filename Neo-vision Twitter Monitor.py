import random
import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Path to your ChromeDriver and Chrome binary
chrome_driver_path = r"C:\Users\user\Documents\Code\Twitter follow monitor bot\chromedriver-win64\chromedriver.exe"
chrome_binary_path = r"C:\Users\user\Documents\Code\Twitter follow monitor bot\chrome-win64\chrome.exe"

# Path for user data directory (to save cache and session cookies)
user_data_dir = r"C:\Users\user\Documents\Code\Twitter follow monitor bot\chrome-user-data"

# JSON file to store processed coins
processed_coins_file = "processed_coins.json"

# Telegram Bot API Token and Channel ID
api_token = ""
channel_id = ""  # Channel ID or username (e.g., @my_channel)


def random_sleep(min_sleep=1, max_sleep=2):
    sleep_time = random.uniform(min_sleep, max_sleep)
    time.sleep(sleep_time)


def create_chrome_driver():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.binary_location = chrome_binary_path  # Ensure the correct Chrome binary is used
    options.add_argument("--start-maximized")
    options.add_argument("--remote-debugging-port=9222")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def load_processed_coins():
    """Load processed coins from JSON file."""
    if os.path.exists(processed_coins_file):
        with open(processed_coins_file, 'r') as file:
            return set(json.load(file))
    return set()


def save_processed_coins(processed_coins):
    """Save processed coins to JSON file."""
    with open(processed_coins_file, 'w') as file:
        json.dump(list(processed_coins), file)


def extract_coin_details(driver, processed_neobull_links):
    """Scrape Neo BullX to get all available coin details while filtering out processed and duplicate links."""

    # Wait for the page to load and coin cards to be visible
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "some-card"))
    )

    coin_cards = driver.find_elements(By.CLASS_NAME, "some-card")
    print(f"Found {len(coin_cards)} coin cards on the page.")

    coins = []
    extracted_links = set()  # To track duplicates within the current iteration

    for card in coin_cards:
        try:
            # Extract the NeoBull link early to filter duplicates
            neobull_link = card.find_element(By.CSS_SELECTOR, "a[href*='/terminal?chainId=']").get_attribute('href')

            # Skip if this link has already been processed or extracted during this iteration
            if neobull_link in processed_neobull_links or neobull_link in extracted_links:
                print(f"Skipping duplicate or already processed link: {neobull_link}")
                continue

            # Mark this link as extracted
            extracted_links.add(neobull_link)

            # Extract the Twitter handle and skip coins without one
            twitter_handle_elements = card.find_elements(By.XPATH, ".//a[contains(@href, 'x.com') and .//span[contains(@class, 'w-5 h-5')]]")
            if not twitter_handle_elements:
                print("No Twitter link found for this coin. Skipping.")
                continue

            original_twitter_url = twitter_handle_elements[0].get_attribute('href')
            twitter_handle_link = original_twitter_url

            # the original URL = the twitter handle link unless it is a /status/ link
            if '/status/' in original_twitter_url:
                twitter_handle_link = original_twitter_url.split('/status/')[0]

            print(f"Extracted Twitter Handle: {twitter_handle_link} from URL: {original_twitter_url}")  # Debug print

            # Extract the contract address
            contract_address = neobull_link.split('address=')[1]  # Already fetched earlier from neobull_link
            print(f"Extracted Contract Address: {contract_address}")  # Debug print

            # Extract other coin details
            coin_name = card.find_element(By.CSS_SELECTOR, "span.font-normal.text-grey-200").text
            coin_ticker = card.find_element(By.CSS_SELECTOR, "span.text-sm").text

            # Append to the coins list after filtering duplicates
            coins.append({
                "contract_address": contract_address,
                "coin_name": coin_name,
                "coin_ticker": coin_ticker,
                "twitter_handle_link": twitter_handle_link,
                "original_twitter_url" : original_twitter_url,
                "neobull_link": neobull_link
            })

        except Exception as e:
            print(f"Error extracting details for a coin: {e}")

    print(f"Extracted {len(coins)} coins.")
    return coins



def get_twitter_followers(twitter_handle_link, original_twitter_url, coin_contract_address, coin_name, coin_ticker, driver):
    driver.get(twitter_handle_link)

    try:
        WebDriverWait(driver, 2.5).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'verified_followers')]//span[contains(@class, 'css-1jxf684') and contains(@class, 'r-bcqeeo')]"))
        )

        follower_element = driver.find_element(By.XPATH, "//a[contains(@href, 'verified_followers')]//span[contains(@class, 'css-1jxf684') and contains(@class, 'r-bcqeeo')]")
        followers_raw = follower_element.text.replace(",", "")

        if 'M' in followers_raw or 'K' in followers_raw:
            is_above_10k = True
        else:
            is_above_10k = False

        print(f"Debug: Coin '{coin_name}' (Ticker: {coin_ticker}) | Contract Address: {coin_contract_address} | Twitter Handle Link: {twitter_handle_link} | Original URL: {original_twitter_url} | Above 10k: {is_above_10k} ")

        return is_above_10k

    except Exception as e:
        print(f"Error fetching Twitter data for {twitter_handle_link}: {e}")
        return False

def check_recent_tweets_for_contract(driver, twitter_handle_link, contract_address):
    """Check the most recent 10 tweets for the presence of the contract address."""
    try:
        # Load the Twitter page
        driver.get(twitter_handle_link)

        # Wait for tweets to load (you might need to adjust the wait conditions based on actual structure)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//article[contains(@role, 'article')]"))
        )

        # Get the first 10 tweet elements
        tweets = driver.find_elements(By.XPATH, "//article[contains(@role, 'article')]")[:10]

        # Check each tweet for the contract address
        for tweet in tweets:
            tweet_text = tweet.text
            if contract_address in tweet_text:
                print(f"Contract address found in recent tweet: {tweet_text}")
                return True
        
        print("No recent tweets contain the contract address.")
        return False

    except Exception as e:
        print(f"Error checking recent tweets: {e}")
        return False
    
def extract_market_cap_and_liquidity(driver, coin):
    """Extracts market cap and liquidity from the NeoBull link."""
    driver.get(coin['neobull_link'])
    try:
        # Wait until the "Mkt Cap" element appears
        WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Mkt Cap']"))
        )

        # Extract Market Cap and Liquidity
        market_cap = driver.find_element(By.XPATH, "//span[text()='Mkt Cap']/following-sibling::span").text
        liquidity = driver.find_element(By.XPATH, "//span[text()='Liquidity']/following-sibling::span").text

    except Exception as e:
        print(f"Error extracting market cap and liquidity: {e}")
        market_cap, liquidity = "N/A", "N/A"

    return market_cap, liquidity


    
def send_telegram_message(coin_name, coin_ticker, neobull_link, original_twitter_url, market_cap, liquidity, trench_held_percentage):
    message = f"{coin_ticker} | {coin_name}\n"
    message += f"MC:{market_cap} | L: {liquidity}\n"
    message += f"NeoBullX Coin Link: {neobull_link}\n"
    message += f"Twitter Link: {original_twitter_url}\n"
    message += f"TrenchBot Held Percentage: {trench_held_percentage}"
    
    telegram_url = f"https://api.telegram.org/bot{api_token}/sendMessage"
    params = {
        'chat_id': channel_id,
        'text': message
    }
    response = requests.get(telegram_url, params=params)
    
    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message: {response.text}")

def send_error_notification(message):
    """Send an error notification to Telegram."""
    error_message = f"🚨 Bot Error:\n{message}"
    telegram_url = f"https://api.telegram.org/bot{api_token}/sendMessage"
    params = {
        'chat_id': channel_id,
        'text': error_message
    }
    response = requests.get(telegram_url, params=params)
    
    if response.status_code == 200:
        print("Error notification sent successfully!")
    else:
        print(f"Failed to send error notification: {response.text}")

def monitor_bullx():
    driver = create_chrome_driver()
    processed_neobull_links = load_processed_coins()
    driver.get("https://neo.bullx.io/")

    while True:
        try:
            # Navigate and extract coin details
            print("Checking Neo BullX page...")
            WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, "grid")))

            # Extract coins with filtering handled in the extract_coin_details function
            coins = extract_coin_details(driver, processed_neobull_links)
            apply_delay = len(coins) > 15 #check if there are high initial amount of coins to process at once

            for coin in coins:
                try:
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])

                    if apply_delay:
                        random_sleep(1.5,3) #prevent twitter rate limits if there are high amount of coins to process

                    if get_twitter_followers(coin['twitter_handle_link'], coin['original_twitter_url'], coin['contract_address'], coin['coin_name'], coin['coin_ticker'], driver):
                        if check_recent_tweets_for_contract(driver, coin['twitter_handle_link'], coin['contract_address']):
                            market_cap, liquidity = extract_market_cap_and_liquidity(driver, coin)
                            send_telegram_message(coin['coin_name'], coin['coin_ticker'], coin['neobull_link'] , coin['original_twitter_url'], market_cap, liquidity, "Not Checked")

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    processed_neobull_links.add(coin['neobull_link'])
                except Exception as e:
                    print(f"Error processing coin {coin['coin_name']}: {e}") 

            # Save updated processed links
            save_processed_coins(processed_neobull_links)
            random_sleep(1, 2)

        except TimeoutException:
            print("TimeoutException: Page load or extraction failed. Refreshing and retrying...")
            time.sleep(15)
            driver.get("https://neo.bullx.io/")
            driver.refresh()
            continue  # Restart the loop by refreshing the page
        except Exception as e:
            error_msg = f"Unexpected error in monitor loop: {e}"
            print(error_msg)
            send_error_notification(error_msg)
            break  # Break the loop if it's a severe error
    driver.quit()


monitor_bullx()
