import asyncio
import json
from datetime import datetime
from urllib.parse import urlparse

from flask import render_template, url_for, redirect, request, flash, abort
from flask_login import current_user

from app.forms import FolderForm
from app.models import Item, ItemsFolder, User
from app import app, db, bcrypt
from app.parser import ItemFactory
from app.notification import Notification


@app.route('/folder/add', methods=['GET', 'POST'])
def create_folder():
    form = FolderForm()

    if request.method == 'POST':
        if form.validate_on_submit() and current_user.is_authenticated:
            new_folder = ItemsFolder(title=form.title.data, user_id=current_user.get_id())

            db.session.add(new_folder)
            db.session.commit()

            flash('Folder created successfully', 'success')
            return redirect(url_for('home'))
    return render_template('folder_form.html', form=form, legend='Create folder')


@app.route('/folder/<int:folder_id>/edit', methods=['GET', 'POST'])
def edit_folder(folder_id):
    form = FolderForm()

    folder = ItemsFolder.query.get_or_404(folder_id)

    # Check if is owner.
    if current_user.get_id() != str(folder.user_id):  # current_user.get_id() return string
        abort(403)

    if request.method == 'POST':
        if form.validate_on_submit() and current_user.is_authenticated:
            folder.title = form.title.data
            db.session.commit()

            flash('Folder edited successfully', 'success')
            return redirect(url_for('home'))
    return render_template('folder_form.html', form=form, legend='Edit folder')


@app.route('/folder/<int:folder_id>/delete')
def delete_folder(folder_id):
    folder = ItemsFolder.query.get_or_404(folder_id)

    # Check if is owner.
    if current_user.get_id() != str(folder.user_id):  # current_user.get_id() return string
        abort(403)

    db.session.delete(folder)
    db.session.commit()

    flash('Folder deleted successfully', 'success')
    return redirect(url_for('home'))


@app.route('/folder/<int:folder_id>')
def folder_items(folder_id):
    folder = ItemsFolder.query.get_or_404(folder_id)

    # Check if is owner.
    if current_user.get_id() != str(folder.user_id):  # current_user.get_id() return string
        abort(403)

    folder_items = Item.query.filter_by(folder_id=folder.id).all()

    return render_template('folder_items.html', items=folder_items, folder=folder)
