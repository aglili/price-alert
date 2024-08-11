import math

import structlog
from fastapi import Depends, FastAPI, Form, Query, Request, status
from fastapi.responses import ORJSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.api.core import messages
from app.api.core.dependencies import get_ebay_parser
from app.api.core.exceptions import ValidationError
from app.api.database.config import Base, engine, get_db
from app.api.database.ebay_listing import EbayListing
from app.api.utils.ebay_scrape import ParseEbayListing
from app.api.utils.ebay_transformer import ebay_listing_transformer
from app.api.utils.responses import client_side_error, internal_server_error
from app.scheduler.daily import scheduler

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


templates = Jinja2Templates(directory="app/api/templates")


@app.post("/", response_class=ORJSONResponse)
def create_listing_watch(
    url: str = Form(...),
    parser: ParseEbayListing = Depends(get_ebay_parser),
    current_db: Session = Depends(get_db),
):
    try:
        existing_entry = (
            current_db.query(EbayListing).filter(EbayListing.listing_url == url).first()
        )
        if existing_entry:
            return client_side_error(
                messages.LISTING_ALREADY_EXISTS, status.HTTP_409_CONFLICT
            )

        listing_details, image_url = parser.parse_ebay_listing(url)
        title, country, currency, price = listing_details

        new_listing = EbayListing(
            listing_name=title,
            image_url=image_url,
            entry_price=float(price),
            country=country,
            currency=currency,
            listing_url=url,
        )

        current_db.add(new_listing)
        current_db.commit()
        current_db.refresh(new_listing)

        return RedirectResponse("/", status_code=303)

    except ValidationError as e:
        return client_side_error(e.detail)
    except Exception as e:
        return internal_server_error(
            user_msg=messages.FAILED_TO_CREATE_LISTING, error=str(e)
        )


@app.get("/")
def get_all_listings(
    request: Request,
    current_db: Session = Depends(get_db),
    page_number: int = Query(1, ge=1),
    page_size: int = Query(5, ge=1),
):
    total_listings = current_db.query(EbayListing).count()
    total_pages = math.ceil(total_listings / page_size)

    page_number = max(1, min(page_number, total_pages))

    listings = (
        current_db.query(EbayListing)
        .order_by(desc(EbayListing.created_at))
        .offset((page_number - 1) * page_size)
        .limit(page_size)
        .all()
    )

    transformed_listings = [ebay_listing_transformer(listing) for listing in listings]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "listings": transformed_listings,
            "page_number": page_number,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    )
