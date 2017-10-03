import os
import os.path
import sys
from flask import current_app
from datetime import datetime
from benwaonline.models import user_datastore, Tag, SelectOption
from benwaonline.database import db

from run import app
import add_benwas

def file_to_list(fname):
    with open(fname, 'r') as f:
        return [line.rstrip() for line in f]

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

# Options should be a list of tuples - (category, value)
def init_selectoptions(session, adjectives, nouns):
    created = datetime.utcnow()
    option = SelectOption(category='benwa', value='Benwa', created=created)
    session.add(option)

    for a in adjectives:
        session.add(SelectOption(category='adjective', value=a.title(), created=created))

    for n in nouns:
        session.add(SelectOption(category='noun', value=n.title(), created=created))

    session.commit()

if __name__ == '__main__':
    img_path = None
    if len(sys.argv) > 1:
        img_path = os.path.abspath(sys.argv[1])
        preview_path = os.path.abspath(sys.argv[2])
    try:
        adjectives = file_to_list('setup\\adjectives.txt')
        nouns = file_to_list('setup\\nouns.txt')
    except Exception as e:
        print('ya blew it', e)

    with app.app_context():
        if not os.path.isfile(current_app.config['SQLALCHEMY_DATABASE_URI']):
            init_db()

            init_roles(db.session)
            init_tags(db.session)
            init_selectoptions(db.session, adjectives, nouns)

        if img_path:
            add_benwas.add_posts(img_path, preview_path)

        db.session.commit()
