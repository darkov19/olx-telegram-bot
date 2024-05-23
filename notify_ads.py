import os
import requests
import logging
import pickle
import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
API_URL = os.getenv("API_URL")

if not BOT_TOKEN or not CHAT_ID or not API_URL:
    logger.error("Missing environment variables: BOT_TOKEN, CHAT_ID, or API_URL")
    exit(1)

USER_API_URL = "https://www.olx.in/api/users/{user_id}"
AD_URL = "https://www.olx.in/item/{ad_id}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
}

# File to store notified ad IDs
notified_ads_file = 'notified_ads.pkl'

# Load previously notified ads
if os.path.exists(notified_ads_file):
    with open(notified_ads_file, 'rb') as f:
        notified_ads = pickle.load(f)
else:
    notified_ads = set()


def filter_user_data(user_data):
    if not user_data.get('dealer') and not user_data.get('is_business') and not user_data.get('is_phone_visible') and not user_data.get('phone') and not user_data.get('showroom_address'):
        return True
    return False


def fetch_user_data(user_id):
    user_url = USER_API_URL.format(user_id=user_id)
    try:
        response = requests.get(user_url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {})
        else:
            logger.error(f"Failed to fetch user data for user_id: {user_id}. Status code: {response.status_code}")
            return {}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching user data for user_id: {user_id}. Exception: {str(e)}")
        return {}


def fetch_ads():
    ads_data = {"ads": []}
    ads_data["previous_ads_count"] = len(notified_ads)

    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            data = response.json()
            ads_data["total_ads"] = len(data.get('data', []))
            total_filtered_ads = 0

            for item in data.get('data', []):
                user_id = item.get('user_id', '')
                user_data = fetch_user_data(user_id)
                if filter_user_data(user_data):
                    continue

                ad_id = item.get('ad_id', '')
                if ad_id in notified_ads:
                    continue

                ad_url = AD_URL.format(ad_id=ad_id)
                description = item.get('description', 'N/A')
                created_at = item.get('created_at', 'N/A')
                title = item.get('title', 'N/A')
                car_body_type = item.get('car_body_type', 'N/A')
                user_type = item.get('user_type', 'N/A')
                user_name = user_data.get('name', 'N/A')
                price = item.get('price', {}).get(
                    'value', {}).get('display', 'N/A')
                partner_code = item.get('partner_code', 'N/A')
                certified_car = item.get('certified_car', False)
                main_info = item.get('main_info', 'N/A')
                display_date = item.get('display_date', 'N/A')
                display_date = display_date.split("T")[0]

                ads_data["ads"].append({
                    'ad_id': ad_id,
                    'description': description,
                    'created_at': created_at,
                    'title': title,
                    'car_body_type': car_body_type,
                    'user_type': user_type,
                    'user_name': user_name,
                    'price': price,
                    'partner_code': partner_code,
                    'certified_car': certified_car,
                    'main_info': main_info,
                    'user_id': user_id,
                    'display_date': display_date,
                    'ad_url': ad_url
                })

                total_filtered_ads += 1

            ads_data["total_filtered_ads"] = total_filtered_ads
        else:
            logger.error(f"Failed to retrieve data. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        logger.error(f"Error making request: {str(e)}")

    return ads_data


async def send(bot, chat, msg):
    await bot.send_message(chat_id=chat, text=msg)


def send_notification(loop, bot, ad):
    message = (
        f"Title: {ad['title']}\n\n"
        f"Main Info: {ad['main_info']}\n\n"
        f"Price: {ad['price']}\n\n"
        f"Car Body Type: {ad['car_body_type']}\n\n"
        f"Description: {ad['description']}\n\n"
        f"Ad Post Date: {ad['display_date']}\n\n"
        f"Ad URL: {ad['ad_url']}\n\n"
    )

    logger.info(f"Sending notification for AD ID: {ad['ad_id']} ({ad['ad_url']})...")

    loop.run_until_complete(send(bot, CHAT_ID, message))

    notified_ads.add(ad['ad_id'])
    with open(notified_ads_file, 'wb') as f:
        pickle.dump(notified_ads, f)

    return 1


def notify_ads():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    bot = application.bot
    ads_data = fetch_ads()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    notified_ads_count = 0
    for ad in ads_data['ads']:
        notified_ads_count += send_notification(loop, bot, ad)

    if notified_ads_count > 0:
        loop.run_until_complete(send(bot, CHAT_ID, f"Total new ads sent: {notified_ads_count} [{ads_data['previous_ads_count']} ads sent earlier!]"))
    else:
        loop.run_until_complete(send(bot, CHAT_ID, f"No new ads found! [{ads_data['previous_ads_count']} ads sent earlier!]"))
        
    loop.close()


if __name__ == '__main__':
    notify_ads()
