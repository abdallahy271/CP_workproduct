import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from web.database import db, app
app.config.from_object(os.getenv('APP_SETTINGS'))
# BLUEPRINTS
from web.users.routes import users_blueprint
from web.items.routes import items_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(items_blueprint)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()