import json

from flask import render_template, url_for, redirect, request, flash
from flask_login import current_user

from app.forms import CreateItemForm
from app.models import Item
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
            new_item = await create_item(user_id=current_user.get_id(),
                                         item_url=form.item_url.data,
                                         current_price=form.current_price.data,
                                         title=form.title.data,
                                         min_desired_price=form.min_desired_price.data,
                                         max_allowable_price=form.max_allowable_price.data)
            if not new_item:
                flash('Error', 'danger')
                return redirect(url_for('add_item'))
            flash('Item added successfully.', 'success')
            return redirect(url_for('home'))
    return render_template('item_form.html', form=form)


async def create_item(item_url, current_price, user_id, title, min_desired_price=None, max_allowable_price=None):
    new_item = await ItemFactory.create_item(item_url=item_url, current_price=current_price)
    item_to_db = Item(user_id=user_id, title=title, item_url=new_item.item_url,
                      current_price=new_item.current_price,
                      html_attrs=json.dumps(new_item.html_attrs),
                      min_desired_price=min_desired_price,
                      max_allowable_price=max_allowable_price)
    try:
        db.session.add(item_to_db)
        db.session.commit()
    except:
        return None
    return item_to_db
