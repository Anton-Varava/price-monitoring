from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CreateItemForm(FlaskForm):
    item_url = StringField('Url',
                           validators=[DataRequired()])
    current_price = StringField('Current price',
                                validators=[DataRequired()])
    submit = SubmitField('Confirm')
