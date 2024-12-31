from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from db.job_repository import JobRepository
from jobspy import Site, scrape_jobs
from jobspy.scrapers.utils import create_logger
from telegram_bot import TelegramBot
from telegram_handler.telegram_handler import TelegramHandler


class TelegramIndeedHandler(TelegramHandler):
    def __init__(self, locations: list[str], title_filters: list[str], search_term: str):
        self.sites_to_scrap = [Site.INDEED]
        self.locations = locations
        self.search_term = search_term
        self.title_filters = title_filters
        self.telegramBot = TelegramBot()
        self.jobRepository = JobRepository()
        self.logger = create_logger(
            f"Telegram{self.sites_to_scrap[0].name.title()}Handler")

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.logger.info("start handling")
        filtered_out_jobs, jobs = scrape_jobs(
            site_name=self.sites_to_scrap,
            search_term=self.search_term,
            locations=self.locations,
            results_wanted=200,
            hours_old=48,
            country_indeed='israel',
            filter_by_title=self.title_filters
        )
        self.logger.info(f"Found {len(jobs)} jobs")
        new_jobs = self.jobRepository.insert_many_if_not_found(jobs)
        for newJob in new_jobs:
            await self.telegramBot.send_job(newJob)
        self.logger.info("finished handling")
