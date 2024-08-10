from pydantic_settings import BaseSettings
import os



class Settings(BaseSettings):
    EBAY_URL_REGEX : str = r"^https://www\.ebay\.com/itm/\d+(\?.*)?$"






    class Config:
        env_file = os.getenv("ENV_FILE", ".env")
        case_sensitive = True
        extra = "allow"



settings = Settings()