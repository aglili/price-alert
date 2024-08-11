import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    EBAY_URL_REGEX: str = r"^https://www\.ebay\.com/itm/\d+(\?.*)?$"
    COURIER_API_KEY: str = os.getenv("COURIER_API_KEY", "trial_key")
    USER_EMAIL: str = os.getenv("USER_EMAIL", "test@mail.com")

    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        case_sensitive = True
        extra = "allow"


settings = Settings()
