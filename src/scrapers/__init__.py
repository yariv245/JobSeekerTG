from __future__ import annotations

import re
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed


from jobs import (
    Enum,
    JobType,
    JobResponse,
    Country,
    JobPost,
)
from model.User import User
from .glassdoor import GlassdoorScraper
from .google import GoogleJobsScraper
from .goozali import GoozaliScraper
from .indeed import IndeedScraper
from .linkedin import LinkedInScraper
from .scraper_input import ScraperInput
from .scraper_response import ScraperResponse
from .site import Site
from .utils import set_logger_level, create_logger
from .ziprecruiter import ZipRecruiterScraper


class SalarySource(Enum):
    DIRECT_DATA = "direct_data"
    DESCRIPTION = "description"


def scrape_jobs(
        site_name: str | list[str] | Site | list[Site] | None = None,
        user: User = None,
        search_term: str | None = None,
        google_search_term: str | None = None,
        location: str | None = None,
        locations: list[str] | None = None,
        distance: int | None = 50,
        is_remote: bool = False,
        job_type: str | None = None,
        easy_apply: bool | None = None,
        results_wanted: int = 15,
        country_indeed: str = "usa",
        hyperlinks: bool = False,
        proxies: list[str] | str | None = None,
        ca_cert: str | None = None,
        description_format: str = "markdown",
        linkedin_fetch_description: bool | None = False,
        linkedin_company_ids: list[int] | None = None,
        offset: int | None = 0,
        hours_old: int = None,
        enforce_annual_salary: bool = False,
        verbose: int = 2,
        filter_by_title: list[str] = None,
        **kwargs,
) -> ScraperResponse:
    """
    Simultaneously scrapes job data from multiple job sites.
    :return: list of jobPost, list of new jobPost
    """
    SCRAPER_MAPPING = {
        Site.LINKEDIN: LinkedInScraper,
        Site.INDEED: IndeedScraper,
        Site.ZIP_RECRUITER: ZipRecruiterScraper,
        Site.GLASSDOOR: GlassdoorScraper,
        Site.GOOGLE: GoogleJobsScraper,
        Site.GOOZALI: GoozaliScraper,
    }
    set_logger_level(verbose)

    def map_str_to_site(site_name: str) -> Site:
        return Site[site_name.upper()]

    def get_enum_from_value(value_str):
        for job_type in JobType:
            if value_str in job_type.value:
                return job_type
        raise Exception(f"Invalid job type: {value_str}")

    job_type = get_enum_from_value(job_type) if job_type else None

    def get_site_type():
        site_types = list(Site)
        if isinstance(site_name, str):
            site_types = [map_str_to_site(site_name)]
        elif isinstance(site_name, Site):
            site_types = [site_name]
        elif isinstance(site_name, list):
            site_types = [
                map_str_to_site(site) if isinstance(site, str) else site
                for site in site_name
            ]
        return site_types

    country_enum = Country.from_string(country_indeed)
    scraper_input = ScraperInput(
        user=user,
        site_type=get_site_type(),
        country=country_enum,
        search_term=search_term,
        google_search_term=google_search_term,
        location=location,
        locations=locations,
        distance=distance,
        is_remote=is_remote,
        job_type=job_type,
        easy_apply=easy_apply,
        description_format=description_format,
        linkedin_fetch_description=linkedin_fetch_description,
        results_wanted=results_wanted,
        linkedin_company_ids=linkedin_company_ids,
        offset=offset,
        hours_old=hours_old
    )

    def scrape_site(site: Site) -> tuple[str, JobResponse]:
        scraper_class = SCRAPER_MAPPING[site]
        scraper = scraper_class(proxies=proxies, ca_cert=ca_cert)
        scraped_data: JobResponse = scraper.scrape(scraper_input)
        cap_name = site.value.capitalize()
        site_name = "ZipRecruiter" if cap_name == "Zip_recruiter" else cap_name
        create_logger(site_name).info(f"finished scraping")
        return site.value, scraped_data

    site_to_jobs_dict = {}
    site_to_error_dict = {}
    merged_jobs: list[JobPost] = []
    lock = Lock()

    def worker(site):
        logger = create_logger(f"Worker {site}")
        logger.info("Starting")
        try:
            site_val, job_response = scrape_site(site)
            with lock:
                merged_jobs.extend(job_response.jobs)
            logger.info("Finished")
            return site_val, job_response
        except Exception as e:
            logger.error(f"Error: {e}")
            return site.value, JobResponse(exec_message=str(e))

    with ThreadPoolExecutor(max_workers=5) as executor:
        logger = create_logger("ThreadPoolExecutor")
        future_to_site = {
            executor.submit(worker, site): site for site in scraper_input.site_type
        }
        # An iterator over the given futures that yields each as it completes.
        for future in as_completed(future_to_site):
            try:
                site_value, scraped_data = future.result()
                if site_value and scraped_data:
                    if scraped_data.exec_message:
                        site_to_error_dict[site_value] = scraped_data.exec_message
                    else:
                        site_to_jobs_dict[site_value] = scraped_data
            except Exception as e:
                logger.error(f"Future Error occurred: {e}")

    def filter_jobs_by_title_name(jobs: list[JobPost], filter_by_title: list[str]) -> tuple[list, list]:
        """
        Filters jobs based on title names and returns two lists: filtered and remaining jobs.

        Args:
            jobs: A list of JobPost objects.
            filter_by_title: A list of strings representing titles to filter out.

        Returns:
            A tuple containing two lists:
                - The first list contains JobPost objects that were filtered out.
                - The second list contains JobPost objects that remain after filtering.
        """
        filtered_jobs = []
        remaining_jobs = []

        if not filter_by_title:
            return filtered_jobs, remaining_jobs

        for job in jobs:
            for filter_title in filter_by_title:
                if re.search(filter_title, job.title, re.IGNORECASE):
                    logger.info(f"job filtered out by title: {job.id} , {job.title} , found {filter_title}")
                    filtered_jobs.append(job)
                    break  # Exit inner loop once a match is found for the job
            else:
                remaining_jobs.append(job)
        return filtered_jobs, remaining_jobs

    filtered_jobs, remaining_jobs = filter_jobs_by_title_name(merged_jobs, filter_by_title)

    return ScraperResponse(remaining_jobs,filtered_jobs,site_to_error_dict)
