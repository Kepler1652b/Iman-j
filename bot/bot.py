"""
Telegram Bot for sending formatted messages with images
Supports direct messages and channel posts.
Prettified messages in Persian for users.
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
    Send any item (movie, serial, episode) as a Telegram message.
    Prettified with Persian labels.
    Uses parent serial image for episodes if no image.
    """
    if not data:
        logger.warning("No data to send")
        return

    # Fields to show in Persian
    FIELD_MAP = {
        "description": "توضیحات",
        "duration": "مدت زمان",
        "year": "سال",
        "imdb": "امتیاز IMDB",
        "is_persian": "فارسی",
        "season_count": "تعداد فصل‌ها",
    }

    lines = []

    # Title
    title = data.get("title") or data.get("name") or "بدون عنوان"
    lines.append(f"<b>📌 {title}</b>")

    # If episode, include serial name
    if data.get("season_id") and "serial" in data:
        serial_name = data["serial"].get("title") or data["serial"].get("name")
        if serial_name:
            lines.append(f"• سریال: {serial_name}")

    # Add fields
    for key, persian_label in FIELD_MAP.items():
        if key in data and data[key] is not None:
            value = data[key]
            if isinstance(value, bool):
                value = "✅" if value else "❌"
            lines.append(f"• {persian_label}: {value}")

    message = "\n".join(lines)

    # Determine image
    image_url = data.get("image_url") or data.get("cover_url")
    # Episode fallback to serial image
    if not image_url and data.get("season_id") and "serial" in data:
        parent_serial = data["serial"]
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
    Fetch last 5 items from a CRUD class and send them.
    Episodes include serial info if image is missing.
    """
    with safe_session(engine) as session:
        result = crud_class.get_last_five(session)

        if not result.success:
            logger.error(f"Failed to fetch data for {crud_class.__name__}: {result.error}")
            return f"❌ {result.error}"

        items = result.data
        for item in items:
            data = item.model_dump()
            if isinstance(item, Episode) and getattr(item, "serial", None):
                data["serial"] = item.serial.model_dump()
            await send_to_telegram(data, bot, chat_id)
    return "OK"


# ------------------ Commands ------------------
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = LayoutContainer().resolve('admin')
    username = update.effective_user.username
    if username in ADMINS:
        await update.message.reply_text(f"سلام {update.effective_user.first_name}", reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            f"شما دسترسی ندارید، {update.effective_user.first_name}. لطفاً با ادمین تماس بگیرید."
        )


async def send_data_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Command to send all latest movies, serials, and episodes.
    """
    for crud_class in [MovieCRUD, SerialCRUD, EpisodeCRUD]:
        result = await send_last_items(context.bot, crud_class, CHANNEL_ID)
        if result != "OK":
            await update.message.reply_text(result)


# ------------------ Scheduled Jobs ------------------
async def send_data_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Scheduled job to send latest movies, serials, and episodes.
    """
    for crud_class in [MovieCRUD, SerialCRUD, EpisodeCRUD]:
        await send_last_items(context.bot, crud_class, CHANNEL_ID)


async def send_with_limit(context: ContextTypes.DEFAULT_TYPE):
    """
    Send posts with limit, mark them as sent.
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

    # Daily job at 5 PM Iran time
    app.job_queue.run_daily(
        callback=send_with_limit,
        time=time(hour=17, minute=0, tzinfo=IRAN_TZ),
        data={'limit': 5},
        name='daily_5pm_job'
    )

    # Repeat every 6 hours
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
