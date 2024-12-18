from datetime import datetime, timedelta

from jobspy.scrapers.goozali.model import GoozaliRow
from jobspy.scrapers.goozali.model.GoozaliColumn import GoozaliColumn
from jobspy.scrapers.goozali.model.GoozaliColumnChoice import GoozaliColumnChoice
from jobspy.scrapers.utils import create_logger

# Mapping function to convert parsed dictionary into GoozaliResponseData

logger = create_logger("GoozaliScrapperComponent")


class GoozaliScrapperComponent:
    def __init__(self):
        pass

    # Function to filter GoozaliRows based on hours old
    def filter_rows_by_column_choice(self, rows: list[GoozaliRow], column: GoozaliColumn, column_choice: GoozaliColumnChoice) -> list[GoozaliRow]:
        return [
            row for row in rows
            if row.cellValuesByColumnId[column.id] == column_choice.id
        ]

    def filter_rows_by_hours(self, rows: list[GoozaliRow], hours: int) -> list[GoozaliRow]:
        # Current time
        now = datetime.now()

        # Calculate the time delta for the given hours
        time_delta = timedelta(hours=hours)

        # Filter rows
        filtered_rows = [
            row for row in rows
            if now - row.createdTime <= time_delta
        ]

        return filtered_rows

    def find_column(self, columns: list[GoozaliColumn], column_name: str) -> GoozaliColumn:
        for column in columns:
            if (column.name == column_name):
                return column

    def find_choice_from_column(self, column: GoozaliColumn, choice_name: str) -> GoozaliColumnChoice:
        if not column.typeOptions.choices:
            logger.exception(f"Choices for column {column.name} doesn't exist")
            raise Exception(f"Choices for column {column.name} doesn't exist")

        for key, choice in column.typeOptions.choices.items():
            if (choice.name == choice_name):
                return choice

        logger.exception(f"Can't find {choice_name} for column {column.name}")
        raise Exception(f"Can't find {choice_name} for column {column.name}")