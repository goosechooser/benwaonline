from flask_wtf import FlaskForm
from wtforms import SelectField

def file_to_choices(fname):
    with open(fname, 'r') as f:
        lines = [line.rstrip().title() for line in f]
    return [(line, line) for line in lines]

NOUNS = file_to_choices('setup/nouns.txt')
ADJECTIVES = file_to_choices('setup/adjectives.txt')

def format_benwa(length=10):
    return [('Benwa', 'Benwa') for i in range(length)]

class RegistrationForm(FlaskForm):
    adjective = SelectField(u'Adjectives')
    benwa = SelectField(u'Benwa')
    noun = SelectField(u'Nouns')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.adjective.choices = ADJECTIVES
        self.benwa.choices = format_benwa()
        self.noun.choices = NOUNS
