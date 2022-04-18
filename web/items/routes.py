# web/items/routes.py

# IMPORTS
from flask import render_template, Blueprint, request, redirect, url_for, flash, Markup
from flask_login import current_user, login_required
from web.database import db
from web.models.items import Items
from web.models.user import User
from .forms import ItemsForm
from .searcher import run_search

# CONFIG
items_blueprint = Blueprint('items', __name__, template_folder='templates')


# ROUTES
@items_blueprint.route('/all_items', methods=['GET', 'POST'])
@login_required
def all_items():
    """Render homepage"""
    all_user_items = Items.query.filter_by(user_id=current_user.id)
    return render_template('all_items.html', items=all_user_items)


@items_blueprint.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemsForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                search_result = run_search(form.search.data)
                print(search_result)
                new_item = Items(form.search.data,
                                 user_id=current_user.id)
                db.session.add(new_item)
                db.session.commit()
                message = Markup(
                    "<strong>Congrats!</strong> Item search complete!")
                flash(message, 'success')
                # return redirect(url_for('home'))
                return render_template('add_item.html', form=form, search_result=search_result)
            except:
                db.session.rollback()
                message = Markup(
                    "<strong>Oh snap!</strong> Unable to search for item.")
                flash(message, 'danger')
    return render_template('add_item.html', form=form, search_result=None)



@items_blueprint.route('/delete_item/<items_id>')
@login_required
def delete_item(items_id):
    item = Items.query.filter_by(id=items_id).first_or_404()

    if not item.user_id == current_user.id:
        message = Markup(
            "<strong>Error!</strong> Incorrect permissions to delete this item.")
        flash(message, 'danger')
        return redirect(url_for('home'))

    db.session.delete(item)
    db.session.commit()
    flash('{} was deleted.'.format(item.search), 'success')
    return redirect(url_for('items.all_items'))
