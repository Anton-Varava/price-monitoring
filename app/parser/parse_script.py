from bs4 import BeautifulSoup
import re
from requests_html import HTMLSession, AsyncHTMLSession
from abc import ABC, abstractmethod
import random
import asyncio
from urllib.parse import urlparse
from datetime import datetime, timedelta
import time

# session = AsyncHTMLSession()

HEADER = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
        "AppleWebKit/537.36 (KHTML, like Gecko)" +
        "Chrome/83.0.4103.116" +
        "Safari/537.36",
}

PAGES = [
    # ('https://www.copart.com/ru/lot/43708811/salvage-2019-kia-optima-lx-ga-atlanta-west', '3 250'),
    # ('https://usa-auto-online.com/en/auction/35094441-RAM-PROMASTER', '1 700'),
    ('https://eobuv.com.ua/p/chelsi-blundstone-1911-tabacco', '4 597,00'),
    ('https://elmir.ua/ua/video_cards/graphics_card_gigabyte_pci-e_geforce_rtx2060_6gb_ddr6_gv-n2060oc-6gd.html',
     '22 999'),
    ('https://comfy.ua/ua/stiral-naja-mashina-aeg-l9wba61bc.html', '48 199'),
    ('https://bt.rozetka.com.ua/ua/polaris_pwh_imr_0850_v/p237266605/', '7399'),
    ('https://allo.ua/ru/products/mobile/samsung-galaxy-z-fold3-12-256-green-sm-f926bzgdsek.html', '54 999'),
    (
    'https://www.ebay.com/itm/371246540991?_trkparms=pageci%3Ab603444d-2425-11ec-924c-5edf3e9060ad%7Cparentrq%3A4550c11217c0a45b4a61af5dfffc33dc%7Ciid%3A1',
    '24.99'),
    # ('https://www.citrus.ua/uhod-za-volosami/fen-dyson-supersonic-hd03-fuksiya-689591.html', '14 499'),
    # ('https://eldorado.ua/noutbuk-lenovo-legion5-15-imh05-h-phantom-black-81-y600-m0-ra-/p71310322/', '35 999'),
    ('https://www.foxtrot.com.ua/ru/shop/pylesosy_samsung_vc07m2110sr-uk.html', '2 799'),
    ('https://www.moyo.ua/sistemnyy_blok_2e_moyo_complex_gaming_2e-2152_/477942.html', '21 314'),
    ('https://avic.ua/pocketbook-616-basic-lux2-obsidian-black-pb616-h-cis-item', '3239'),

]

POSSIBLE_TAGS = ('span', 'meta', 'p', 'div')


