import asyncio
import json
from datetime import datetime
from urllib.parse import urlparse

from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user

from app.forms import CreateItemForm
from app.models import Item, ItemPriceHistory
from app import app, db, bcrypt
from app.parser import ItemFactory


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
async def home():
    user_id = current_user.get_id()
    items = Item.query.filter_by(user_id=user_id)
    return render_template('home.html', items=items)


@app.route('/item/add', methods=['GET', 'POST'])
async def add_item():
    form = CreateItemForm()
    if request.method == 'POST':
        if form.validate_on_submit() and current_user.is_authenticated:
            domain = urlparse(form.item_url.data).netloc
            if domain == 'elmir.ua':
                flash('Failed to add an item for tracking.', 'danger')
                return redirect(url_for('add_item'))
            new_item = await create_item(user_id=current_user.get_id(),
                                         item_url=form.item_url.data,
                                         current_price=form.current_price.data,
                                         title=form.title.data,
                                         min_desired_price=form.min_desired_price.data,
                                         max_allowable_price=form.max_allowable_price.data)
            if not new_item:
                flash('Failed to add an item for tracking.', 'danger')
                return redirect(url_for('add_item'))
            flash('Item added successfully.', 'success')
            return redirect(url_for('home'))
    return render_template('item_form.html', form=form)


async def create_item(item_url, current_price, user_id, title, min_desired_price=None, max_allowable_price=None):
    item_from_parser = await ItemFactory.create_item(item_url=item_url, current_price=current_price)
    if not item_from_parser:
        return None
    item_to_db = Item(user_id=user_id, title=title, item_url=item_from_parser.item_url,
                      current_price=item_from_parser.current_price,
                      html_attrs=json.dumps(item_from_parser.html_attrs),
                      min_desired_price=min_desired_price,
                      max_allowable_price=max_allowable_price)
    try:
        db.session.add(item_to_db)
        db.session.commit()
    except:
        return None
    return item_to_db


async def update_current_price(product):
    try:
        html_attrs = json.loads(product.html_attrs)
        item_url = product.item_url
        current_price = await ItemFactory.get_current_price(item_url=item_url, html_attr=html_attrs)
        product.current_price = current_price
        db.session.commit()
        update_price_history(product=product)
    except:
        return None
    return product


def update_price_history(product):
    # print(product)
    new_history = ItemPriceHistory(item_id=product.id, price=product.current_price)
    try:
        db.session.add(new_history)
        db.session.commit()
    except:
        print('Не получилось обновить историю')


@app.route('/update')
async def update_prices():
    # start_time = datetime.now()
    try:
        tasks = (update_current_price(product) for product in Item.query.filter_by(user_id=current_user.get_id()))
        await asyncio.gather(*tasks)
        flash('A product prices are updated successfully', 'success')
    except:
        flash('Failed to update a product prices', 'danger')
    # print(datetime.now() - start_time)
    return redirect(url_for('home'))



