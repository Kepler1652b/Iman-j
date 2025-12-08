from telegram import Bot, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.error import TelegramError
import json
from typing import Optional,List
import logging
from html import escape

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
    



def load_data_from_json(file_path: str) -> List[dict]:
    """Load message data from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Handle different JSON structures
    if isinstance(data, dict) and 'articles' in data:
        return data['articles']
    elif isinstance(data, list):
        return data
    else:
        return [data]


def format_movie_message(movie_data: dict) -> dict:
    """
    Format movie data for Telegram message
    
    Args:
        movie_data: Dict with movie information
    
    Returns:
        dict: Formatted message with title, content, image_url
    """
    title = movie_data.get('title', 'Untitled')
    
    # Build content
    content_parts = []
    
    if 'description' in movie_data:
        content_parts.append(movie_data['description'])
    
    if 'author' in movie_data:
        content_parts.append(f"\n👤 Author: {movie_data['author']}")
    
    if 'published_date' in movie_data:
        content_parts.append(f"📅 Date: {movie_data['published_date']}")
    
    if 'source_url' in movie_data:
        content_parts.append(f"\n🔗 Read more: {movie_data['source_url']}")
    
    content = '\n'.join(content_parts)
    
    return {
        'title': title,
        'content': content,
        'image_url': movie_data.get('image_url')
    }
