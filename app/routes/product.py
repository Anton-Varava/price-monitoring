import asyncio
import json
from datetime import datetime
from urllib.parse import urlparse

from flask import render_template, url_for, redirect, request, flash, abort
from flask_login import current_user

from app.forms import CreateItemForm, EditItemForm, ItemReparseForm
from app.models import Item, ItemPriceHistory, User
from app import app, db, bcrypt
from app.parser import ItemFactory
from app.notification import Notification


@app.route('/item/add', methods=['GET', 'POST'])
async def add_item_for_tracking():
    """
    Adds a new item for price tracking. If success - adds a record in 'items_price_history'.
    """
    form = CreateItemForm()
    if request.method == 'POST':
        if form.validate_on_submit() and current_user.is_authenticated:
            # Fix after adding parsing rules for elmir
            domain = urlparse(form.item_url.data).netloc
            if domain == 'elmir.ua':
                flash('Failed to add an item for tracking.', 'danger')
                return redirect(url_for('add_item_for_tracking'))
            new_item = await init_item(user_id=current_user.get_id(),
                                       item_url=form.item_url.data,
                                       current_price=form.current_price.data,
                                       title=form.title.data,
                                       min_desired_price=form.min_desired_price.data,
                                       max_allowable_price=form.max_allowable_price.data,
                                       folder_id=form.folder.data.id if form.folder.data else None)
            if not new_item:
                flash('Failed to add an item for tracking.', 'danger')
                return redirect(url_for('add_item_for_tracking'))

            flash('Item added successfully.', 'success')
            update_item_price_history(new_item)
            return redirect(url_for('home'))

    # If request method == GET
    return render_template('item_form.html', form=form, legend='Add item'), 200


async def init_item(item_url: str, current_price: str, user_id: int, title: str,
                    min_desired_price=None, max_allowable_price=None, folder_id=None):
    """
    Gets an item info from parser and adds an Item object to db.
    """
    item_from_parser = await ItemFactory.create_item(item_url=item_url, current_price=current_price)
    if not item_from_parser:
        return None

    item_to_db = Item(user_id=user_id, title=title, item_url=item_from_parser.item_url,
                      current_price=item_from_parser.current_price,
                      html_attrs=json.dumps(item_from_parser.html_attrs),
                      min_desired_price=min_desired_price,
                      max_allowable_price=max_allowable_price,
                      folder_id=folder_id)
    try:
        db.session.add(item_to_db)
        db.session.commit()
    except:
        return None
    return item_to_db


@app.route('/<int:item_id>/reparse', methods=['POST', 'GET'])
async def reparse_item(item_id: int):
    form = ItemReparseForm()
    item = Item.query.get_or_404(item_id)
    user = User.query.filter_by(id=item.user_id).first()
    price_before_update = item.current_price

    if form.validate_on_submit() and current_user.is_authenticated:
        item_from_parser = await ItemFactory.create_item(item_url=item.item_url, current_price=form.current_price.data)
        if not item_from_parser:
            flash('Failed to add an item for tracking.', 'danger')
            return redirect(url_for('home'))

        item.current_price = item_from_parser.current_price
        item.html_attrs = json.dumps(item_from_parser.html_attrs)

        db.session.commit()

        if item.current_price != price_before_update:
            notify_logic(user=user, item=item)

        flash(f'Item reparsed successfully', 'success')
        return redirect(url_for('home'))
    return render_template('item_reparse.html', form=form, item=item, legend='Reparse Item')


@app.route('/<int:item_id>/update')
async def update_current_price(item_id: int):
    """
    Updates current price of an item using html_attrs. Flash success message with time.

    :param item_id: An Item ID
    :type item_id: int
    """
    item_to_update_price = Item.query.get_or_404(item_id, description='An Item is not exists.')

    time_before_update = datetime.now()
    updated_item = await _update_current_price(item_to_update_price)

    if not updated_item:
        flash('Failed to update a product price', 'danger')
        return redirect(url_for('home'))

    total_time_takes_to_update = round((datetime.now() - time_before_update).total_seconds(), 2)
    flash(f'A product price is updated successfully ({total_time_takes_to_update} seconds)', 'success')
    return redirect(url_for('home'))


