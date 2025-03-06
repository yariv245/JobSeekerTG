from telegram import CallbackQuery
from telegram.constants import ReactionEmoji

from model.application_repository import application_repository
from scrapers import create_logger
from telegram_bot import tg_bot
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class PooStrategy(ButtonStrategy):
    def __init__(self, query: CallbackQuery, job_id: str) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._message = query.message
        self._from_user = query.from_user
        self._job_id = job_id
        self._emoji = ReactionEmoji.PILE_OF_POO
        self._logger = create_logger("PooStrategy")

    async def execute(self):
        application = application_repository.find_by_user_and_message_id(self._from_user.username,
                                                                         self._message.message_id)
        if not application:
            self._logger.error(
                f"Application of {self._from_user.username} with message id: {self._message.message_id} not found.")
            return
        else:
            application.active = False
            application_repository.update(application)

        await tg_bot.set_message_reaction(self._message.chat.id, self._message.message_id, self._emoji)
