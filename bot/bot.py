from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,

)

TOKEN = "7816359510:AAEVjnXCMAWigq8e3zAUEMDPj8FPPzMsiWk"



# def run():
#     app = Application.builder().token(TOKEN).build()
#     app.add_handler(CommandHandler("start", cmd_start))
#     print("Bot started.")
#     app.run_polling()


"""
Telegram Bot for sending formatted messages with images
Supports both direct messages and channel posts
"""

import asyncio
from typing import Optional, List
import json
from telegram import Bot, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.error import TelegramError
import logging

# Setup logging
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
                message_text = self._format_html(title, content)
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
    
    def _format_html(self, title: str, content: str) -> str:
        """Format message with HTML"""
        return f"<b>📌 {title}</b>\n\n{content}"
    
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

from sqlmodel import Session
from database.db import PostCRUD,engine

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sender = TelegramMessageSender(TOKEN)
    with Session(engine) as se:
        for post in PostCRUD.get_all(se):
            await sender.send_message_with_image(
                chat_id=update.effective_user.id,
                title=post.title,
                content=post.summery[:150]+'...',
                image_url=post.image
    )

def run():



    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    print("Bot started.")
    app.run_polling()
