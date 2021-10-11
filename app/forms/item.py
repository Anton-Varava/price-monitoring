from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, DecimalField
from wtforms.validators import DataRequired, NumberRange, Optional


class CreateItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    item_url = StringField('Url',
                           validators=[DataRequired()])
    current_price = StringField('Current price',
                                validators=[DataRequired()])
    min_desired_price = DecimalField('Minimum desired price', validators=[Optional()])
    max_allowable_price = DecimalField('Maximum allowable price', validators=[Optional()])
    submit = SubmitField('Confirm')


