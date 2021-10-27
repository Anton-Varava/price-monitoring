from flask import render_template
from flask_login import current_user

from app.models import Item, ItemsFolder
from app import app


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
async def home():
    user_id = current_user.get_id()
    no_folder_items = Item.query.filter_by(user_id=user_id, folder_id=None).order_by(Item.id.desc())
    folders = ItemsFolder.query.filter_by(user_id=user_id).order_by(ItemsFolder.title.desc())
    return render_template('home.html', no_folder_items=no_folder_items, folders=folders)
