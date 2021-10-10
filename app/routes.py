from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, current_user, logout_user, login_required

from app.forms.item import CreateItemForm
from app.forms.user import LoginForm, RegistrationForm
from app.models.user import User
from app.models.item import Item
from app import app, db, bcrypt


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
async def home():
    items = Item.query.all()
    form = CreateItemForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash('Item added successfully.')
            return redirect(url_for('home'))
    return render_template('home.html', items=items, form=form)


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
