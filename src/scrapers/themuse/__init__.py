"""
scrapers.themuse
~~~~~~~~~~~~~~~~~~~

This module contains routines to scrape themuse.
"""

from __future__ import annotations

import json
import re

from bs4 import BeautifulSoup

from jobs import (
    JobPost,
    JobResponse,
)
from .TheMuseMapper import themuse_mapper
from ..scraper import Scraper
from ..scraper_input import ScraperInput
from ..site import Site
from ..utils import create_session, create_logger

logger = create_logger("TheMuseScraper")


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

    def scrape(self, scraper_input: ScraperInput) -> JobResponse:
        """
        Scrapes TheMuse for jobs with scraper_input criteria
        :param scraper_input:
        :return: job_response
        """
        job_set: set[JobPost] = set()
        responses = []
        user = scraper_input.user
        keyword = re.sub(r'\s+', '-', user.position)
        date_posted = 'last_7d'
        try:
            for city in user.cities:
                city_lower = city.lower()
                country_lower = user.country.lower()
                city_hyphenated = city_lower.replace(" ", "-")
                location = f"{city_hyphenated}-{country_lower}"
                url = f"https://www.themuse.com/search/location/{location}/keyword/{keyword}/radius/50mi/date-posted/{date_posted}/"
                response = self.session.get(
                    url=url,
                    timeout=10)

                logger.info(f"response: {str(response)}")
                if response.status_code != 200:
                    response_error_message = f"Status code: {response.status_code}, Error: {str(response.text)}"
                    logger.error(response_error_message)
                    return JobResponse(jobs=list(job_set), exec_message=response_error_message)
                responses.append(response)
        except Exception as e:
            exception_message = f"Exception: {str(e)}"
            logger.error(exception_message)
            return JobResponse(jobs=list(job_set), exec_message=exception_message)

        for res in responses:
            result = extract_search_results(res.text)
            for hit in result:
                try:
                    job_post = themuse_mapper.map_themuse_response_to_job_post(hit['hit'])
                    if job_post:
                        job_set.add(job_post)
                except Exception as e:
                    exception_message = f"Exception: {str(e)}"
                    logger.error(exception_message)

        return JobResponse(jobs=list(job_set))
