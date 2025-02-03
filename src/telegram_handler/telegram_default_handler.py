from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ReactionEmoji
from telegram.ext import (
    ContextTypes,
)

from model.job_repository import JobRepository
from model.user_repository import user_repository
from scrapers import Site, scrape_jobs, JobPost
from scrapers.utils import create_logger
from telegram_bot import tg_bot
from telegram_handler.telegram_handler import TelegramHandler


def map_jobs_to_keyboard(jobs: list[JobPost]) -> InlineKeyboardMarkup:
    """
    Maps a list of JobPost objects to a list of lists of InlineKeyboardButton objects.

    Args:
        jobs: A list of JobPost objects.

    Returns:
        A list of lists of InlineKeyboardButton objects, where each inner list contains
        a single button representing a job.
    """
    keyboard = []
    for job in jobs:
        # Create a new inner list for each job
        inner_list = [InlineKeyboardButton(f"{job.title},{job.company_name}", callback_data=job.id)]
        # Append the inner list to the main keyboard list
        keyboard.append(inner_list)

    return InlineKeyboardMarkup(keyboard)


class TelegramDefaultHandler(TelegramHandler):
    def __init__(self, sites: list[Site]):
        self.sites_to_scrap = sites
        self.jobRepository = JobRepository()
        if len(sites) == 1:
            self.logger = create_logger(
                f"Telegram{sites[0].name.title()}Handler")
        else:
            self.logger = create_logger("TelegramAllHandler")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("start handling")
        chat_id = update.message.chat.id
        await tg_bot.set_message_reaction(chat_id,
                                                     update.message.message_id, ReactionEmoji.FIRE)
        user = user_repository.find_by_username(update.message.from_user.username)

        site_names = [site.name for site in self.sites_to_scrap]
        site_names_print = ", ".join(site_names)
        locations = [location + f", {user.country}" for location in user.cities]
        await tg_bot.send_text(chat_id,f"Start scarping: {site_names_print}")
        scraper_response = scrape_jobs(
            site_name=self.sites_to_scrap,
            user=user,
            search_term=user.position.value,
            locations=locations,
            results_wanted=200,
            hours_old=int(user.job_age),
            filter_by_title=user.title_filters,
            country_indeed='israel'
        )
        self.logger.info(f"Found {len(scraper_response.remaining_jobs)} jobs")
        self.jobRepository.insert_many_if_not_found(scraper_response.filtered_jobs)
        new_jobs = self.jobRepository.insert_many_if_not_found(scraper_response.remaining_jobs)
        if scraper_response.site_to_error_dict:
            for pair in scraper_response.site_to_error_dict:
                error_message = scraper_response.site_to_error_dict[pair]
                await tg_bot.send_text(chat_id, f"Error {pair} scarping: {error_message}")
        for newJob in new_jobs:
            await tg_bot.send_job(chat_id, newJob)
        if scraper_response.filtered_jobs:
            await tg_bot.send_text(chat_id, "filtered by title: ",
                                              reply_markup=map_jobs_to_keyboard(scraper_response.filtered_jobs))
        await tg_bot.send_text(chat_id,f"Finished scarping: {site_names_print}")
        self.logger.info("finished handling")
