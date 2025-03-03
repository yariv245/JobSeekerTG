import json
from datetime import datetime

from jobs import JobPost, Location


class TheMuseMapper:
    def find_israel_location(self, locations):
        """
        Finds the first location in the list with country code 'IL'.

        Args:
            locations (list): A list of location dictionaries.

        Returns:
            dict or None: The first location dictionary with country 'IL', or None if not found.
        """
        if locations:
            for location in locations:
                if location.get("country") == "IL":
                    return location
        return None

    def map_to_location(self, locations):

        location = self.find_israel_location(locations)

        return Location(
            country=location['country'],
            city=location['locality'],
            latitude=str(location['latitude']),
            longitude=str(location['longitude']),
            text=location['address'])

    def map_themuse_response_to_job_post(self, hit) -> JobPost | None:
        location = self.map_to_location(hit['locations'])
        if not location:
            return None
        url = f"https://www.themuse.com/jobs/{hit['company']['short_name']}/{hit['short_title']}"
        timestamp = datetime.fromtimestamp(hit['posted_at'])
        job_post = JobPost(
            id=hit['id'],
            title=hit['title'],
            company_name=hit['company']['name'],
            job_url=url,
            location=location,
            description=hit['search_text_snippet'],
            date_posted=timestamp.date(),
            datetime_posted=datetime.now(),
            applied=False,
            company_logo=hit['company']['logo']
        )

        return JobPost.model_validate(job_post)

themuse_mapper = TheMuseMapper()