from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Optional, NumberRange, URL, ValidationError


def is_numeric_field(form, field):
    """
    Checks if field data is numeric.
    """
    try:
        float(field.data)
    except:
        raise ValidationError('Field must be a number.')


def less_than_current_price_check(form, field):
    """
    Checks that field data less than a current price field.
    """
    if field.data >= float(form.current_price.data):
        raise ValidationError('Field must be less than current price.')


def more_than_current_price_check(form, field):
    """
    Checks that field data bigger than a current price field.
    """
    if field.data <= float(form.current_price.data):
        raise ValidationError('Field can\'t be less than current price.')


class CreateItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    item_url = StringField('Url', validators=[DataRequired(), URL(message='You need to specify a valid URL')])
    current_price = StringField('Current price', validators=[DataRequired(), is_numeric_field])
    min_desired_price = DecimalField('Minimum desired price', validators=[Optional(), is_numeric_field,
                                                                          NumberRange(min=0),
                                                                          less_than_current_price_check])
    max_allowable_price = DecimalField('Maximum allowable price', validators=[Optional(), is_numeric_field,
                                                                              more_than_current_price_check])
    submit = SubmitField('Confirm')


class EditItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    current_price = StringField('Current price', render_kw={'readonly': True})
    min_desired_price = DecimalField('Minimum desired price', validators=[Optional(), NumberRange(min=0),
                                                                          less_than_current_price_check])
    max_allowable_price = DecimalField('Maximum allowable price', validators=[Optional(),
                                                                              more_than_current_price_check])
    submit = SubmitField('Confirm')
