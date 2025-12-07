"""
Telegram Bot for sending formatted messages with images
Supports both direct messages and channel posts
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from bot_utilities import TelegramMessageSender
from templats.admin import AdminLayout
from templats.base import Button,Layout

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


def run():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    print("Bot started.")
    app.run_polling()



run()