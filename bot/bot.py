"""
Telegram Bot for sending formatted messages with images
Supports both direct messages and channel posts
"""

import logging
import json
from urllib.parse import unquote
from .templats.admin import AdminLayout
from .templats.base import Layout
from .bot_utilities import (
    TelegramMessageSender,format_episode_message,
    format_movie_message,format_series_message,
    fetch_data_from_api
    )
from database.db import PostCRUD,engine
from .config_loader import ADMINS,TOKEN,CHANNEL_ID
from sqlmodel import Session
from datetime import time, timezone, timedelta
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode
from telegram import Update

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)


# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
skip = 0
IRAN_TZ = timezone(timedelta(hours=3, minutes=30))

class LayoutContianer:
    def __init__(self):
        self.layout_map : dict= {
            "admin":AdminLayout,
            # "news":NewsLayout,
        }

    def resolve(self,layout:str) -> Layout:
        layout_:Layout = self.layout_map.get(layout)
        if layout_:
            return layout_().render()
        raise ValueError("Layout not supported ")










       

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




async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = LayoutContianer().resolve('admin')
    if update.effective_user.username in ADMINS:
        await update.message.reply_text(f'Hello {update.effective_user.first_name}',reply_markup=reply_markup)
    else:
        await update.message.reply_text(f'You dont have a premission to start {update.effective_user.first_name} please contact admin ',)


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    datastr = json.loads(query.data)
    data = json.loads(datastr)

    await query.message.reply_text("N/A")









async def send_with_limit(context: ContextTypes.DEFAULT_TYPE):
    global skip
    message_sender = TelegramMessageSender(TOKEN)
    limit = context.job.data.get("limit")
    with Session(engine) as session:
        CRUDresult = PostCRUD.get_all(session,limit=limit,skip=skip)
        posts = CRUDresult.data
        
        for post in posts:
            if post.sent != True:
                await message_sender.send_message_with_image(chat_id=CHANNEL_ID,title=post.title
                                                ,content=post.summery,image_url=post.image
                                                ,link=unquote(post.link))
                post.sent = True
                session.add(post)
        session.commit()
    skip += 5

    
def run():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))

    app.job_queue.run_daily(
        callback=send_with_limit,
        time=time(hour=17, minute=0, second=0, tzinfo=IRAN_TZ),
        data={'limit': 5},
        name='daily_5pm_job'
    )
    app.job_queue.run_repeating(
        callback=send_data_to_telegram,
        interval=21600,
        first=5
    )

    logger.info("✅ Scheduled: Daily at 5:00 PM Iran time (UTC+3:30)")
    print("🚀 Bot started.")
    app.run_polling()

if __name__ == "__main__":
    run()