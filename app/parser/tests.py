import asyncio
from datetime import datetime, timedelta
from factory import ItemFactory

PAGES = [
    # ('https://www.copart.com/ru/lot/43708811/salvage-2019-kia-optima-lx-ga-atlanta-west', '3 250'),
    ('https://usa-auto-online.com/en/auction/35094441-RAM-PROMASTER', '550'),
    ('https://eobuv.com.ua/p/chelsi-blundstone-1911-tabacco', '4 597,00'),
    # ('https://elmir.ua/ua/video_cards/graphics_card_gigabyte_pci-e_geforce_rtx2060_6gb_ddr6_gv-n2060oc-6gd.html',
    #  '22 999'),
    ('https://comfy.ua/ua/stiral-naja-mashina-aeg-l9wba61bc.html', '48 199'),
    ('https://bt.rozetka.com.ua/ua/polaris_pwh_imr_0850_v/p237266605/', '7399'),
    ('https://allo.ua/ru/products/mobile/samsung-galaxy-z-fold3-12-256-green-sm-f926bzgdsek.html', '54 999'),
    ('https://www.ebay.com/itm/371246540991?_trkparms=pageci%3Ab603444d-2425-11ec-924c-5edf3e9060ad%7Cparentrq%3A4550c11217c0a45b4a61af5dfffc33dc%7Ciid%3A1',
    '24.99'),
    # # ('https://www.citrus.ua/uhod-za-volosami/fen-dyson-supersonic-hd03-fuksiya-689591.html', '14 499'),
    # # ('https://eldorado.ua/noutbuk-lenovo-legion5-15-imh05-h-phantom-black-81-y600-m0-ra-/p71310322/', '35 999'),
    ('https://www.foxtrot.com.ua/ru/shop/pylesosy_samsung_vc07m2110sr-uk.html', '2 799'),
    ('https://www.moyo.ua/sistemnyy_blok_2e_moyo_complex_gaming_2e-2152_/477942.html', '21 314'),
    ('https://avic.ua/pocketbook-616-basic-lux2-obsidian-black-pb616-h-cis-item', '3239'),

]

async def run_all():
    tasks = (run_one(item_url, current_price) for item_url, current_price in PAGES)
    await asyncio.gather(*tasks)

created_objects = []


async def run_one(item_url, current_price):
    item = await ItemFactory.create_item(item_url=item_url, current_price=current_price)
    created_objects.append(item)
    # print(f'\n{item_url}\n----------------------------------------------------\n')
    # print(f'Price default - {item.current_price}')
    # print(f'Attrs - {item.html_attrs}')
    # print(f'Price by attr - {await ItemFactory.get_current_price(item_url, item.html_attrs)}')


async def get_updated_price(item_url, html_attrs):
    print(f'{item_url} - {await ItemFactory.get_current_price(item_url, html_attrs)}')


async def update_all(items):
    tasks = (get_updated_price(item.item_url, item.html_attrs) for item in items)
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    start_time = datetime.now()
    asyncio.run(run_all())
    print('Created in ', datetime.now() - start_time, '\n')
    start_time = datetime.now()
    asyncio.run(update_all(created_objects))
    print('Updated in ', datetime.now() - start_time)
