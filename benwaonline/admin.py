from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from benwaonline.models import *

def setup_adminviews(admin, db):
    admin.add_view(ModelView(Post, db.session))
    admin.add_view(ModelView(Image, db.session))
    admin.add_view(ModelView(Tag, db.session))