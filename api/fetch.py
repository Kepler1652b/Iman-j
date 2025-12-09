import logging
import requests
from telegram import Update, Bot
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your bot token and channel ID
TOKEN = "8001927972:AAFMgUbtKlGUle7Z0N_g_qTLoxZ1LC5luUs"  # Replace with your bot token
CHANNEL_ID = "@cinema_news_test"  # Replace with your channel username (without '@' symbol in code)

# Fetch data from the API
def fetch_data_from_api(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()  # Check if the request was successful
        return response.json()  # Returns the response as a JSON object
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data: {e}")
        return None

# Format movie data to send as Telegram message
def format_movie_message(data):
    if data["type"] == "movie":
        message = f"<b>{data['title']}</b>\n\n"  # Title in bold
        message += f"📅 <i>سال:</i> {data['year']}\n"
        message += f"🕒 <i>مدت زمان:</i> {data['duration']}\n"
        message += f"⭐ <i>امتیاز IMDB:</i> {data['imdb']}\n"
        message += f"📍 <i>کشور:</i> {data['countries'][0]['title']}\n"
        message += f"🎭 <i>بازیگران:</i> {', '.join([actor['name'] for actor in data['actors']])}\n"
        message += f"📝 <i>توضیحات:</i> {data['description']}\n"
        
        # Add trailer if available
        trailer_url = data.get("trailer", {}).get("url", None)
        if trailer_url:
            message += f"🎬 <a href='{trailer_url}'>تماشای تریلر</a>\n"
        
        # Add channel username at the end
        message += f"\n\n🔗 {CHANNEL_ID}"
        
        return message
    return "داده ای برای ارسال وجود ندارد."

# Format series data to send as Telegram message
def format_series_message(data):
    if data["type"] == "serie":
        message = f"<b>{data['title']}</b>\n\n"  # Title in bold
        message += f"📅 <i>سال:</i> {data['year']}\n"
        message += f"🕒 <i>مدت زمان:</i> {data['duration']}\n"
        message += f"⭐ <i>امتیاز IMDB:</i> {data['imdb']}\n"
        message += f"📍 <i>کشور:</i> {data['countries'][0]['title']}\n"
        message += f"🎭 <i>بازیگران:</i> {', '.join([actor['name'] for actor in data['actors']])}\n"
        message += f"📝 <i>توضیحات:</i> {data['description']}\n"
        
        # Add season count for series
        message += f"📺 <i>فصل ها:</i> {data.get('season_count', 'N/A')}\n"
        
        # Add trailer if available
        trailer_url = data.get("trailer", {}).get("url", None)
        if trailer_url:
            message += f"🎬 <a href='{trailer_url}'>تماشای تریلر</a>\n"
        
        # Add channel username at the end
        message += f"\n\n🔗 {CHANNEL_ID}"
        
        return message
    return "داده ای برای ارسال وجود ندارد."

# Format episode data to send as Telegram message
def format_episode_message(data):
    # Check if 'episode' exists in the data
    if "episode" in data:
        # Begin constructing the message
        message = f"<b>{data['title']}</b>\n\n"
        message += f"📅 <i>سال:</i> {data['year']}\n"
        message += f"🕒 <i>مدت زمان:</i> {data['duration']}\n"
        message += f"⭐ <i>امتیاز IMDB:</i> {data['imdb']}\n"
        message += f"📍 <i>کشور:</i> {data['countries'][0]['title']}\n"
        
        # Add actors
        message += f"🎭 <i>بازیگران:</i> {', '.join([actor['name'] for actor in data['actors']])}\n"
        
        # Add description
        message += f"📝 <i>توضیحات:</i> {data['description']}\n"
        
        # Add episode specific info
        episode = data["episode"]
        message += f"🎬 <i>قسمت:</i> {episode['title']}\n"
        message += f"📝 <i>توضیحات قسمت:</i> {episode['description']}\n"
        message += f"📺 <i>فصل:</i> {episode['season']['title']}\n"
        
        # Add trailer link
        trailer_url = data.get("trailer", {}).get("url", None)
        if trailer_url:
            message += f"🎬 <a href='{trailer_url}'>تماشای تریلر</a>\n"
        
        # Add channel link
        message += f"\n\n🔗 {CHANNEL_ID}"

        return message
    return "داده ای برای ارسال وجود ندارد."


       

# Send data to the Telegram channel
async def send_to_telegram(data, bot, channel_id):
    message = None
    if data["type"] == "movie":
        message = format_movie_message(data)
    elif data["type"] == "serie":
        message = format_series_message(data)
    elif "episode" in data:  # Handling episode data
        message = format_episode_message(data)
    
    if message:
        image_url = data.get('image', None)
        if image_url:
            await bot.send_photo(chat_id=channel_id, photo=image_url, caption=message, parse_mode=ParseMode.HTML)
        else:
            await bot.send_message(chat_id=channel_id, text=message, parse_mode=ParseMode.HTML)
        logger.info("Message sent successfully.")
    else:
        logger.error("No message to send.")


# Command to fetch data from API and send to Telegram
async def send_data_to_telegram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    movie_id = 20518  # Example movie ID
    series_id = 20512  # Example series ID
    episode_id = 132246  # Example episode ID
    
    # Fetch movie data
    movie_data = fetch_data_from_api(f"http://localhost:5000/api/movies/{movie_id}")
    if movie_data:
        await send_to_telegram(movie_data, context.bot, CHANNEL_ID)
    else:
        await update.message.reply_text("Error fetching movie data.")
    
    # Fetch series data
    series_data = fetch_data_from_api(f"http://localhost:5000/api/series/{series_id}")
    if series_data:
        await send_to_telegram(series_data, context.bot, CHANNEL_ID)
    else:
        await update.message.reply_text("Error fetching series data.")
    
    # Fetch episode data
    episode_data = fetch_data_from_api(f"http://localhost:5000/api/episodes/{episode_id}")
    if episode_data:
        await send_to_telegram(episode_data, context.bot, CHANNEL_ID)
    else:
        await update.message.reply_text("Error fetching episode data.")

# Set up the Telegram bot
def run():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("send_api_data", send_data_to_telegram))
    app.run_polling()

if __name__ == "__main__":
    run()