class Item:
    _possible_tags = ('span', 'meta', 'p', 'div')

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

    async def refresh_current_price(self) -> float:
        """
        Update current price of an item.

        :return: Current price.
        :rtype: float
        """
        self._current_price = await self._get_price_from_html_element()
        return self._current_price

    async def init_attr(self):
        """
        Initializes a html-element attributes for tracking a item price.
        """
        self._html_attrs = await self._get_html_attrs()

    async def _get_response_from_item_source(self) -> object:
        """
        Gets response from a web-page.

        :return: Response object
        :rtype: object
        """
        session = AsyncHTMLSession()
        response = await session.get(self.item_url, headers=HEADER, cookies=session.cookies.get_dict())
        if response.status_code != 200:
            # render html by js
            await response.html.arender(sleep=1.5)
        await session.close()
        return response

    async def _make_item_page_soup(self):
        """
        Makes a BeautifulSoup object from response.

        :return: BeautifulSoup object of web-page.
        :rtype: object
        """
        response = await self._get_response_from_item_source()
        soup = BeautifulSoup(response.html.html, 'html.parser')
        return soup

    async def _get_html_attrs(self) -> dict:
        """
        Return a dictionary with a html attributes for tracking a current price.

        :return: Dictionary with a html attributes. None if it failed to get a attributes.
        :rtype: dict
        """
        html_attrs = None
        html_element = await self._get_html_element_from_page_soup()
        if html_element:
            html_attrs = html_element.attrs
            # Needed to discard the fractional part if the price is without it
            price = (str(int(self.current_price)) if self.current_price.is_integer() else str(self.current_price))
            # Remove a price indication from a html-element attributes
            for key, value in list(html_attrs.items()):
                if value == price:
                    del html_attrs[key]
                elif key == 'style':
                    del html_attrs[key]
        return html_attrs

    async def _get_html_element_from_page_soup(self) -> object:
        """
        Gets a html-element from a web-page for tracking price.

        :return: Return html-element for tracking price. None if html-element for tracking couldn't be found.
                 (bs4.element.Tag). None if it failed to get a needed html-element.
        :rtype: object
        """
        page_soup = await self._make_item_page_soup()
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
                elif all([result, self._get_price_number_from_str(result.get('content')) ==
                                  self.current_price]):
                    return result
        return None

    async def _get_price_from_html_element(self) -> float:
        """
        Get price of an item from a specified html-element.

        :param soup: BeautifulSoup object of a web-page.
        :type soup: object
        :param element: Html-element with price indication (bs4.element.Tag).
        :type element: object
        :return: Price of an item.
        :rtype: float
        """

        page_soup = await self._make_item_page_soup()
        current_html_element = page_soup.find(attrs=self.html_attrs)
        attrs_current_html_element = current_html_element.attrs
        if attrs_current_html_element.get('content'):
            return self._get_price_number_from_str(attrs_current_html_element.get('content'))
        return self._get_price_number_from_str(current_html_element.text)

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
        if price_in_string:
            price = float(price_in_string.group().replace(',', '.').replace(u'\xa0', '').replace(' ', ''))
        return price


class DefaultItem(Item):
    """
    Item object with a default rules for parsing a current price.
    """
    pass


class RozetkaItem(Item):
    """
    Item object from rozetka.com.ua store.
    """

    async def _get_response_from_item_source(self):
        """
        Gets response from Rozetka web-page.
        :return: Response object
        :rtype: object
        """
        session = AsyncHTMLSession()
        response = await session.get(self.item_url, headers=HEADER, cookies=session.cookies.get_dict(), )
        await response.html.arender()
        await session.close()
        return response

    async def init_attr(self):
        """
        Initializes a html-element attributes for tracking a item price.
        """
        self._html_attrs = await self._get_html_attrs()

    async def _get_html_attrs(self) -> dict:
        """
        Return a dictionary with a html attributes for tracking a current price.

        :return: Dictionary with a html attributes. None if it failed to get a attributes.
        :rtype: dict
        """
        return {'class': ['product-prices__big']}


class ItemFactory:
    """
    Factory for creating an Item objects.
    """
    _sources = {'bt.rozetka.com.ua': RozetkaItem}

    @staticmethod
    async def create_item(item_url: str, current_price: str) -> object:
        """
        Create an Item object.

        :param item_url: Url to an item.
        :type item_url: str
        :param current_price: Current price of an item.
        :type current_price:str
        :return: Item object.
        :rtype: object
        """
        item = await ItemFactory._create_item(item_url, current_price)
        return item

    @staticmethod
    async def _create_item(item_url, current_price):
        """
        Creates an object of a certain type depending on a domain.

        :param item_url: Url to an item.
        :type item_url: str
        :param current_price: Current price of an item.
        :type current_price:str
        :return: Item object.
        :rtype: object
        """
        domain = urlparse(item_url).netloc
        class_for_item = ItemFactory._sources.get(domain)
        if class_for_item:
            item = class_for_item(item_url=item_url, current_price=current_price)
        else:
            item = DefaultItem(item_url=item_url, current_price=current_price)
        await item.init_attr()
        return item


async def run_all():
    tasks = (run_one(item_url, current_price) for item_url, current_price in PAGES)
    await asyncio.gather(*tasks)


async def run_one(item_url, current_price):
    item = await ItemFactory.create_item(item_url=item_url, current_price=current_price)
    print(f'\n{item_url}\n----------------------------------------------------\n')
    print(f'Attrs - {item.html_attrs}')
    print(f'Price - {item.current_price}')


if __name__ == '__main__':
    start_time = datetime.now()
    asyncio.run(run_all())
    print(datetime.now() - start_time)
