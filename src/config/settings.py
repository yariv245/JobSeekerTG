from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_api_token: str = Field(alias="telegram_api_token")
    mongo_uri: str = Field(alias="mongo_uri")
    mongo_db_name: str = Field(alias="mongo_db_name")


settings = Settings()
