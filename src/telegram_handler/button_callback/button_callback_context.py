from __future__ import annotations

from telegram import CallbackQuery
from telegram.constants import ReactionEmoji

from model.job_repository import job_repository
from scrapers import create_logger
from telegram_handler.button_callback.button_fire_strategy import FireStrategy
from telegram_handler.button_callback.button_job_title_strategy import JobTitleStrategy
from telegram_handler.button_callback.button_poo_strategy import PooStrategy
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class ButtonCallBackContext:
    """
    The Context defines the interface
    """

    def __init__(self, query: CallbackQuery, job_id: str) -> None:
        self._logger = create_logger("Button CallBack Context")
        self._job_id = job_id
        self._query = query
        self._strategy = None

    @property
    def strategy(self) -> ButtonStrategy:
        """
        The Context maintains a reference to one of the Strategy objects. The
        Context does not know the concrete class of a strategy. It should work
        with all strategies via the Strategy interface.
        """

        return self._strategy

    @strategy.setter
    def strategy(self, strategy: ButtonStrategy) -> None:
        """
        Usually, the Context allows replacing a Strategy object at runtime.
        """

        self._strategy = strategy

    async def run(self) -> None:
        self._logger.debug("Starting")
        if ReactionEmoji.FIRE.name == self._query.data:
            self._strategy = FireStrategy(self._query, self._job_id)
        elif ReactionEmoji.PILE_OF_POO.name == self._query.data:
            self._strategy = PooStrategy(self._query, self._job_id)
        elif self._query.data:
            job = job_repository.find_by_id(self._query.data)
            if job:
                chat_id = self._query.message.chat.id
                self._strategy = JobTitleStrategy(chat_id, job)
        else:
            self._logger.error("Invalid enum value")
            return

        await self._strategy.execute()
        self._logger.debug("Finished")
