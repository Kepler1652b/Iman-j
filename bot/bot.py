"""
Telegram Bot for sending formatted messages with images
Supports both direct messages and channel posts
"""

import logging
import json
from urllib.parse import unquote

from .templats.admin import AdminLayout
from .templats.base import Layout
from .bot_utilities import TelegramMessageSender
from database.db import PostCRUD,engine
from .config_loader import ADMINS,TOKEN,CHANNEL_ID
from sqlmodel import Session
from datetime import time, timezone, timedelta
from telegram.ext import Application, CommandHandler, ContextTypes
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









async def send_with_limit(context):
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


    logger.info("✅ Scheduled: Daily at 5:00 PM Iran time (UTC+3:30)")
    print("🚀 Bot started.")
    app.run_polling()

if __name__ == "__main__":
    run()