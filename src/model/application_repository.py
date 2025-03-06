from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

from scrapers.utils import create_logger
from .application import Application
from .monogo_db import mongo_client

load_dotenv()


class ApplicationRepository:
    def __init__(self):
        self._logger = create_logger("ApplicationRepository")
        self._collection = mongo_client.get_collection('application')

    def find_by_id(self, application_id: str) -> Optional[Application]:
        """
        Finds a application document in the collection by its ID.

        Args:
            application_id: The ID of the application to find.

        Returns:
            The application document if found, otherwise None.
        """
        return self._collection.find_one({"id": application_id})

    def find_by_user_and_message_id(self, user_id: str, message_id: int) -> Optional[Application]:
        """
        Finds a application document in the collection by its user id and job id.

        Args:
            user_id: The user id.
            message_id: The message id.

        Returns:
            The application document if found, otherwise None.
        """

        document = self._collection.find_one({"user_id": user_id, "message_id": message_id})
        if document:
            return Application(**document)  # Convert the dictionary to an Application object
        return None

    def find_by_user_and_job(self, user_id: str, job_id: str) -> Optional[Application]:
        """
        Finds a application document in the collection by its user id and job id.

        Args:
            user_id: The user id.
            job_id: The job id.

        Returns:
            The application document if found, otherwise None.
        """

        document = self._collection.find_one({"user_id": user_id, "job_id": job_id})
        if document:
            return Application(**document)  # Convert the dictionary to an Application object
        return None

    def update(self, application: Application) -> bool:
        """
        Updates a Application in the database.

        Args:
            application: A dictionary representing the Application data.

        Returns:
            True if the update was successful, False otherwise.
        """
        application.modified_at = datetime.now()
        result = self._collection.update_one({"id": application.id}, {"$set": application.model_dump()})
        return result.modified_count > 0

    def insert_application(self, application: Application):
        """
        Inserts a new application posting into the database collection.

        Args:
            application (Application): The Application object to be inserted.

        Raises:
            Exception: If an error occurs during insertion.
        """
        self._collection.insert_one(application.model_dump())
        self._logger.info(f"{application.user_id} inserted new application to {application.job_id}")


application_repository = ApplicationRepository()
