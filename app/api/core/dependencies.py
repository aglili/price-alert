from app.api.utils.ebay_scrape import ParseEbayListing


parser = ParseEbayListing()


def get_ebay_parser():
    return parser