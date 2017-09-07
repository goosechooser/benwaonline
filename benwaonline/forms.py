from wtforms import Form, StringField, validators

class GuestbookEntry(Form):
    name = StringField('Name', [validators.Length(min=4, max=40)])
    comment = StringField('Comment', [validators.Length(min=2, max=255)])
