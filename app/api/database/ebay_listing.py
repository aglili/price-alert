from app.api.database.base_model import BaseModel
from sqlalchemy import Column, String, Float, Enum
from app.api.utils.enums import ListingStatus

class EbayListing(BaseModel):
    __tablename__ = "ebay_listing"
    listing_name = Column(String(length=50), nullable=False)
    image_url = Column(String(length=100), nullable=False)
    listing_url = Column(String(length=100), nullable=False, index=True)
    entry_price = Column(Float, nullable=False)
    country = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    status = Column(Enum(ListingStatus), default=ListingStatus.AVAILABLE)

    def has_changed_price(self, scraped_price: float) -> bool:
        return self.entry_price < scraped_price or self.entry_price > scraped_price
