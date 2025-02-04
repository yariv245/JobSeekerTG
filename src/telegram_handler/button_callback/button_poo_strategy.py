from telegram import MaybeInaccessibleMessage
from telegram.constants import ReactionEmoji

from model.job_repository import job_repository
from scrapers import create_logger
from telegram_bot import tg_bot
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class PooStrategy(ButtonStrategy):
    def __init__(self, message: MaybeInaccessibleMessage, job_id: str) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._message = message
        self._job_id = job_id
        self._emoji = ReactionEmoji.PILE_OF_POO
        self._logger = create_logger("PooStrategy")


    async def execute(self):
        job = job_repository.find_by_id(self._job_id)
        if not job:
            self._logger.error(f"Job with ID {self._job_id} not found.")
            return
        job.applied = False
        job_repository.update(job)
        chat_id = self._message.chat.id
        await tg_bot.set_message_reaction(chat_id, self._message.message_id, self._emoji)
