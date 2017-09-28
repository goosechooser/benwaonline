from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, FieldList, Field, TextAreaField
from wtforms.widgets import TextInput
from wtforms.validators import Length

images = UploadSet('images', IMAGES)

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
    def __init__(self, label='', validators=None, remove_duplicates=True, **kwargs):
        super(BetterTagListField, self).__init__(label, validators, **kwargs)
        self.remove_duplicates = remove_duplicates

    def process_formdata(self, valuelist):
        super(BetterTagListField, self).process_formdata(valuelist)
        if self.remove_duplicates:
            self.data = list(self._remove_duplicates(self.data))

    @classmethod
    def _remove_duplicates(cls, seq):
        """Remove duplicates in a case insensitive, but case preserving manner"""
        d = {}
        for item in seq:
            if item.lower() not in d:
                d[item.lower()] = True
                yield item


class CommentForm(FlaskForm):
    content = TextAreaField('Comment',\
        render_kw={"rows": 5, "cols": 40, "placeholder": "write your comment here!!"},\
        validators=[Length(min=1, max=255)])

class PostForm(FlaskForm):
    image = FileField('image', validators=[
        FileRequired(),
        FileAllowed(images, 'Only benwa _pictures_ please')
    ])
    tags = BetterTagListField('Tags')
