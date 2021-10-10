from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import asyncio

from parse_script import PAGES, ItemFactory

from config import Configuration

from forms.user import RegistrationForm, LoginForm

app = Flask(__name__)
app.config.from_object(Configuration)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


@app.route('/')
@app.route('/home')
async def hello_world():
    items = []
    new_item = await ItemFactory.create_item(PAGES[0][0], PAGES[0][1])
    items.append(new_item)
    return render_template('home.html', items=items)


@app.route('/sing-in')
def sign_in():
    form = LoginForm()
    return render_template('sign_in.html', title='Login', form=form)


@app.route('/sign-up')
def sign_up():
    form = RegistrationForm()
    return render_template('sign_up.html', title='Register', form=form)


async def generate_items():
    items = []
    tasks = (items.append(await ItemFactory.create_item(item_url, current_price)) for item_url, current_price in PAGES)

    await asyncio.gather(*tasks)
    return items

from models.item import Item
from models.user import User


