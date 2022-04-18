# IMPORTS
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask import render_template
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

import os
from .database import db, app

#
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "users.login"

from web.models.items import Items
from web.models.user import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

# BLUEPRINTS
from web.users.routes import users_blueprint
from web.items.routes import items_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(items_blueprint)


def setup_database(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

# ROUTES
@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    """Render homepage"""

    #filter_by(user_id=current_user.id)
    all_user_items = Items.query.filter_by(user_id=current_user.id)
    return render_template('home.html', items=all_user_items)


# ERROR PAGES
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def page_forbidden(e):
    return render_template('403.html'), 403


@app.errorhandler(410)
def page_gone(e):
    return render_template('410.html'), 410

if __name__ == '__main__':
    if not os.path.isfile('web.db'):
        setup_database(app)
    app.run()
