from bs4 import BeautifulSoup
import re
from requests_html import HTMLSession, AsyncHTMLSession


HEADER = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
        "AppleWebKit/537.36 (KHTML, like Gecko)" +
        "Chrome/83.0.4103.116" +
        "Safari/537.36",
}

PAGES = [('https://eobuv.com.ua/p/chelsi-blundstone-1911-tabacco', '4 597,00'),
         ('https://elmir.ua/ua/video_cards/graphics_card_gigabyte_pci-e_geforce_rtx2060_6gb_ddr6_gv-n2060oc-6gd.html',
          '22 999'),
         ('https://comfy.ua/ua/stiral-naja-mashina-aeg-l9wba61bc.html', '48 199'),
         # ('https://bt.rozetka.com.ua/ua/polaris_pwh_imr_0850_v/p237266605/', '6 099'),
         ('https://allo.ua/ru/products/mobile/samsung-galaxy-z-fold3-12-256-green-sm-f926bzgdsek.html', '54 999'),
         ('https://www.ebay.com/itm/371246540991?_trkparms=pageci%3Ab603444d-2425-11ec-924c-5edf3e9060ad%7Cparentrq%3A4550c11217c0a45b4a61af5dfffc33dc%7Ciid%3A1', '24.99'),
         # ('https://www.citrus.ua/uhod-za-volosami/fen-dyson-supersonic-hd03-fuksiya-689591.html', '14 499'),
         # ('https://eldorado.ua/noutbuk-lenovo-legion5-15-imh05-h-phantom-black-81-y600-m0-ra-/p71310322/', '35 999'),
         ('https://www.foxtrot.com.ua/ru/shop/pylesosy_samsung_vc07m2110sr-uk.html', '2 799'),
         ('https://www.moyo.ua/sistemnyy_blok_2e_moyo_complex_gaming_2e-2152_/477942.html', '21 314'),
         ('https://avic.ua/pocketbook-616-basic-lux2-obsidian-black-pb616-h-cis-item', '3239')
         ]

POSSIBLE_TAGS = ('span', 'meta', 'p', 'div')


def make_text_without_whitespaces(text: str) -> str:
    return ''.join(text.split())


def make_price_number_from_str(price_string: str) -> float:
    """
    Gets item price from string and converts to float.

    :param price_string: A string with a price contained inside
    :type price_string: str
    :return: an item price
    :rtype: float
    """
    try:
        price_int = float(price_string)
    except ValueError:
        price_string = re.search(r'\d+(\s|\\xa0)?\d+((\.|,)\d{1,2})?', price_string).group().replace(',', '.').replace(u'\xa0', '').replace(' ', '')
        price_int = float(price_string)
    return price_int


def get_page_soup(page_url: str):
    """
    Gets response from web-page and makes soup.

    :param page_url: Link to an item.
    :type page_url: str
    :return: BeautifulSoup object of web-page.
    :rtype: object
    """
    session = HTMLSession()
    response = session.get(page_url, headers=HEADER)
    if response.status_code != 200:
        # render html by js
        response.html.render(sleep=1.5)
    soup = BeautifulSoup(response.html.html, 'html.parser')
    return soup


def get_itemprop(page_soup: object, item_price: str) -> object:
    """
    Check that web-page has html-element with itemprop='price' and a price in a 'content' attribute
    or in a text of an element.

    :param page_soup: BeautifulSoup object of a web-page.
    :type page_soup: object
    :param item_price: Current item price
    :type item_price: str
    :return: Return html-element for tracking price. None if html-element for tracking couldn't be found. (bs4.element.Tag)
    :rtype: object
    """
    for tag in POSSIBLE_TAGS:
        result = page_soup.find(tag, itemprop="price")
        if result:
            if all([result, make_text_without_whitespaces(result.text) == make_text_without_whitespaces(item_price)]):
                return result
            elif all([result, make_text_without_whitespaces(result.get('content')) == make_text_without_whitespaces(item_price)]):
                return result
    return None


def get_html_element_with_price(page_soup: object, current_price: str) -> object:
    """
    Get html-element from web-page for tracking price.

    :param page_soup: BeautifulSoup object of a web-page.
    :type page_soup: object
    :param current_price: Current item price
    :type current_price: str
    :return: Return html-element for tracking price. None if html-element for tracking couldn't be found. (bs4.element.Tag)
    :rtype: object
    """
    current_price = make_text_without_whitespaces(current_price)

    itemprop_result = get_itemprop(page_soup, current_price)
    if itemprop_result:
        return itemprop_result

    result = None
    for possible_tag in POSSIBLE_TAGS:
        for tag in page.select(f'{possible_tag}[class*="price"]'):
            if current_price in make_text_without_whitespaces(tag.text):
                t = tag
                if not result or len(t) < len(result):
                    result = t
    return result


def get_price_from_html_element(soup: object, element: object) -> float:
    """
    Get price of an item from a specified html-element.

    :param soup: BeautifulSoup object of a web-page.
    :type soup: object
    :param element: Html-element with price indication (bs4.element.Tag).
    :type element: object
    :return: Price of an item.
    :rtype: float
    """
    attrs = element.attrs
    current_html_element = soup.find(attrs=attrs)
    attrs_current_html_element = current_html_element.attrs
    if attrs_current_html_element.get('content'):
        return make_price_number_from_str(attrs_current_html_element.get('content'))
    return make_price_number_from_str(current_html_element.text)


if __name__ == '__main__':
    for url, price in PAGES:
        page = get_page_soup(url)
        print(f'\n{url}\n----------------------------------------------------\n')
        html_element = get_html_element_with_price(page, price)
        print(html_element, '\n')
        if html_element:
            print(f'Price - {get_price_from_html_element(page, html_element)}')


