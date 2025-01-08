from typing import Optional

from dotenv import load_dotenv
from pymongo import UpdateOne

from jobs import JobPost
from scrapers import create_logger
from .monogo_db import mongo_client

load_dotenv()


class JobRepository:
    def __init__(self):
        self._logger = create_logger("JobRepository")
        self._collection = mongo_client.get_collection('jobs')
        self._collection.create_index('id', unique=True)

    def find_by_id(self, job_id: str) -> Optional[JobPost]:
        """
        Finds a job document in the collection by its ID.

        Args:
            job_id: The ID of the job to find.

        Returns:
            The job document if found, otherwise None.
        """
        result = self._collection.find_one({"id": job_id})
        return JobPost(**result)

    def update(self, job: JobPost) -> bool:
        """
        Updates a JobPost in the database.

        Args:
            job: A dictionary representing the JobPost data.

        Returns:
            True if the update was successful, False otherwise.
        """
        result = self._collection.update_one({"id": job.id}, {"$set": job.model_dump(exclude={"date_posted"})})
        return result.modified_count > 0

    def insert_job(self, job: JobPost):
        """
        Inserts a new job posting into the database collection.

        Args:
            job (JobPost): The JobPost object to be inserted.

        Raises:
            Exception: If an error occurs during insertion.
        """
        job_dict = job.model_dump(exclude={"date_posted"})
        self._collection.insert_one(job_dict)
        self._logger.info(f"Inserted new job with title {job.title}.")

    def insert_many_if_not_found(self, jobs: list[JobPost]) -> list[JobPost]:
        """
        Perform bulk upserts for a list of JobPost objects into a MongoDB collection.
        Only insert new jobs and return the list of newly inserted jobs.
        """
        operations = []
        new_jobs = []  # List to store the new jobs inserted into MongoDB
        for job in jobs:
            job_dict = job.model_dump(exclude={"date_posted"})
            operations.append(
                UpdateOne(
                    {"id": job.id},  # Match by `id`
                    # Only set fields if the job is being inserted (not updated)
                    {"$setOnInsert": job_dict},
                    upsert=True  # Insert if not found, but do not update if already exists
                )
            )

        if operations:
            result = self._collection.bulk_write(operations)
            self._logger.info(f"""Matched: {result.matched_count}, Upserts: {
            result.upserted_count}, Modified: {result.modified_count}""")
            result.upserted_ids.get(0)
            new_ids = list(result.upserted_ids.values())
            query = {"_id": {"$in": new_ids}}
            result = self._collection.find(query)
            for document in result:
                new_jobs.append(JobPost(**document))

        return new_jobs


job_repository = JobRepository()
