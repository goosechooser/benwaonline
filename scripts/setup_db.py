import os
import os.path
import sys
from flask import current_app
from datetime import datetime
from benwaonline.models import user_datastore, Tag
from benwaonline.database import db

from run import app
from scripts.add_benwas import add_posts

def file_to_list(fname):
    with open(fname, 'r') as f:
        return [line.rstrip().title() for line in f]

def init_db():
    import benwaonline.models
    db.create_all()

def init_roles(session):
    user_datastore.create_role(name='admin', description='a 10 on the benwa chart')
    user_datastore.create_role(name='member', description='like a 1 on the benwa chart')

    session.commit()

def init_tags(session):
    created = datetime.utcnow()
    tag = Tag(name='benwa', created=created)
    session.add(tag)

    session.commit()

def setup(img_path=None, preview_path=None):
    with app.app_context():
        if not os.path.isfile(current_app.config['SQLALCHEMY_DATABASE_URI']):
            init_db()

            init_roles(db.session)
            init_tags(db.session)

        if img_path:
            add_posts(img_path, preview_path)

        db.session.commit()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        img_path = os.path.abspath(sys.argv[1])
        preview_path = os.path.abspath(sys.argv[2])

    setup()

