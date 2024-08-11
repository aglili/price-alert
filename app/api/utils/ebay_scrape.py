from urllib.request import urlopen

from bs4 import BeautifulSoup

from app.api.core import messages
from app.api.core.exceptions import ValidationError


class ParseEbayListing:

    def _open_url(self, url: str):
        html = urlopen(url=url)
        return html.read()

    def _bs_html(self, html):
        bs = BeautifulSoup(html, "html.parser")
        return bs

    def _get_product_details(self, bs):
        product_name_tag = bs.find("h1", {"class": "x-item-title__mainTitle"})
        product_price_tag = bs.find("div", {"class": "x-price-primary"})

        product_name = (
            product_name_tag.get_text(strip=True) if product_name_tag else None
        )
        product_price_text = (
            product_price_tag.get_text(strip=True) if product_price_tag else None
        )

        if product_price_text is not None:
            country = product_price_text.split()[0]
            currency = product_price_text.split()[1][0]
            price = product_price_text.split()[1][1:]
        else:
            raise ValidationError(messages.FAILED_PARSE_EBAY_LISTING)

        return product_name, country, currency, price

    def _get_image_url(self, bs):
        # Find the first image tag with the src attribute
        image_tag = bs.find("img", {"alt": True, "src": True})
        if image_tag:
            # Return the URL from the src attribute
            image_url = image_tag.get("src")
        else:
            raise ValidationError(messages.FAILED_PARSE_EBAY_LISTING)
        return image_url

    def parse_ebay_listing(self, url: str):
        html_content = self._open_url(url)
        bs_obj = self._bs_html(html_content)
        product_details = self._get_product_details(bs_obj)
        image_url = self._get_image_url(bs_obj)
        return product_details, image_url
