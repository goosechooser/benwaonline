from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from benwaonline.models import SelectOption

def format_benwa(length=10):
    q = SelectOption.query.get(1)
    return [(q.value, q.value) for i in range(length)]

def enabled_category(category):
    return SelectOption.query.filter_by(category=category).all

class RegistrationForm(FlaskForm):
    adjective = QuerySelectField(u'Adjectives', get_label='value')
    benwa = SelectField(u'Benwa')
    noun = QuerySelectField(u'Nouns', get_label='value')

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        self.adjective.query_factory = enabled_category('adjective')
        self.benwa.choices = format_benwa()
        self.noun.query_factory = enabled_category('noun')
