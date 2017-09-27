from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField

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

class RegistrationForm(FlaskForm):
    adj = SelectField(u'Adjectives', choices=adjectives)
    benwa = SelectField(label='', choices=benwas)
    pos = SelectField(label='', choices=positions)