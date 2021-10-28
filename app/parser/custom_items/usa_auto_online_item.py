import pyppeteer
from requests_html import AsyncHTMLSession

from .default_item import Item


class UsaAutoOnlineItem(Item):
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
        response = await session.get(item_url, headers=Item._HEADERS, verify=False)
        if response.status_code != 200:
            # render html by js
            await response.html.arender(sleep=1.5)
        await session.close()
        return response
