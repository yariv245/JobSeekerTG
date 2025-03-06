from telegram import CallbackQuery
from telegram.constants import ReactionEmoji

from model.application import Application
from model.application_repository import application_repository
from scrapers import create_logger
from telegram_bot import tg_bot
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class FireStrategy(ButtonStrategy):
    def __init__(self, query: CallbackQuery, job_id: str) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._message = query.message
        self._from_user = query.from_user
        self._emoji = ReactionEmoji.FIRE
        self._job_id = job_id
        self._logger = create_logger("FireStrategy")

    async def execute(self):
        message_id = self._message.message_id
        application = application_repository.find_by_user_and_message_id(self._from_user.username, message_id)

        if not application:
            application = Application(user_id=self._from_user.username, job_id=self._job_id, message_id=message_id)
            application_repository.insert_application(application)
        elif not application.active:
            application.active = True
            application_repository.update(application)

        await tg_bot.set_message_reaction(self._message.chat.id, message_id, self._emoji)
