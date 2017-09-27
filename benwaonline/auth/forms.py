from wtforms import Form, SelectField, SubmitField, validators

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