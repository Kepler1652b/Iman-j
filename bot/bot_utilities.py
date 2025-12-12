import logging
from telegram import Bot
from telegram.error import TelegramError
from typing import Optional,List
from html import escape
import httpx
from bot.config_loader import CHANNEL_ID

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramMessageSender:
    """
    Send formatted messages with images to Telegram
    """
    
    def __init__(self, bot_token: str):
        """
        Initialize Telegram bot
        
        Args:
            bot_token: Your Telegram bot token from @BotFather
        """
        self.bot = Bot(token=bot_token)
        
    async def send_message_with_image(
        self,
        chat_id: str,
        title: str,
        content: str,
        link:str,
        image_url: Optional[str] = None,
        parse_mode: str = "HTML"
    ) -> bool:
        """
        Send a formatted message with image
        
        Args:
            chat_id: Chat ID or channel username (e.g., "@channelname" or "123456789")
            title: Message title
            content: Message content/description
            image_url: URL of the image to send
            parse_mode: "HTML", "Markdown", or "MarkdownV2"
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format the message
            if parse_mode == "HTML":
                message_text = self._format_html(title, content,link)
            elif parse_mode == "Markdown":
                message_text = self._format_markdown(title, content)
            else:
                message_text = f"Title: {title}\n\nContent:\n{content}"
            
            # Send with image if provided
            if image_url:
                await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=image_url,
                    caption=message_text,
                    parse_mode=parse_mode if parse_mode != "plain" else None
                )
            else:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text=message_text,
                    parse_mode=parse_mode if parse_mode != "plain" else None
                )
            
            logger.info(f"Message sent successfully to {chat_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def _format_html(self, title: str, content: str,link:str) -> str:
        """Format message with HTML"""
        link = escape(link)
        link =f'<a href="{link}">لینک خبر</a>'
        content = escape(content)
        title = escape(title)
        return f'<b>📌 {title}</b>\n\n{content}\n\n{link}\n\n @newsscrape کانال ما '
    
    def _format_markdown(self, title: str, content: str) -> str:
        """Format message with Markdown"""
        return f"*📌 {title}*\n\n{content}"
    







# Fetch data from the API
def fetch_data_from_api(endpoint):
    try:
        response = httpx.get(endpoint)
        response.raise_for_status()  # Check if the request was successful
        return response.json()  # Returns the response as a JSON object
    except httpx.exceptions.RequestException as e:
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

