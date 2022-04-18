import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def create_app():
    # CONFIG
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(os.getenv('APP_SETTINGS'))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

app = create_app()
db = SQLAlchemy(app)
db.init_app(app)