from flask import render_template, url_for, redirect, request, flash
from flask_login import login_user, current_user, logout_user

from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, RequestResetPasswordForm
from app.models import User
from app import app, db, bcrypt
from app.notification import Notification


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
            flash('Login Unsuccessful. Please check email and password', 'danger')
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


def send_password_reset_email(user: User):
    token = user.get_reset_token()
    reset_link = f"{url_for('request_for_reset_password', _external=True)}/{token}"
    Notification.send_password_reset_instructions(reset_link=reset_link, email_address=user.email)


@app.route("/reset_password", methods=['GET', 'POST'])
def request_for_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetPasswordForm()

    # If request method POST
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_password_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('sign_in'))

    # If request method GET
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not User:
        flash('That link for reset password is an invalid or expired', 'warning')
        return redirect(url_for('request_for_reset_password'))
    form = ResetPasswordForm()

    # If request method POST
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated', 'success')
        return redirect(url_for('sign_in'))

    # If request method GET
    return render_template('reset_password.html', title='Reset Password', form=form)




