from web.database import db

class Items(db.Model):
    __tablename__ = 'items'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    search = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, search, user_id):
        self.search = search
        self.user_id = user_id

    def __repr__(self):
        return '<id {}>'.format(self.id)