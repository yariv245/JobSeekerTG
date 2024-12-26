from telegram import Update
from telegram.ext import (
    ContextTypes,
)

from src.jobspy import Site, scrape_jobs
from src.jobspy.db.job_repository import JobRepository
from src.jobspy.scrapers.utils import create_logger
from src.telegram_bot import TelegramBot
from src.telegram_handler.telegram_handler import TelegramHandler

logger = create_logger("TelegramAllHandler")


class TelegramAllHandler(TelegramHandler):
    def __init__(self, sites: list[Site], locations: list[str], title_filters: list[str],search_term:str):
        self.sites_to_scrap = sites
        self.locations = locations
        self.search_term = search_term
        self.title_filters = title_filters
        self.telegramBot = TelegramBot()
        self.jobRepository = JobRepository()

    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("start handling")
        jobs = scrape_jobs(
            site_name=self.sites_to_scrap,
            search_term=self.search_term,
            locations=self.locations,
            results_wanted=200,
            hours_old=48,
            country_indeed='israel',
            filter_by_title=self.title_filters
        )
        logger.info(f"Found {len(jobs)} jobs")
        new_jobs = self.jobRepository.insertManyIfNotFound(jobs)
        for newJob in new_jobs:
            await self.telegramBot.sendJob(newJob)
        logger.info("finished handling")