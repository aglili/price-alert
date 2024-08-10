from app.api.database.ebay_listing import EbayListing


def ebay_listing_transformer(listing:EbayListing):
    return {
        "id":listing.id,
        "image_url":listing.image_url,
        "listing_url":listing.listing_url,
        "entry_price":listing.entry_price,
        "country":listing.country,
        "currency":listing.currency,
        "status":listing.status
    }