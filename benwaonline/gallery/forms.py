from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length

class CommentForm(FlaskForm):
    content = StringField('Comment', validators=[Length(min=1, max=255)])

class PostForm(FlaskForm):
    pass

