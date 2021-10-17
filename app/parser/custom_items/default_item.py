import pyppeteer
from bs4 import BeautifulSoup
import re
from requests_html import AsyncHTMLSession
import asyncio


class Item:
    _possible_tags = ('span', 'meta', 'p', 'div')
    _HEADERS = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
            "AppleWebKit/537.36 (KHTML, like Gecko)" +
            "Chrome/83.0.4103.116" +
            "Safari/537.36",
    }

    def __init__(self, item_url: str, current_price: str):
        self.item_url = item_url
        self._current_price = self._get_price_number_from_str(current_price)
        self._html_attrs = None  # Needed to run init_attr() to initialize a html_attrs

    @property
    def current_price(self) -> float:
        """
        Return a current price.

        :return: Current price
        :rtype: float
        """
        return self._current_price

    @property
    def html_attrs(self) -> dict:
        """
        Return a dictionary with a html attributes for tracking a current price.

        :return: Dictionary with a html attributes.
        :rtype: dict
        """
        return self._html_attrs

    async def init_attr(self):
        """
        Initializes a html-element attributes for tracking a item price.
        """
        self._html_attrs = await self._get_html_attrs()

    @classmethod
    async def _get_response_from_item_source(cls, item_url) -> object:
        """
        Gets response from a web-page.

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
        response = await session.get(item_url, headers=Item._HEADERS)
        if response.status_code != 200:
            # render html by js
            await response.html.arender(sleep=1.5)
        await session.close()
        return response

    @staticmethod
    def _make_item_page_soup(response: object) -> object:
        """
        Makes a BeautifulSoup object from response.

        :return: BeautifulSoup object of web-page.
        :rtype: object
        """
        soup = BeautifulSoup(response.html.html, 'html.parser')
        return soup

    async def _get_html_attrs(self) -> dict:
        """
        Return a dictionary with a html attributes for tracking a current price.

        :return: Dictionary with a html attributes. None if it failed to get a attributes.
        :rtype: dict
        """
        html_attrs = None
        html_element = await self._find_html_element_with_current_from_web_page()
        if html_element:
            html_attrs = html_element.attrs
            # Needed to discard the fractional part if the price is without it
            price = (str(int(self.current_price)) if self.current_price.is_integer() else str(self.current_price))
            # Remove a price indication from a html-element attributes
            for key, value in list(html_attrs.items()):
                if value == price:
                    del html_attrs[key]
                elif key == 'content':
                    del html_attrs[key]
                elif key == 'style':
                    del html_attrs[key]
        return html_attrs

    async def _find_html_element_with_current_from_web_page(self) -> object:
        """
        Gets a html-element from a web-page for tracking price.

        :return: Return html-element for tracking price. None if html-element for tracking couldn't be found.
                 (bs4.element.Tag). None if it failed to get a needed html-element.
        :rtype: object
        """
        response = await self._get_response_from_item_source(item_url=self.item_url)
        page_soup = self._make_item_page_soup(response)

        itemprop_result = self._get_itemprop(page_soup)
        if itemprop_result:
            return itemprop_result

        result = None
        for possible_tag in Item._possible_tags:
            for html_element in page_soup.select(f'{possible_tag}[class*="price"]'):
                if self.current_price == self._get_price_number_from_str(html_element.text):
                    if not result:
                        result = html_element
        return result

    def _get_itemprop(self, page_soup: object) -> object:
        """
        Check that a web-page soup has the html-element with itemprop='price' and a price in a 'content' attribute
        or in a text of an element.

        :param page_soup: BeautifulSoup object
        :type page_soup: object
        :return: Return html-element for tracking price. None if html-element for tracking couldn't be found.
                 (bs4.element.Tag)
        :rtype: object
        """
        for tag in Item._possible_tags:
            result = page_soup.find(tag, itemprop="price")
            if result:
                # Check if price in html-element text
                if all([result,
                        self._get_price_number_from_str(result.text) == self.current_price]):
                    return result
                # Check if price in 'content' attribute of html-element
                elif all([result, self._get_price_number_from_str(result.get('content')) == self.current_price]):
                    return result
        return None

    @classmethod
    async def get_current_price_by_html_attrs(cls, item_url, html_attrs):
        response = await cls._get_response_from_item_source(item_url=item_url)
        page_soup = cls._make_item_page_soup(response)

        html_element_with_current_price = page_soup.find(attrs=html_attrs)
        full_attrs_of_html_element_with_current_price = html_element_with_current_price.attrs
        if full_attrs_of_html_element_with_current_price.get('content'):
            return cls._get_price_number_from_str(full_attrs_of_html_element_with_current_price.get('content'))
        return cls._get_price_number_from_str(html_element_with_current_price.text)

    @staticmethod
    def _get_price_number_from_str(string_with_price: str) -> float:
        """
        Gets item price from string and converts to float.

        :param string_with_price: A string with a price contained inside
        :type string_with_price: str
        :return: an item price
        :rtype: float
        """
        price = None
        price_in_string = re.search(r'\d+(\s|\\xa0)?\d+((\.|,)\d{1,2})?', string_with_price)
        # price_in_string = re.search(r'(\d+(\s|\\xa0|,)?)+((\.|,)\d{1,2})?', string_with_price)
        if price_in_string:
            price = float(price_in_string.group().replace(',', '.').replace(u'\xa0', '').replace(' ', ''))
        return price

    def __str__(self):
        return f'\n{self.item_url}\n{self.current_price}\n{self.html_attrs}'


class DefaultItem(Item):
    """
    Item object with a default rules for parsing a current price.
    """
    pass
