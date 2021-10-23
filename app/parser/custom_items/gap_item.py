from .default_item import Item


class GapItem(Item):
    """
    Item object from gap.com store.
    """

    async def _get_html_attrs(self) -> dict:
        """
        Return a dictionary with a html attributes for tracking a current price.

        :return: Dictionary with a html attributes. None if it failed to get a attributes.
        :rtype: dict
        """
        return {'class': ['pdp-pricing__selected']}
