import asyncio
import json

from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, current_user, logout_user, login_required

from app.forms.item import CreateItemForm
from app.forms.user import LoginForm, RegistrationForm
from app.models.user import User
from app.models.item import Item
from app import app, db, bcrypt
from app.parser import ItemFactory


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('sign_in.html', title='Login', form=form)


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('home'))
    return render_template('sign_up.html', title='Register', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


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
