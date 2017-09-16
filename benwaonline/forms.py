from wtforms import Form, StringField, validators

class Comment(Form):
    name = StringField('Name', [validators.Length(min=1, max=40)])
    content = StringField('Comment', [validators.Length(min=1, max=255)])
