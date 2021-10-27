from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class FolderForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=80)])
    submit = SubmitField('Confirm')
