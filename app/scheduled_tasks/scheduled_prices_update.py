import asyncio

from  datetime import datetime

from app import app, scheduler

from app.models import Item
from app.routes.product import _update_current_price


async def total_items_update():
    """
    Updates a current price of all Items in db.
    Calls '_update_current_price' for every Item.
    """
    all_items = Item.query.all()
    tasks = (_update_current_price(item) for item in all_items)
    await asyncio.gather(*tasks)


@scheduler.scheduled_job('interval', minutes=10)
def scheduled_prices_update_task():
    start_time = datetime.now()
    asyncio.run(total_items_update())
    time_spent_updating = datetime.now() - start_time
    print(f'Updated at {datetime.now().strftime("%Y-%m-%d %H:%M")}. Task is completed by {time_spent_updating}')
