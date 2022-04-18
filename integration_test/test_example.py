from flask import Blueprint
from unittest import TestCase
import os, sys
sys.path.insert(1, os.getcwd())
from web.database import create_app

app = create_app()
bp = Blueprint('chefs', __name__)

@bp.route('/')
def index():
    return 'Hello, World!'

class TestEndpoint(TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()

    def test_index(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 200)



