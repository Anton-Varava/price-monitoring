from bs4 import BeautifulSoup
from requests_html import HTMLSession, AsyncHTMLSession


HEADER = {
    "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" +
        "AppleWebKit/537.36 (KHTML, like Gecko)" +
        "Chrome/83.0.4103.116" +
        "Safari/537.36",
}

PAGES = [('https://eobuv.com.ua/p/chelsi-blundstone-1911-tabacco', '4 597,00'),
         ('https://elmir.ua/ua/video_cards/graphics_card_gigabyte_pci-e_geforce_rtx2060_6gb_ddr6_gv-n2060oc-6gd.html',
          '22 999'),
         ('https://comfy.ua/ua/stiral-naja-mashina-aeg-l9wba61bc.html', '48 199'),
         ('https://bt.rozetka.com.ua/ua/polaris_pwh_imr_0850_v/p237266605/', '6 099'),
         ('https://allo.ua/ru/products/mobile/samsung-galaxy-z-fold3-12-256-green-sm-f926bzgdsek.html', '54 999'),
         ('https://www.ebay.com/itm/371246540991?_trkparms=pageci%3Ab603444d-2425-11ec-924c-5edf3e9060ad%7Cparentrq%3A4550c11217c0a45b4a61af5dfffc33dc%7Ciid%3A1', '24.99'),
         ('https://www.citrus.ua/uhod-za-volosami/fen-dyson-supersonic-hd03-fuksiya-689591.html', '14 499'),
         ('https://eldorado.ua/noutbuk-lenovo-legion5-15-imh05-h-phantom-black-81-y600-m0-ra-/p71310322/', '35 999'),
         ('https://www.foxtrot.com.ua/ru/shop/pylesosy_samsung_vc07m2110sr-uk.html', '2 799'),
         ('https://www.moyo.ua/sistemnyy_blok_2e_moyo_complex_gaming_2e-2152_/477942.html', '21 314'),
         ('https://avic.ua/smartfon-apple-iphone-13-pro-max-128gb-silver-item', '50 999')
         ]
comfy = PAGES[2]
POSSIBLE_TAGS = ('p', 'span', 'div', 'meta')


def make_text_without_whitespaces(text):
    return ''.join(text.split())


def get_page_soup(url: str):
    session = HTMLSession()
    r = session.get(url, headers=HEADER)
    if r.status_code != 200:
        r.html.render(sleep=1.5)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    return soup


def get_itemprop(page_soup, item_price):
    for tag in POSSIBLE_TAGS:
        result = page_soup.find(tag, itemprop="price")
        if result:
            if all([result, make_text_without_whitespaces(result.text) == make_text_without_whitespaces(item_price)]):
                return result
            elif all([result, make_text_without_whitespaces(result.get('content')) == make_text_without_whitespaces(item_price)]):
                return result
    return None


def parse_page(page, price):
    price = make_text_without_whitespaces(price)

    itemprop_result = get_itemprop(page, price)
    if itemprop_result:
        return itemprop_result

    result = None
    for possible_tag in POSSIBLE_TAGS:
        for tag in page.select(f'{possible_tag}[class*="price"]'):
            if price in make_text_without_whitespaces(tag.text):
                t = tag
                if not result or len(t) < len(result):
                    result = t
    return result


if __name__ == '__main__':
    for url, price in PAGES:
        page = get_page_soup(url)
        print(f'\n{url}\n----------------------------------------------------\n')
        result = parse_page(page, price)
        if result:
            print(result.attrs)
        print(result)
    #


