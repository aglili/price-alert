from fastapi import FastAPI, Depends
from fastapi.responses import ORJSONResponse
from sqlalchemy.orm import Session
from app.api.schema.ebay_schema import EbayListingURL
from app.api.core.dependencies import get_ebay_parser
from app.api.utils.ebay_scrape import ParseEbayListing
from app.api.database.config import get_db
from app.api.database.ebay_listing import EbayListing
from app.api.utils.responses import send_data_with_info, client_side_error, internal_server_error
from app.api.core import messages
from app.api.utils.ebay_transformer import ebay_listing_transformer
from app.api.core.exceptions import ValidationError
from app.api.database.config import Base,engine
from app.scheduler.daily import scheduler
import structlog

Base.metadata.create_all(bind=engine)
logger = structlog.get_logger()

app = FastAPI(
    title="Ebay Price Alert Bot",
    docs_url="/docs",
    version="1.0.0",
)


@app.on_event("startup")
async def start_scheduler():
    logger.info("Started Scheduler")

    scheduler.start()


@app.on_event("shutdown")
async def shutdown_scheduler():
    scheduler.shutdown()



@app.post("/", response_class=ORJSONResponse)
def create_listing_watch(
    listing: EbayListingURL,
    parser: ParseEbayListing = Depends(get_ebay_parser),
    current_db: Session = Depends(get_db)
):
    try:
        existing_entry = current_db.query(EbayListing).filter(EbayListing.listing_url == listing.url).first()
        if existing_entry:
            return client_side_error(messages.LISTING_ALREADY_EXISTS)

        listing_details, image_url = parser.parse_ebay_listing(listing.url)
        title, country, currency, price = listing_details

        print(listing.url)

        new_listing = EbayListing(
            listing_name=title,
            image_url=image_url,
            entry_price=float(price), 
            country=country,
            currency=currency,
            listing_url=listing.url
        )

        current_db.add(new_listing)
        current_db.commit()
        current_db.refresh(new_listing)

        data = ebay_listing_transformer(new_listing)

        return send_data_with_info(
            info=messages.NEW_LISTING_CREATED,
            data=data
        )

    except ValidationError as e:
        return client_side_error(e.detail)
    except Exception as e:
        return internal_server_error(user_msg=messages.FAILED_TO_CREATE_LISTING, error=str(e))
    


@app.get("/",response_class=ORJSONResponse)
def get_all_listings(current_db:Session = Depends(get_db)):
    listings = current_db.query(EbayListing).all()
    return send_data_with_info(
        info=messages.GET_LISTINGS_SUCCESS,
        data=[ebay_listing_transformer(listing) for listing in listings]
    )
    


