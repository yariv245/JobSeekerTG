"""
scrapers.themuse
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape themuse.
"""

from __future__ import annotations

import json

from bs4 import BeautifulSoup

from jobs import (
    JobPost,
    JobResponse,
)
from ..scraper import Scraper
from ..scraper_input import ScraperInput
from ..site import Site
from ..utils import create_session, create_logger

logger = create_logger("ThemuseScraper")


def extract_search_results(html_content):
    """
    Extracts the JSON data from the <script id="__NEXT_DATA__"> tag.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})

    if script_tag and script_tag.string:
        try:
            data = json.loads(script_tag.string)
            return data['props']['pageProps']['initialSearchResultsState']['results']
        except json.JSONDecodeError:
            print("Error decoding JSON from __NEXT_DATA__ script.")
            return None
    else:
        return None


class TheMuseScraper(Scraper):
    delay = 3
    band_delay = 4
    jobs_per_page = 25

    def __init__(
        self, proxies: list[str] | str | None = None, ca_cert: str | None = None
    ):
        """
        Initializes TheMuseScraper with the TheMusejob search url
        """
        super().__init__(site=Site.THEMUSE, proxies=proxies, ca_cert=ca_cert)
        self.session = create_session(
            proxies=self.proxies,
            ca_cert=ca_cert,
            is_tls=False,
            has_retry=True,
            delay=5,
            clear_cookies=False,
        )
        self.base_url = "https://www.themuse.com/search/location/tel-aviv-israel/keyword/backend/radius/50mi/date-posted/last_7d/"

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes TheMuse for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        self.scraper_input = scraper_input
        job_list: list[JobPost] = []
        try:
            response = self.session.get(
                url=self.base_url,
                timeout=10)

            logger.info(f"response: {str(response)}")
            if (response.status_code != 200):
                response_error_message = f"Status code: {response.status_code}, Error: {str(response.text)}"
                logger.error(response_error_message)
                return JobResponse(jobs=job_list,exec_message=response_error_message)
        except Exception as e:
            exception_message = f"Exception: {str(e)}"
            logger.error(exception_message)
            return JobResponse(jobs=job_list,exec_message=exception_message)

        result = extract_search_results(response.text)

        return JobResponse(jobs=job_list)
