from telegram import MaybeInaccessibleMessage
from telegram.constants import ReactionEmoji

from telegram_bot import tg_bot
from telegram_handler.button_callback.button_strategy import ButtonStrategy


class PooStrategy(ButtonStrategy):
    def __init__(self, message: MaybeInaccessibleMessage) -> None:
        """
        Usually, the Context accepts a strategy through the constructor, but
        also provides a setter to change it at runtime.
        """
        self._message = message
        self._emoji = ReactionEmoji.PILE_OF_POO

    async def execute(self):
        chat_id = self._message.chat.id
        await tg_bot.set_message_reaction(chat_id, self._message.message_id, self._emoji)
