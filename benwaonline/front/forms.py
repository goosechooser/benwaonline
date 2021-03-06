from flask_wtf import FlaskForm
from wtforms import Field
from wtforms.validators import Optional
from wtforms.widgets import TextInput

# Taken from WTFields documentation
class TagListField(Field):
    widget = TextInput()

    def _value(self):
        if self.data:
            return u', '.join(self.data)
        else:
            return u''

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = [x.strip() for x in valuelist[0].split(',')]
        else:
            self.data = []

# Taken from WTFields documentation
class BetterTagListField(TagListField):
    def __init__(self, label='', validators=None, filters=(), remove_duplicates=True, **kwargs):
        super(BetterTagListField, self).__init__(label, validators, filters, **kwargs)
        self.remove_duplicates = remove_duplicates

    def process_formdata(self, valuelist):
        super(BetterTagListField, self).process_formdata(valuelist)
        if self.remove_duplicates:
            self.data = list(self._remove_duplicates(self.data))

    @classmethod
    def _remove_duplicates(cls, seq):
        """Remove duplicates in a case insensitive, but case preserving manner"""
        d = {'benwa': True}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item

class SearchForm(FlaskForm):
    tags = BetterTagListField('Tags',
                        validators=[Optional()],
                        filters = [lambda x: x or None]
                        )
