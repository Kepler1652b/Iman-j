"""
Telegram Bot for sending formatted messages with images
Supports direct messages and channel posts.
Fully dynamic: handles any new fields in the database.
"""

import logging
from urllib.parse import unquote
from datetime import time, timezone, timedelta

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from database.db import MovieCRUD, SerialCRUD, EpisodeCRUD, PostCRUD, safe_session, engine
from bot.config_loader import ADMINS, TOKEN, CHANNEL_ID
from bot.templats.admin import AdminLayout
from bot.templats.base import Layout
from bot.bot_utilities import TelegramMessageSender
from database.models import Episode  

# ------------------ Logging ------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

IRAN_TZ = timezone(timedelta(hours=3, minutes=30))
skip = 0

# ------------------ Layout Container ------------------
class LayoutContainer:
    def __init__(self):
        self.layout_map: dict = {
            "admin": AdminLayout,
        }

    def resolve(self, layout: str) -> Layout:
        layout_: Layout = self.layout_map.get(layout)
        if layout_:
            return layout_().render()
        raise ValueError("Layout not supported")


# ------------------ Dynamic Telegram Message ------------------
async def send_to_telegram(data: dict, bot, chat_id: int):
    """
    Dynamically send any data (movie, serial, episode) as a Telegram message.
    Uses episode's parent serial image if episode has no image.
    """
    if not data:
        logger.warning("No data to send")
        return

    lines = []

    # Title
    title = data.get("title") or data.get("name") or "بدون عنوان"
    lines.append(f"<b>📌 {title}</b>")

    # Dynamic fields
    for key, value in data.items():
        if key in ["title", "name", "image_url", "cover_url", "sent", "type", "type_"]:
            continue
        if value is None:
            continue
        # Format booleans
        if isinstance(value, bool):
            value = "✅" if value else "❌"
        # Format lists of dicts
        elif isinstance(value, list) and all(isinstance(v, dict) for v in value):
            if all("name" in v for v in value):
                value = ", ".join(v["name"] for v in value)
            elif all("title" in v for v in value):
                value = ", ".join(v["title"] for v in value)
        display_key = key.replace("_", " ").capitalize()
        lines.append(f"• {display_key}: {value}")

    message = "\n".join(lines)

    # Determine image
    image_url = data.get("image_url") or data.get("cover_url")

    # If episode, fallback to parent serial image
    if not image_url and data.get("season_id") and "serial" in data:
        parent_serial = data["serial"]  # make sure you include serial data when fetching episode
        image_url = parent_serial.get("image_url") or parent_serial.get("cover_url")

    try:
        if image_url:
            await bot.send_photo(chat_id=chat_id, photo=image_url, caption=message, parse_mode=ParseMode.HTML)
        else:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
        logger.info(f"Message sent: {title}")
    except Exception as e:
        logger.error(f"Failed to send telegram message: {e}")



# ------------------ Fetch Last Items ------------------
async def send_last_items(bot, crud_class, chat_id: int):
    """
    Fetch last 5 items from a CRUD class and send dynamically.
    Handles episode images with fallback to serial images.
    """
    with safe_session(engine) as session:
        result = crud_class.get_last_five(session)

        if not result.success:  # check the CRUDResult success
            logger.error(f"Failed to fetch data for {crud_class.__name__}: {result.error}")
            return f"❌ {result.error}"

        items = result.data  # extract actual list of items
        for item in items:
            data = item.model_dump()

            # Handle episodes: fallback to serial image if episode has none
            if isinstance(item, Episode) and not data.get("image_url") and getattr(item, "serial", None):
                data["image_url"] = item.serial.image_url

            await send_to_telegram(data, bot, chat_id)
    return "OK"


# ------------------ Commands ------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = LayoutContainer().resolve('admin')
    username = update.effective_user.username
    if username in ADMINS:
        await update.message.reply_text(f"Hello {update.effective_user.first_name}", reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            f"You don't have permission, {update.effective_user.first_name}. Please contact admin."
        )


async def send_data_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command to send all latest movies, serials, and episodes.
    """
    for crud_class in [MovieCRUD, SerialCRUD, EpisodeCRUD]:
        result = await send_last_items(context.bot, crud_class, CHANNEL_ID)
        if result != "OK":
            await update.message.reply_text(result)


# ------------------ Scheduled Job ------------------
async def send_data_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Scheduled job to send latest content automatically.
    """
    for crud_class in [MovieCRUD, SerialCRUD, EpisodeCRUD]:
        await send_last_items(context.bot, crud_class, CHANNEL_ID)


async def send_with_limit(context: ContextTypes.DEFAULT_TYPE):
    """
    Send posts with a limit, update `sent` status in DB.
    """
    global skip
    message_sender = TelegramMessageSender(TOKEN)
    limit = context.job.data.get("limit", 5)

    with safe_session(engine) as session:
        result = PostCRUD.get_all(session, limit=limit, skip=skip)
        posts = result.data

        for post in posts:
            if not post.sent:
                await message_sender.send_message_with_image(
                    chat_id=CHANNEL_ID,
                    title=post.title,
                    content=post.summary,
                    image_url=post.image,
                    link=unquote(post.link) if post.link else None
                )
                post.sent = True
                session.add(post)
        session.commit()
    skip += limit


# ------------------ Run Bot ------------------
def run():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("send_data", send_data_command))

    # Daily scheduled job at 5:00 PM Iran time
    app.job_queue.run_daily(
        callback=send_with_limit,
        time=time(hour=17, minute=0, tzinfo=IRAN_TZ),
        data={'limit': 5},
        name='daily_5pm_job'
    )

    # Repeating job every 6 hours
    app.job_queue.run_repeating(
        callback=send_data_job,
        interval=21600,  # 6 hours
        first=10
    )

    logger.info("✅ Bot scheduled successfully")
    print("🚀 Bot started")
    app.run_polling()


if __name__ == "__main__":
    run()