async def _update_current_price(item_to_update_price: Item):
    """
    Takes an Item object and updates an item current price.
    Calls method 'notify_logic' to make a decision on alerting a User.
    Calls method 'update_item_price_history' for updating price history.

    :param item_to_update_price: An Item object.
    :return: An Item object with an updated current price.
    """
    html_attrs = json.loads(item_to_update_price.html_attrs)
    item_url = item_to_update_price.item_url
    price_before_update = item_to_update_price.current_price
    user = User.query.filter_by(id=item_to_update_price.user_id).first()
    try:
        current_price = await ItemFactory.get_current_price(item_url=item_url, html_attr=html_attrs)
    except:
        return None
    item_to_update_price.current_price = current_price
    db.session.commit()

    update_item_price_history(product=item_to_update_price)

    # Calls notify_logic if price is changed
    if item_to_update_price.current_price != price_before_update:
        notify_logic(user=user, item=item_to_update_price)

    return item_to_update_price


def notify_logic(user: User, item: Item):
    """
    Sends an email with info on price changes.

    :param user: An User object.
    :param item: An Item object.
    """
    # If a price has dropped to a desired level
    if item.min_desired_price and item.current_price <= item.min_desired_price:
        message = f'The price of {item.title} has reached the desired mark.'

    # If a price has exceeded an allowed maximum
    elif item.max_allowable_price and item.current_price >= item.max_allowable_price:
        message = f'The price of {item.title}the acceptable maximum. You will no longer receive a price alert.'

    # If no price restrictions are specified then
    else:
        message = f'The price of {item.title} has changed.'

    Notification.notify_to_email(message=message, email_address=user.email)


def update_item_price_history(product: Item):
    """
    Adds a record to 'update_item_price_history' on db.
    :param product: An Item object.
    """
    new_history = ItemPriceHistory(item_id=product.id, price=product.current_price)
    db.session.add(new_history)
    db.session.commit()


@app.route('/update_all')
async def update_all_user_item_prices():
    """ Updates all user item prices. """

    user_items = Item.query.filter_by(user_id=current_user.get_id())
    if not user_items.count():
        flash('No items to update', 'danger')
        return redirect(url_for('home'))

    start_time = datetime.now()
    tasks = (_update_current_price(item) for item in user_items)
    try:
        await asyncio.gather(*tasks)
    except:
        flash('Failed to update a product prices', 'danger')

    finish_time = round((datetime.now() - start_time).total_seconds(), 2)
    flash(f'A product prices are updated successfully ({finish_time} seconds)', 'success')
    return redirect(url_for('home'))


@app.route('/<int:item_id>/delete')
async def delete_item(item_id: int):
    """
    Deletes an Item object.

    :param item_id: ID of an Item.
    :type item_id: int
    """
    item = Item.query.get_or_404(item_id)

    # Check if is owner.
    if current_user.get_id() != str(item.user_id):  # current_user.get_id() return string
        abort(403)

    db.session.delete(item)
    db.session.commit()

    flash('Item deleted successfully.', 'success')
    return redirect(url_for('home'))


@app.route('/<int:item_id>/edit', methods=['GET', 'POST'])
async def edit_item(item_id: int):
    """
    Route for editing Item. 'title', 'min_desired_price', 'max_allowable_price' can be edited.
    :param item_id: ID of an Item.
    """
    item = Item.query.get_or_404(item_id)

    # Check if is owner.
    if current_user.get_id() != str(item.user_id):  # current_user.get_id() return string
        abort(403)

    form = EditItemForm()
    if request.method == 'GET':
        form.title.data = item.title
        form.current_price.data = item.current_price
        form.min_desired_price.data = item.min_desired_price
        form.max_allowable_price.data = item.max_allowable_price
        form.folder.data = item.folder

    elif request.method == 'POST':
        if form.validate_on_submit():
            item.title = form.title.data
            item.min_desired_price = form.min_desired_price.data
            item.max_allowable_price = form.max_allowable_price.data
            item.folder_id = form.folder.data.id if form.folder.data else None

            db.session.commit()

            flash('Item updated successfully.', 'success')
            return redirect(url_for('home'))
    return render_template('item_edit_form.html', title='Update item', form=form, legend='Update item')


@app.route('/<int:item_id>/chart', methods=['GET'])
def item_price_chart(item_id: int):
    """
    Route for viewing the schedule of changes in the price of an item.
    :param item_id: ID of an Item object
    """
    item = Item.query.get_or_404(item_id)

    # Check if is owner.
    if current_user.get_id() != str(item.user_id):  # current_user.get_id() return string
        abort(403)

    item_history = ItemPriceHistory.query.filter_by(item_id=item_id).order_by('date_updated')
    history = [(item_record.date_updated.strftime('%Y-%m-%d %H:%M'), item_record.price) for item_record in item_history]

    labels = [row[0] for row in history]
    values = [row[1] for row in history]
    return render_template('price_chart.html', history=history, prices=values, dates=labels, item_title=item.title)




