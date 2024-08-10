from pydantic import BaseModel,field_validator
from app.api.config.settings import settings
import re
from app.api.core.exceptions import ValidationError
from app.api.core import messages


class EbayListingURL(BaseModel):
    url : str

    @field_validator("url")
    @classmethod
    def validate_input_url(cls, value):
        if not re.match(settings.EBAY_URL_REGEX,value):
            raise ValidationError(messages.INVALID_EBAY_URL)
        return value
