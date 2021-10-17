import pyppeteer
from requests_html import AsyncHTMLSession

from .default_item import Item


class RozetkaItem(Item):
    """
    Item object from rozetka.com.ua store.
    """

    @classmethod
    async def _get_response_from_item_source(cls, item_url):
        """
        Gets response from Rozetka web-page.
        :return: Response object
        :rtype: object
        """
        session = AsyncHTMLSession()
        browser = await pyppeteer.launch({
            'ignoreHTTPSErrors': True,
            'headless': True,
            'handleSIGINT': False,
            'handleSIGTERM': False,
            'handleSIGHUP': False,
            'autoClose': False
        })
        session._browser = browser
        response = await session.get(item_url, headers=super()._HEADERS)
        await response.html.arender()
        await session.close()
        return response

    async def _get_html_attrs(self) -> dict:
        """
        Return a dictionary with a html attributes for tracking a current price.

        :return: Dictionary with a html attributes. None if it failed to get a attributes.
        :rtype: dict
        """
        return {'class': ['product-prices__big']}
