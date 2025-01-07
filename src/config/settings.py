from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    env: str = Field(alias="env")
    telegram_api_token_prod: str = Field(alias="telegram_api_token_prod")
    telegram_api_token_dev: str = Field(alias="telegram_api_token_dev")
    mongo_uri: str = Field(alias="mongo_uri")
    mongo_db_name: str = Field(alias="mongo_db_name")


settings = Settings()
