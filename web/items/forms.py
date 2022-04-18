from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.validators import DataRequired, Length


class ItemsForm(FlaskForm):
    search = TextField('Search', validators=[DataRequired(),
                                         Length(min=1, max=254)])
