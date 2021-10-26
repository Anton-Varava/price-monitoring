from urllib.parse import urlparse

from .custom_items import RozetkaItem, UsaAutoOnlineItem, DefaultItem, GapItem


class ItemFactory:
    """
    Factory for creating an Item objects.
    """
    _sources = {'bt.rozetka.com.ua': RozetkaItem,
                'rozetka.com.ua': RozetkaItem,
                'usa-auto-online.com': UsaAutoOnlineItem,
                'www.gap.com': GapItem}

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
        if not item.html_attrs:
            return None
        return item

    @staticmethod
    async def get_current_price(item_url, html_attr):
        domain = urlparse(item_url).netloc
        class_for_item = ItemFactory._sources.get(domain)
        if class_for_item:
            current_price = await class_for_item.get_current_price_by_html_attrs(item_url=item_url,
                                                                                 html_attrs=html_attr)
        else:
            current_price = await DefaultItem.get_current_price_by_html_attrs(item_url=item_url, html_attrs=html_attr)
        return current_price
