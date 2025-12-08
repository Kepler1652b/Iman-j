"""
Telegram Bot for sending formatted messages with images
Supports both direct messages and channel posts
"""
from urllib.parse import unquote
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
# from bot_utilities import TelegramMessageSender
from .templats.admin import AdminLayout
from .templats.base import Button,Layout
from database.db import PostCRUD,engine

from sqlmodel import Session
# from 
from telegram import (
    Update,


)

TOKEN = ''

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


# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)



async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = LayoutContianer().resolve('admin')
    await update.message.reply_text(f'Hello {update.effective_user.first_name}',reply_markup=reply_markup)





import json


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # """Handle inline button presses"""
    query = update.callback_query
    await query.answer()
    datastr = json.loads(query.data)
    data = json.loads(datastr)

    await query.message.reply_text(f"foad {data['class']}")


from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "7322296332:AAH8sHGUv11XS_Ka7TceRYSbddibAfaumsA"
CHANNEL_ID = "-1003281525466"

# async def send_ltp(context: ContextTypes.DEFAULT_TYPE):
#     """Send LTP to channel"""
#     try:
#         await context.bot.send_message(
#             chat_id=CHANNEL_ID,
#             text=f"📊 LTP Update\n⏰ {datetime.now().strftime('%H:%M:%S')}"
#         )
#         logger.info("✅ LTP sent")
#     except Exception as e:
#         logger.error(f"❌ Error: {e}")

# async def cmd_start(update, context: ContextTypes.DEFAULT_TYPE):
#     await update.message.reply_text(
#         f"Hello {update.effective_user.first_name}!"
#     )
from .bot_utilities import TelegramMessageSender
from functools import partial


async def sendd(context):
    t = TelegramMessageSender('7322296332:AAH8sHGUv11XS_Ka7TceRYSbddibAfaumsA')
    with Session(engine) as session:
        CRUDresult = PostCRUD.get_all(session,limit=10)
        posts = CRUDresult.data

        for post in posts:
         await t.send_message_with_image(chat_id=CHANNEL_ID,title=post.title
                                        ,content=post.summery,image_url=post.image
                                        ,link=unquote(post.link))
        

def run():
    app = Application.builder().token("7322296332:AAH8sHGUv11XS_Ka7TceRYSbddibAfaumsA").build()
    
    app.add_handler(CommandHandler("start", cmd_start))


    app.job_queue.run_repeating(
        callback=sendd,
        interval=30,  # seconds
        first=10  # wait 10 seconds before first run
    )
    
    logger.info("✅ Job scheduled - will run every 60 seconds")
    print("🚀 Bot started.")
    app.run_polling()

if __name__ == "__main__":
    run()