import structlog
from fastapi import Depends
from sqlalchemy.orm import Session

from app.api.core.dependencies import get_ebay_parser
from app.api.core.exceptions import ValidationError
from app.api.database.config import get_db
from app.api.database.ebay_listing import EbayListing
from app.api.utils.ebay_scrape import ParseEbayListing
from app.api.utils.enums import ListingStatus
from app.api.utils.utils import send_email

logger = structlog.get_logger()


def check_all_listings_and_mail(
    db: Session = Depends(get_db), parser: ParseEbayListing = Depends(get_ebay_parser)
):
    all_available = (
        db.query(EbayListing)
        .filter(EbayListing.status == ListingStatus.AVAILABLE)
        .all()
    )

    for listing in all_available:
        try:

            listing_details, image_url = parser.parse_ebay_listing(listing.listing_url)
            logger.info("Crawwling For Change In Details", listing_id=listing.id)
            title, country, currency, price = listing_details

            if listing.has_changed_price(float(price)):
                send_email(
                    old_price=f"{listing.currency} {listing.entry_price}",
                    new_price=f"{listing.currency} {price}",
                    listing_name=listing.listing_name,
                    listing_url=listing.listing_url,
                )
                logger.info(
                    "Sent email for listing",
                    listing_id=listing.id,
                    old_price=listing.entry_price,
                    new_price=float(price),
                )

                listing.entry_price = float(price)
                db.commit()
                db.refresh(listing)
                logger.info(
                    "Updated listing price in database",
                    listing_id=listing.id,
                    new_price=float(price),
                )

        except ValidationError as e:
            logger.error(
                "Validation error while processing listing",
                listing_id=listing.id,
                error=str(e),
            )
            listing.status = ListingStatus.SOLD
            db.commit()
            db.refresh(listing)
            logger.info(
                "Updated listing status to SOLD due to validation error",
                listing_id=listing.id,
            )
        except Exception as e:
            logger.error(
                "Unexpected error while processing listing",
                listing_id=listing.id,
                error=str(e),
            )
