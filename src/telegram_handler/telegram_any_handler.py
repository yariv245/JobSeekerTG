from telegram import Update
from telegram.constants import ReactionEmoji
from telegram.ext import (
    ContextTypes,
)

from scrapers.utils import create_logger
from telegram_bot import tg_bot
from telegram_handler.start_handler_constats import DEFAULT_MESSAGE
from telegram_handler.telegram_handler import TelegramHandler


class AnyTelegramHandler(TelegramHandler):
    def __init__(self):
        self._logger = create_logger("AnyTelegramHandler")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self._logger.info("start handling")
        chat_id = update.message.chat.id
        await tg_bot.set_message_reaction(chat_id,
                                          update.message.message_id, ReactionEmoji.FIRE)
        await tg_bot.send_text(chat_id, DEFAULT_MESSAGE)

        self._logger.info("finished handling")


any_handler = AnyTelegramHandler()
