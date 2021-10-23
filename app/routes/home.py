from flask import render_template
from flask_login import current_user

from app.models import Item
from app import app


@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
async def home():
    user_id = current_user.get_id()
    items = Item.query.filter_by(user_id=user_id).order_by(Item.id.desc())
    return render_template('home.html', items=items)
