import os
from os.path import split, join, abspath
import sys
from datetime import datetime
from benwaonline import models
from benwaonline.database import db
from run import app

def get_or_create_tag(session, tagname):
    instance = models.Tag.query.filter_by(name=tagname).first()
    if instance:
        return instance, False
    else:
        created = datetime.utcnow()
        instance = models.Tag(name=tagname, created=created)
        session.add(instance)

    return instance, True

def add_post(img_path, preview_path, tags=['benwa']):
    created = datetime.utcnow()
    with app.app_context():
        img = models.Image(filepath=img_path, created=created)
        db.session.add(img)

        preview = models.Preview(filepath=preview_path, created=created)
        db.session.add(preview)

        tag_models = [get_or_create_tag(db.session, tag)[0] for tag in tags]

        _, title = split(img_path)
        post = models.Post(title=title, created=datetime.utcnow(), preview=preview, image=img, tags=tag_models)
        db.session.add(post)

        db.session.commit()

def add_posts(img_path, preview_path, tags=['benwa']):
    files_ = [f for f in os.listdir(img_path)]
    for f in files_:
        img = '/'.join([img_path, f])
        preview = join(preview_path, f)
        add_post(img, preview, tags)

if __name__ == '__main__':
    img_path = abspath(sys.argv[1])
    preview_path = abspath(sys.argv[2])

    add_posts(img_path, preview_path)
