from enum import Enum

from telegram import Update, Chat, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters,
)

from db.User import User
from db.position_repository import position_repository
from db.user_repository import UserRepository
from jobspy.scrapers.utils import create_logger
from telegram_bot import TelegramBot
from telegram_handler.telegram_handler import TelegramHandler


class Flow(Enum):
    POSITION = 0
    ADDRESS = 1
    FILTERS = 2
    EXPERIENCE = 3
    VERIFY_ADDRESS = 4
    VERIFY_FILTERS = 5
    SKIP_FILTERS = 6


class TelegramStartHandler(TelegramHandler):

    def __init__(self):
        self.filters = None
        self.telegram_bot = TelegramBot()
        self.user_repository = UserRepository()
        self.logger = create_logger("TelegramStartHandler")
        self.positions = position_repository.find_all()
        self.temp_user = None
        self.cities = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Starts the conversation and asks the user about their position."""
        chat: Chat = update.message.chat
        user = User(full_name=chat.full_name, username=chat.username, chat_id=chat.id)
        self.user_repository.insert_user(user)

        buttons = [[KeyboardButton(position.name)] for position in self.positions]
        reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True,
                                           input_field_placeholder=Flow.POSITION.name)
        await update.message.reply_text(
            "Hi! My name is Professor Bot. I will hold a conversation with you. "
            "Send /cancel to stop talking to me.\n\n"
            "What Position are you looking for?",
            reply_markup=reply_markup,
        )

        return Flow.POSITION.value

    async def position(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the selected position and asks for a photo."""
        user = update.message.from_user
        self.logger.info("Position of %s: %s", user.first_name, update.message.text)
        position = next((p for p in self.positions if p.name == update.message.text), None)
        if not position:
            await update.message.reply_text("Position not found")
            buttons = [[KeyboardButton(position.name)] for position in self.positions]
            reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True,
                                               input_field_placeholder=Flow.POSITION.name)
            await update.message.reply_text(
                "What Position are you looking for?",
                reply_markup=reply_markup,
            )
            return Flow.POSITION.value

        await update.message.reply_text(
            "Gorgeous! Now, send me cites you want to search for\n"
            "Example: Rishon Lezion,Petah Tikva,..."
        )

        return Flow.ADDRESS.value

    async def address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the photo and asks for a location."""
        user = update.message.from_user
        self.cities = update.message.text.split(",")
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Yes"), KeyboardButton("No")]], one_time_keyboard=True,
                                           input_field_placeholder=Flow.VERIFY_ADDRESS.name)
        await update.message.reply_text(f"Did you choose: {self.cities} ?", reply_markup=reply_markup)

        return Flow.VERIFY_ADDRESS.value

    async def verify_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.text == "No":
            await update.message.reply_text(
                "Please send the cities\n"
                "Example: Rishon Lezion,Petah Tikva,..."
            )
            return Flow.ADDRESS.value

        reply_markup = ReplyKeyboardMarkup([["1", "2"]], one_time_keyboard=True,
                                           input_field_placeholder=Flow.VERIFY_ADDRESS.name)
        await update.message.reply_text(
            "Maybe I can visit you sometime!\n"
            "Tell Your experience",
            reply_markup=reply_markup
        )

        return Flow.EXPERIENCE.value

    async def experience(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the info about the user and ends the conversation."""
        user = update.message.from_user
        self.logger.info("Experience of %s: %s", user.first_name, update.message.text)

        await update.message.reply_text(
            "Gorgeous!\n"
            "Now, send me keywords to filter out positions based on title\n"
            "Example: Data,QA,..."
        )
        return Flow.FILTERS.value

    async def filters_flow(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Stores the location and asks for some info about the user."""
        self.filters = update.message.text.split(",")
        reply_markup = ReplyKeyboardMarkup([[KeyboardButton("Yes"), KeyboardButton("No")]], one_time_keyboard=True,
                                           input_field_placeholder=Flow.VERIFY_FILTERS.name)
        await update.message.reply_text(f"Did you choose: {self.filters} ?", reply_markup=reply_markup)

        return Flow.VERIFY_FILTERS.value

    async def verify_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.message.text == "No":
            await update.message.reply_text(
                "Please send the filters\n"
                "Example: QA ,DATA,..."
            )
            return Flow.FILTERS.value

        await update.message.reply_text("Thank you! I hope we can talk again some day.")

        return ConversationHandler.END

    async def skip_filter(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Skips the location and asks for info about the user."""
        user = update.message.from_user
        self.logger.info("User %s did not send a filters.", user.first_name)
        await update.message.reply_text("Thank you! I hope we can talk again some day.")

        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        self.logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("start handling")
        # chat: Chat = update.message.chat
        # chat.id - 368620919
        # chat.username - 'Qw1zeR'
        # chat.full_name - 'Qw1zeR'
        # user = User(full_name=chat.full_name, username=chat.username, chat_id=chat.id)
        # self.user_repository.insert_user(user)
        # fields = field_repository.find_all()  # Get all fields from the database
        # buttons = [[KeyboardButton(field.name)] for field in fields]
        # reply_markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
        #
        # await update.message.reply_text("Please select your field:", reply_markup=reply_markup)
        # await self.telegram_bot.set_message_reaction(
        #     update.message.message_id, ReactionEmoji.FIRE)
        # site_names = [site.name for site in self.sites_to_scrap]
        # site_names_print = ", ".join(site_names)
        # await self.telegram_bot.send_text(
        #     f"Start scarping: {site_names_print}")
        # self.logger.info(f"Found {len(jobs)} jobs")
        # self.jobRepository.insert_many_if_not_found(filtered_out_jobs)
        # old_jobs, new_jobs = self.jobRepository.insert_many_if_not_found(jobs)
        # for newJob in new_jobs:
        #     await self.telegram_bot.send_job(newJob)
        # self.logger.info(f"Found {len(old_jobs)} old jobs")
        # await self.telegram_bot.send_text(
        #     f"Finished scarping: {site_names_print}")
        self.logger.info("finished handling")


start_handler = TelegramStartHandler()
start_conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_handler.start)],
    states={
        Flow.POSITION.value: [MessageHandler(filters.TEXT, start_handler.position)],
        Flow.ADDRESS.value: [MessageHandler(filters.TEXT, start_handler.address)],
        Flow.VERIFY_ADDRESS.value: [MessageHandler(filters.TEXT, start_handler.verify_address)],
        Flow.EXPERIENCE.value: [MessageHandler(filters.TEXT, start_handler.experience)],
        Flow.FILTERS.value: [MessageHandler(filters.TEXT, start_handler.filters_flow)],
        Flow.VERIFY_FILTERS.value: [MessageHandler(filters.TEXT, start_handler.verify_filter)],
    },
    fallbacks=[CommandHandler("cancel", start_handler.cancel)],
)