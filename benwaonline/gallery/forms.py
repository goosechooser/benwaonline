from wtforms import Form, StringField, SubmitField, validators

class CommentForm(Form):
    content = StringField('Comment', [validators.Length(min=1, max=255)])
    submit = SubmitField('Share your precious benwa meories', [validators.Required()])
