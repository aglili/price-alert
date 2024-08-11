import structlog
from trycourier import Courier

from app.api.config.settings import settings

logger = structlog.get_logger()


client = Courier(auth_token=settings.COURIER_API_KEY)


def send_email(old_price: str, new_price: str, listing_name: str, listing_url: str):
    client.send_message(
        message={
            "to": {
                "email": settings.USER_EMAIL,
            },
            "template": "R3N78WV5ETM0PGNF6S30Q72PQY4Q",
            "data": {
                "listing_name": listing_name,
                "old_price": old_price,
                "new_price": new_price,
                "listing_url": listing_url,
            },
        }
    )
    logger.info("Email Sent")
