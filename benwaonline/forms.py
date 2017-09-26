from wtforms import Form, StringField, SelectField, SubmitField, validators

class Comment(Form):
    content = StringField('Comment', [validators.Length(min=1, max=255)])

# Turn these 3 lists into file(s)
# Script takes file with list produces list of tuples with proper capital etc
adjectives = [
    ('beautiful', 'beautiful'),
    ('fantastic', 'fantastic')
]

benwas = [
    ('benwa', 'benwa'),
    ('benwa', 'benwa'),
    ('benwa', 'benwa'),
    ('benwa', 'benwa'),
    ('benwa', 'benwa'),
    ('benwa', 'benwa')
]

positions = [
    ('liker', 'liker'),
    ('fan', 'fan'),
    ('lover', 'lover')
]

class RegistrationForm(Form):
    adj = SelectField(u'Adjectives', choices=adjectives)
    benwa = SelectField(label='', choices=benwas)
    pos = SelectField(label='', choices=positions)
    submit = SubmitField('Submit', [validators.Required()])
